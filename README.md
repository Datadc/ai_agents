# Insurance Policy Audit Agent

This folder contains a starter implementation for an open-source LLM-based insurance policy review agent.

## Objectives
- Parse uploaded policy text or policy number lookup results
- Identify critical terms and future claim risks
- Flag discrepancies and missing coverage items
- Generate structured audit output

## Tech stack
- Python 3.11+
- llama-cpp-python (local open-source model)
- Optional: LangChain, FASTAPI, OCR pipeline

## Quick start
1. `pip install -r requirements.txt`
2. Place the model at `./models/ggml-model-q4_0.bin` (or supported file)
3. `python agent.py --policy-file example-policy.txt`

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
- Command-line:
  - `python agent.py --policy-file path/to/policy.pdf --model ./models/ggml-model-q4_0.bin --out report.json`
- `--policy-file` accepts TXT or PDF
- `--out` saves structured JSON report

## Testing
1. `pip install pytest`
2. `pytest -q`

## Optional enhancements
- Add FastAPI wrapper for HTTP endpoint
- Add policy-number database/API lookup
- Add rules for jurisdiction-specific requirements
- Add configurable `--skip-llm` for deterministic rule-only response
