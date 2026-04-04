try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False


def run_llm_assessment(policy_text: str, model_path: str):
    if not LLAMA_AVAILABLE:
        return "LLM not available: llama-cpp-python not installed."
    
    try:
        llama = Llama(model_path=model_path)
        prompt = (
            "You are an insurance policy audit expert.\n"
            "Summarize key fields, top 3 risks, discrepancies, and missing criteria in JSON.\n"
            "Policy text:\n" + policy_text + "\n"
        )
        response = llama(prompt=prompt, max_tokens=800, temperature=0.1)
        return response["choices"][0]["text"].strip()
    except Exception as e:
        return f"LLM error: {str(e)}"
