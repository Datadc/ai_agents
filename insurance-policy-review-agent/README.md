# Insurance Policy Audit Agent

This folder contains a starter implementation for an open-source LLM-based insurance policy review agent.

## Objectives
- Parse uploaded policy text or policy number lookup results
- Identify critical terms and future claim risks
- Flag discrepancies and missing coverage items
- Generate structured audit output

## Tech stack
- Python 3.11+
- Core dependencies: `pdfplumber`, `pytesseract`, `Pillow`, `fastapi`, `uvicorn`
- Optional: `llama-cpp-python` (for LLM-powered summaries)

## Installation

### Basic Setup
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Optional: Enable LLM Features
To use LLM-powered policy summaries:
```bash
pip install llama-cpp-python
# Download a GGML model and place it at ./models/ggml-model-q4_0.bin
```

## Quick Start
```bash
# Basic analysis (works without LLM)
python agent.py --policy-file policy.pdf

# With LLM summary (requires model file)
python agent.py --policy-file policy.pdf --model ./models/ggml-model-q4_0.bin

# Save report to file
python agent.py --policy-file policy.pdf --out audit_report.json
```

## Features
- Modular architecture under `agent_impl/`:
  - `io.py` (PDF/text loading + OCR fallback)
  - `parser.py` (formal field extraction)
  - `analysis.py` (risk, discrepancy, missing coverage rules)
  - `llm.py` (optional LLM summary with llama-cpp-python)
  - `agent.py` (CLI entrypoint)
- PDF ingestion: parses text via `pdfplumber`; uses `pytesseract` where needed
- Policy text analysis:
  - detects exposures (e.g., pre-existing exclusions, short claims windows)
  - validates key dates and values
  - flags missing core policy attributes
- Output is JSON object with structured keys

## Usage

### Command-line Arguments
```bash
python agent.py --policy-file <path> [--model <path>] [--out <file>]
```

| Option | Description |
|--------|-------------|
| `--policy-file` | Path to text or PDF policy document (required) |
| `--model` | Path to GGML model file (optional, for LLM summary) |
| `--out` | Output file for JSON report (optional) |

### Examples
```bash
# Analyze a text policy
python agent.py --policy-file policy.txt

# Analyze PDF with detailed report
python agent.py --policy-file policy.pdf --out report.json

# Full analysis with LLM summary
python agent.py --policy-file policy.pdf --model ./models/model.bin --out report.json
```

### Output Structure
The agent generates a JSON report with:
- **policy_summary**: Extracted fields (policy number, issuer, dates, exclusions, etc.)
- **critical_findings**: High-severity risks and coverage gaps
- **discrepancies**: Missing or malformed policy fields
- **missing_criteria**: Recommended clauses not found in policy
- **llm_summary**: AI-powered analysis (if LLM available)

## Error Handling

The agent gracefully handles missing dependencies:
- **Without `llama-cpp-python`**: Core analysis still works, LLM summary shows informative message
- **Missing model file**: Agent continues with rule-based analysis
- **Invalid PDF/text**: Detailed error messages guide troubleshooting

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Test Coverage
- Policy text loading from TXT and PDF
- Field extraction via regex patterns
- Risk analysis and discrepancy detection
- Missing criteria identification
- Complete report generation

**Current Status**: All 5 tests passing ✓

### Test Example
```bash
$ pytest tests/test_agent.py -v
tests/test_agent.py::test_load_policy_text_from_string PASSED
tests/test_agent.py::test_extract_fields_from_text PASSED
tests/test_agent.py::test_match_findings_and_discrepancies PASSED
tests/test_agent.py::test_missing_criteria PASSED
tests/test_agent.py::test_generate_report_contains_all_sections PASSED
```

## code Structure

```
agent_impl/
├── __init__.py       # Module exports
├── io.py             # PDF/text loading with OCR fallback
├── parser.py         # Regex-based field extraction
├── analysis.py       # Risk, discrepancy, missing criteria analysis
└── llm.py            # Optional LLM integration with error handling

tests/
├── test_agent.py     # Unit tests for all components
```

### Key Modules

**io.py**
- `load_policy_text(path)`: Handles TXT and PDF files
- `extract_text_from_pdf()`: pdfplumber + pytesseract fallback for scanned documents

**parser.py**
- `extract_fields(text)`: Regex patterns for policy number, dates, exclusions, etc.

**analysis.py**
- `risk_analysis()`: Identifies exposures (low sum insured, pre-existing exclusions, claim windows)
- `find_discrepancies()`: Flags missing required fields
- `find_missing_criteria()`: Recommends important policy clauses
- `generate_report()`: Orchestrates analysis and returns JSON

**llm.py**
- `run_llm_assessment()`: Optional AI summary (graceful if unavailable)
- Handles ImportError and runtime exceptions safely

## Known Limitations

- **Regex-based parsing**: Works well for standard formatted policies; may miss unconventional layouts
- **OCR quality**: Scanned PDF recognition depends on image quality and tesseract setup
- **Language**: Currently English-only (policy text expectations)
- **Jurisdiction**: Rules are generic; jurisdiction-specific validations not implemented

## Future Enhancements

- [ ] FastAPI wrapper for REST endpoints
- [ ] Database integration for policy number lookups
- [ ] Jurisdiction-specific rules (India insurance regulations, etc.)
- [ ] Advanced NLP for better field extraction
- [ ] Support for policy amendment documents
- [ ] Configurable `--skip-llm` flag for deterministic mode
- [ ] HTML/web UI dashboard
- [ ] Batch processing for multiple policies

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'pdfplumber'`
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: PyTesseract not recognizing Tesseract
**Solution**: Install Tesseract OCR system

macOS:
```bash
brew install tesseract
```

Linux (Ubuntu):
```bash
sudo apt-get install tesseract-ocr
```

Windows: Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Issue: LLM model not found
**Solution**: Place GGML model file in the correct location
```bash
mkdir -p models/
# Download model and place at ./models/ggml-model-q4_0.bin
```

Or skip LLM features - the agent works fine without it (graceful degradation).

### Issue: Tests failing
**Ensure pytest is installed**:
```bash
pip install pytest
cd insurance-policy-review-agent  # if running from parent directory
pytest tests/ -v
```

## Development

### Running Tests with Coverage
```bash
# Install coverage tool
pip install pytest-cov

# Generate coverage report
pytest --cov=agent_impl tests/
```

### Code Quality
```bash
# Lint with flake8
pip install flake8
flake8 agent_impl/ agent.py

# Type checking with mypy
pip install mypy
mypy agent_impl/ agent.py
```

## Contributing

Contributions are welcome! Areas for improvement:
- Enhanced regex patterns for policy field extraction
- Additional policy risk rules
- Support for more languages
- Performance optimizations for large PDFs
- Better error messages and logging

## License

[Specify license here]

## Contact

For questions or issues, please [open an issue on GitHub](https://github.com/Datadc/ai_agents).
