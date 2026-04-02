import re


def extract_fields(text: str) -> dict:
    out = {
        "policy_number": "",
        "policy_type": "",
        "issuer": "",
        "sum_insured": "",
        "effective_date": "",
        "expiry_date": "",
        "exclusions": [],
        "claims_process": "",
        "raw_text": text.strip(),
    }

    patterns = {
        "policy_number": r"Policy\s*Number[:\s]*([A-Za-z0-9\-]+)",
        "policy_type": r"Policy\s*type[:\s]*([A-Za-z ]+)",
        "issuer": r"Issuer[:\s]*([A-Za-z0-9 &.]+)",
        "sum_insured": r"Sum\s*insured[:\s]*\$?([0-9,]+)",
        "effective_date": r"Effective\s*date[:\s]*([0-9]{4}-[0-9]{2}-[0-9]{2})",
        "expiry_date": r"Expiry\s*date[:\s]*([0-9]{4}-[0-9]{2}-[0-9]{2})",
        "claims_process": r"Claims\s*process[:\s]*(.+?)(?:\n|$)",
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            out[key] = m.group(1).strip()

    exclusions = re.search(r"Exclusions[:\s]*([\s\S]+?)(?:\n\n|$)", text, re.IGNORECASE)
    if exclusions:
        items = re.split(r",|;", exclusions.group(1))
        out["exclusions"] = [i.strip() for i in items if i.strip()]

    return out
