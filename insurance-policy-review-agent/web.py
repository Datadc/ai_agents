from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

from agent_impl.analysis import generate_report

app = FastAPI(
    title="Insurance Policy Review Agent",
    description="AI-powered insurance policy analysis and risk assessment",
    version="1.0.0"
)

MODEL_DEFAULT = "./models/ggml-model-q4_0.bin"

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "insurance-policy-review-agent"}

@app.post("/analyze")
async def analyze_policy(
    file: UploadFile = File(...),
    model_path: str = MODEL_DEFAULT
) -> Dict[str, Any]:
    """
    Analyze an uploaded insurance policy file (PDF or TXT).

    Returns a comprehensive analysis including:
    - Policy summary with extracted fields
    - Critical risk findings
    - Discrepancies and missing criteria
    - LLM-generated summary (if available)
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.txt']:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload PDF or TXT files."
        )

    # Save uploaded file to temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Process the file
        policy_path = Path(temp_file_path)
        report = generate_report(str(policy_path), model_path=model_path)

        return JSONResponse(
            content={
                "status": "success",
                "filename": file.filename,
                "analysis": report
            },
            status_code=200
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing policy file: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass  # File may already be deleted or inaccessible

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API information"""
    return {
        "message": "Insurance Policy Review Agent API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)