# Insurance Policy Audit Agent

This folder contains a comprehensive implementation for an open-source LLM-based insurance policy review agent with both CLI and web API interfaces.

## Objectives
- Parse uploaded policy text or policy number lookup results
- Identify critical terms and future claim risks
- Flag discrepancies and missing coverage items
- Generate structured audit output
- Provide web API for easy integration and user-friendly access

## Tech stack
- Python 3.11+
- Core dependencies: `pdfplumber`, `pytesseract`, `Pillow`, `fastapi`, `uvicorn`, `httpx`
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

### Command Line Usage
```bash
# Basic analysis (works without LLM)
python agent.py --policy-file policy.pdf

# With LLM summary (requires model file)
python agent.py --policy-file policy.pdf --model ./models/ggml-model-q4_0.bin

# Save report to file
python agent.py --policy-file policy.pdf --out audit_report.json
```

### Web API Usage
```bash
# Start the web server
python web.py

# Server runs at http://localhost:8000
# API documentation available at http://localhost:8000/docs

# Upload and analyze a policy via API
curl -X POST "http://localhost:8000/analyze" -F "file=@policy.pdf"

# Check service health
curl http://localhost:8000/health
```

### Demo
Run the included demo script to see both CLI and web API in action:
```bash
# From the project root directory
./demo.sh
```

## Features
- **Dual Interface**: Both command-line and web API access
- Modular architecture under `agent_impl/`:
  - `io.py` (PDF/text loading + OCR fallback)
  - `parser.py` (formal field extraction)
  - `analysis.py` (risk, discrepancy, missing coverage rules)
  - `llm.py` (optional LLM summary with llama-cpp-python)
  - `agent.py` (CLI entrypoint)
  - `web.py` (FastAPI web application)
- PDF ingestion: parses text via `pdfplumber`; uses `pytesseract` where needed
- Policy text analysis:
  - detects exposures (e.g., pre-existing exclusions, short claims windows)
  - validates key dates and values
  - flags missing core policy attributes
- Web API with automatic documentation and file upload support
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

### Web API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and links |
| `GET` | `/health` | Service health check |
| `POST` | `/analyze` | Upload and analyze policy file |

**File Upload**: POST to `/analyze` with `file` parameter containing PDF or TXT file.

### Examples
```bash
# Analyze a text policy (CLI)
python agent.py --policy-file policy.txt

# Analyze PDF with detailed report (CLI)
python agent.py --policy-file policy.pdf --out report.json

# Full analysis with LLM summary (CLI)
python agent.py --policy-file policy.pdf --model ./models/model.bin --out report.json

# Web API usage
curl -X POST "http://localhost:8000/analyze" -F "file=@policy.pdf"
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
- Policy text loading from TXT and PDF (including OCR)
- Field extraction via regex patterns
- Risk analysis and discrepancy detection
- Missing criteria identification
- Complete report generation
- Web API endpoints and error handling
- File upload validation

**Current Status**: All 22 tests passing ✓ (94% coverage)

### Test Example
```bash
$ pytest tests/test_agent.py -v
tests/test_agent.py::test_load_policy_text_from_string PASSED
tests/test_agent.py::test_load_policy_text_file_not_found PASSED
tests/test_agent.py::test_load_policy_text_from_pdf PASSED
tests/test_agent.py::test_load_policy_text_from_pdf_ocr PASSED
tests/test_agent.py::test_extract_fields_from_text PASSED
tests/test_agent.py::test_match_findings_and_discrepancies PASSED
tests/test_agent.py::test_missing_criteria PASSED
tests/test_agent.py::test_risk_analysis_low_sum_insured PASSED
tests/test_agent.py::test_risk_analysis_pre_existing_exclusion PASSED
tests/test_agent.py::test_risk_analysis_invalid_dates PASSED
tests/test_agent.py::test_risk_analysis_date_parsing_error PASSED
tests/test_agent.py::test_risk_analysis_no_findings PASSED
tests/test_agent.py::test_generate_report_contains_all_sections PASSED
tests/test_agent.py::test_agent_main PASSED
tests/test_agent.py::test_agent_main_with_out PASSED
tests/test_agent.py::test_health_check PASSED
tests/test_agent.py::test_root_endpoint PASSED
tests/test_agent.py::test_analyze_policy_txt PASSED
tests/test_agent.py::test_analyze_policy_pdf PASSED
tests/test_agent.py::test_analyze_policy_no_file PASSED
tests/test_agent.py::test_analyze_policy_invalid_file_type PASSED
tests/test_agent.py::test_analyze_policy_processing_error PASSED
```

## code Structure

```
agent_impl/
├── __init__.py       # Module exports
├── io.py             # PDF/text loading with OCR fallback
├── parser.py         # Regex-based field extraction
├── analysis.py       # Risk, discrepancy, missing criteria analysis
└── llm.py            # Optional LLM integration with error handling

├── agent.py          # CLI entrypoint
├── web.py            # FastAPI web application
└── tests/
    └── test_agent.py # Unit tests for all components
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

**web.py**
- FastAPI application with REST endpoints
- File upload handling with validation
- Error handling and temporary file management
- Automatic API documentation at `/docs`

## Web API Details

The web API provides RESTful endpoints for programmatic access:

### Endpoints

**GET /** 
Returns API information and navigation links.

**GET /health**
Health check endpoint for monitoring service status.

**POST /analyze**
Analyzes an uploaded insurance policy file.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: `file` parameter with PDF or TXT file

**Response:**
```json
{
  "status": "success",
  "filename": "policy.pdf",
  "analysis": {
    "policy_summary": {...},
    "critical_findings": [...],
    "discrepancies": [...],
    "missing_criteria": [...],
    "llm_summary": "..."
  }
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

### Running the Web Server
```bash
python web.py
```

Access the API documentation at `http://localhost:8000/docs`

## Known Limitations

- **Regex-based parsing**: Works well for standard formatted policies; may miss unconventional layouts
- **OCR quality**: Scanned PDF recognition depends on image quality and tesseract setup
- **Language**: Currently English-only (policy text expectations)
- **Jurisdiction**: Rules are generic; jurisdiction-specific validations not implemented

## Future Enhancements

- [x] ~~FastAPI wrapper for REST endpoints~~ ✓ **Implemented**
- [ ] Database integration for policy storage and history
- [ ] Jurisdiction-specific rules (India insurance regulations, etc.)
- [ ] Advanced NLP for better field extraction
- [ ] Support for policy amendment documents
- [ ] Configurable `--skip-llm` flag for deterministic mode
- [ ] HTML/web UI dashboard for visual analysis
- [ ] Batch processing for multiple policies
- [ ] User authentication and session management
- [ ] Policy comparison and diff analysis
- [ ] Export reports to PDF/HTML formats

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
pytest --cov=. tests/ --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=. tests/ --cov-report=html
# View report at htmlcov/index.html
```

### Code Quality
```bash
# Lint with flake8
pip install flake8
flake8 agent_impl/ agent.py web.py

# Type checking with mypy
pip install mypy
mypy agent_impl/ agent.py web.py
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
