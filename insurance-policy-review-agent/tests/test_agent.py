import json
from pathlib import Path

from agent_impl.parser import extract_fields
from agent_impl.analysis import (
    risk_analysis,
    find_discrepancies,
    find_missing_criteria,
    generate_report,
)
from agent_impl.io import load_policy_text


def test_load_policy_text_from_string(tmp_path):
    # Write sample file + use loader
    file = tmp_path / "policy.txt"
    content = "Policy Number: POLICY-123\nPolicy type: Health insurance"
    file.write_text(content, encoding="utf-8")
    loaded = load_policy_text(file)
    assert "Policy Number" in loaded


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


def test_generate_report_contains_all_sections():
    sample = """Policy Number: POLICY-123\nPolicy type: Health insurance\nIssuer: AlphaCare Ltd.\nSum insured: $150000\nEffective date: 2025-01-01\nExpiry date: 2025-12-31\nExclusions: pre-existing conditions not declared\nClaims process: submit documents within 30 days."""
    report = generate_report(sample, model_path="./models/ggml-model-q4_0.bin")
    assert "policy_summary" in report
    assert "critical_findings" in report
    assert "discrepancies" in report
    assert "missing_criteria" in report
