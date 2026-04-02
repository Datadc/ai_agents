from llama_cpp import Llama


def run_llm_assessment(policy_text: str, model_path: str):
    llama = Llama(model_path=model_path)
    prompt = (
        "You are an insurance policy audit expert.\n"
        "Summarize key fields, top 3 risks, discrepancies, and missing criteria in JSON.\n"
        "Policy text:\n" + policy_text + "\n"
    )
    response = llama(prompt=prompt, max_tokens=800, temperature=0.1)
    return response["choices"][0]["text"].strip()
