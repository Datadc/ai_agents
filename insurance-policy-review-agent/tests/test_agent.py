import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

from agent_impl.parser import extract_fields
from agent_impl.analysis import (
    risk_analysis,
    find_discrepancies,
    find_missing_criteria,
    generate_report,
)
from agent_impl.io import load_policy_text
from agent_impl.llm import run_llm_assessment
import agent
from agent_impl.llm import run_llm_assessment


def test_load_policy_text_from_string(tmp_path):
    # Write sample file + use loader
    file = tmp_path / "policy.txt"
    content = "Policy Number: POLICY-123\nPolicy type: Health insurance"
    file.write_text(content, encoding="utf-8")
    loaded = load_policy_text(file)
    assert "Policy Number" in loaded


def test_load_policy_text_file_not_found(tmp_path):
    file = tmp_path / "nonexistent.txt"
    try:
        load_policy_text(file)
        assert False, "Should raise FileNotFoundError"
    except FileNotFoundError:
        pass


@patch('agent_impl.io.pdfplumber')
def test_load_policy_text_from_pdf(mock_pdfplumber, tmp_path):
    # Mock pdfplumber to return text
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Policy Number: PDF-123"
    mock_pdf.pages = [mock_page]
    mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
    
    file = tmp_path / "policy.pdf"
    file.write_text("", encoding="utf-8")  # Create empty file to simulate PDF
    loaded = load_policy_text(file)
    assert "Policy Number: PDF-123" in loaded


@patch('agent_impl.io.pdfplumber')
@patch('agent_impl.io.pytesseract')
def test_load_policy_text_from_pdf_ocr(mock_pytesseract, mock_pdfplumber, tmp_path):
    # Mock pdfplumber to return no text, then OCR
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None
    mock_page.to_image.return_value.original = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
    mock_pytesseract.image_to_string.return_value = "OCR Policy Text"
    
    file = tmp_path / "policy.pdf"
    file.write_text("", encoding="utf-8")
    loaded = load_policy_text(file)
    assert "OCR Policy Text" in loaded


def test_extract_fields_from_text():
    sample = """Policy Number: POLICY-123\nPolicy type: Health insurance\nIssuer: AlphaCare Ltd.\nSum insured: $150000\nEffective date: 2025-01-01\nExpiry date: 2025-12-31\nExclusions: pre-existing conditions not declared, dental treatment\nClaims process: submit documents within 30 days."""
    fields = extract_fields(sample)
    assert fields["policy_number"] == "POLICY-123"
    assert fields["policy_type"] == "Health insurance"
    assert fields["issuer"] == "AlphaCare Ltd."


def test_match_findings_and_discrepancies():
    sample = """Policy Number: POLICY-123\nPolicy type: Health insurance\nIssuer: AlphaCare Ltd.\nSum insured: $150000\nEffective date: 2025-01-01\nExpiry date: 2025-12-31\nExclusions: pre-existing conditions not declared\nClaims process: submit documents within 30 days."""
    fields = extract_fields(sample)
    findings = risk_analysis(fields)
    assert any(x["severity"] == "high" for x in findings)
    discrepancies = find_discrepancies(fields)
    assert len(discrepancies) == 0


def test_missing_criteria():
    sample = """Policy Number: POLICY-NOX\nPolicy type: Motor insurance\nIssuer: BetaInsure\nSum insured: $75000"""
    fields = extract_fields(sample)
    missing = find_missing_criteria(fields)
    assert any(x["criteria"] == "waiting period" for x in missing)


def test_risk_analysis_low_sum_insured():
    sample = """Policy Number: POLICY-123\nPolicy type: Health insurance\nIssuer: AlphaCare Ltd.\nSum insured: $30000\nEffective date: 2025-01-01\nExpiry date: 2025-12-31\nExclusions: dental treatment\nClaims process: submit documents within 60 days."""
    fields = extract_fields(sample)
    findings = risk_analysis(fields)
    assert any("Low sum insured" in x["risk"] for x in findings)


def test_risk_analysis_pre_existing_exclusion():
    sample = """Policy Number: POLICY-123\nPolicy type: Health insurance\nIssuer: AlphaCare Ltd.\nSum insured: $150000\nEffective date: 2025-01-01\nExpiry date: 2025-12-31\nExclusions: pre-existing conditions not declared\nClaims process: submit documents within 60 days."""
    fields = extract_fields(sample)
    findings = risk_analysis(fields)
    assert any("Undeclared pre-existing condition exclusion" in x["risk"] for x in findings)


def test_risk_analysis_invalid_dates():
    sample = """Policy Number: POLICY-123\nPolicy type: Health insurance\nIssuer: AlphaCare Ltd.\nSum insured: $150000\nEffective date: 2025-12-31\nExpiry date: 2025-01-01\nExclusions: dental treatment\nClaims process: submit documents within 60 days."""
    fields = extract_fields(sample)
    findings = risk_analysis(fields)
    assert any("Invalid policy dates" in x["risk"] for x in findings)


def test_risk_analysis_date_parsing_error():
    sample = """Policy Number: POLICY-123\nPolicy type: Health insurance\nIssuer: AlphaCare Ltd.\nSum insured: $150000\nEffective date: 2025-13-01\nExpiry date: 2025-01-01\nExclusions: dental treatment\nClaims process: submit documents within 60 days."""
    fields = extract_fields(sample)
    findings = risk_analysis(fields)
    assert any("Date parsing issue" in x["risk"] for x in findings)


def test_risk_analysis_no_findings():
    sample = """Policy Number: POLICY-123\nPolicy type: Health insurance\nIssuer: AlphaCare Ltd.\nSum insured: $200000\nEffective date: 2025-01-01\nExpiry date: 2025-12-31\nExclusions: dental treatment\nClaims process: submit documents within 60 days."""
    fields = extract_fields(sample)
    findings = risk_analysis(fields)
    assert len(findings) == 0


def test_generate_report_contains_all_sections():
    sample = """Policy Number: POLICY-123\nPolicy type: Health insurance\nIssuer: AlphaCare Ltd.\nSum insured: $150000\nEffective date: 2025-01-01\nExpiry date: 2025-12-31\nExclusions: pre-existing conditions not declared\nClaims process: submit documents within 30 days."""
    report = generate_report(sample, model_path="./models/ggml-model-q4_0.bin")
    assert "policy_summary" in report


@patch('agent.load_policy_text')
@patch('agent.generate_report')
@patch('builtins.print')
def test_agent_main(mock_print, mock_generate_report, mock_load_policy_text, tmp_path):
    mock_load_policy_text.return_value = "policy text"
    mock_generate_report.return_value = {"result": "ok"}
    
    # Mock sys.argv
    with patch('sys.argv', ['agent.py', '--policy-file', str(tmp_path / "policy.txt")]):
        agent.main()
    
    mock_load_policy_text.assert_called_once()
    mock_generate_report.assert_called_once_with("policy text", model_path="./models/ggml-model-q4_0.bin")
    # Check print calls
    assert mock_print.call_count >= 1


@patch('agent.load_policy_text')
@patch('agent.generate_report')
@patch('pathlib.Path.write_text')
@patch('builtins.print')
def test_agent_main_with_out(mock_print, mock_write_text, mock_generate_report, mock_load_policy_text, tmp_path):
    mock_load_policy_text.return_value = "policy text"
    mock_generate_report.return_value = {"result": "ok"}
    
    out_file = tmp_path / "out.json"
    # Mock sys.argv
    with patch('sys.argv', ['agent.py', '--policy-file', str(tmp_path / "policy.txt"), '--out', str(out_file)]):
        agent.main()
    
    mock_load_policy_text.assert_called_once()
    mock_generate_report.assert_called_once_with("policy text", model_path="./models/ggml-model-q4_0.bin")
    mock_write_text.assert_called_once()
    mock_print.assert_called()
