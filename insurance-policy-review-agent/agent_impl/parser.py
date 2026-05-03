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
        "riders": [],
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

    rider_sections = re.findall(
        r"(?:Rider|Riders|Add[- ]on|Optional benefit|Optional coverage)[:\s]*(.+?)(?:\n|$)",
        text,
        re.IGNORECASE,
    )
    known_riders = {
        "critical illness": "Critical Illness Rider",
        "accidental death": "Accidental Death Benefit Rider",
        "waiver of premium": "Waiver of Premium Rider",
        "hospital cash": "Hospital Cash Rider",
        "family floater": "Family Floater Rider",
        "disability income": "Disability Income Rider",
        "return of premium": "Return of Premium Rider",
        "top-up": "Top-up Rider",
        "spouse coverage": "Spouse Coverage Rider",
        "premium waiver": "Premium Waiver Rider",
    }

    riders = []
    for section in rider_sections:
        items = re.split(r",|;| and |\band\b", section, flags=re.IGNORECASE)
        for item in items:
            item_text = item.strip()
            if not item_text:
                continue
            for keyword, canonical in known_riders.items():
                if keyword in item_text.lower():
                    if canonical not in riders:
                        riders.append(canonical)
                    break
            else:
                if item_text not in riders:
                    riders.append(item_text)

    raw_lower = text.lower()
    for keyword, canonical in known_riders.items():
        if keyword in raw_lower and canonical not in riders:
            riders.append(canonical)

    out["riders"] = riders
    return out
