import re


def _first_match(text: str, patterns: list) -> str:
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


def _normalize_date(text: str) -> str:
    date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", text)
    if date_match:
        return date_match.group(0).strip()
    date_match = re.search(r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s*\d{4}\b", text, re.IGNORECASE)
    if date_match:
        return date_match.group(0).strip()
    date_match = re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text)
    return date_match.group(0).strip() if date_match else ""


def _extract_section(text: str, heading: str) -> str:
    stop_markers = [
        r"\nPART [A-Z]",
        r"\nName of Your Plan",
        r"\nName of your Rider",
        r"\nPolicy Number",
        r"\nSum Assured on Death",
        r"\nPremium Instalment",
        r"\nPayment frequency",
        r"\nNext premium due date",
        r"\nPolicy Term",
        r"\nDate of Maturity",
        r"\nDate of commencement",
        r"\nAuthorised Signatory",
        r"\nBase Policy No",
    ]
    boundary = r"|".join(stop_markers)
    pattern = re.compile(rf"{re.escape(heading)}[:\s]*(.*?)(?=(?:{boundary})|$)", re.IGNORECASE | re.DOTALL)
    m = pattern.search(text)
    if not m:
        return ""
    return m.group(1).strip()


def _split_clauses(text: str) -> list:
    if not text:
        return []
    cleaned = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"\n(?=[a-z]\)|\d+\.|[A-Z][a-z]+\.|;|- )", cleaned)
    items = [p.strip() for p in parts if len(p.strip()) > 20]
    return items


def extract_fields(text: str) -> dict:
    raw_text = text.strip()
    out = {
        "policy_number": _first_match(raw_text, [
            r"Policy\s*Number\s*[:\-]\s*([A-Za-z0-9\-]+)",
            r"Base\s*Policy\s*No\s*[:\-]\s*([A-Za-z0-9\-]+)",
        ]),
        "policy_type": _first_match(raw_text, [
            r"Policy\s*type\s*[:\-]\s*([A-Za-z0-9 &\-/()]+)",
        ]),
        "plan_name": _first_match(raw_text, [
            r"Name\s*of\s*Your\s*Plan\s*[:\-]\s*([A-Za-z0-9 &\-/()]+?)(?=\s+(?:You have an option|within \d+ days|Policy Number|Mobile Number|Email ID|Person insured|Name of Plan variant|$))"
        ]),
        "plan_variant": _first_match(raw_text, [
            r"Name\s*of\s*Plan\s*variant\s*[:\-]\s*([A-Za-z0-9 &\-/()]+)"
        ]),
        "issuer": _first_match(raw_text, [
            r"(ICICI Prudential Life Insurance Company Limited)",
            r"(ICICI Prudential Life Insurance Co(?:mpany)? Ltd\.?)",
            r"Issuer\s*[:\-]\s*([A-Za-z0-9 &\-.]+)",
        ]),
        "broker_name": _first_match(raw_text, [
            r"Name\s*[:\-]\s*([A-Za-z0-9 &\-.]+Brokers?\s+Private\s+Limited)",
        ]),
        "sum_insured": _first_match(raw_text, [
            r"Sum\s*Assured\s*on\s*Death\s*[:\-]\s*[`₹$]?\s*([0-9,]+)",
            r"Sum\s*insured\s*[:\-]\s*[`₹$]?\s*([0-9,]+)",
        ]),
        "premium_first_year": _first_match(raw_text, [
            r"Premium\s*Instalment\s*in\s*first\s*policy\s*year\s*\(in [`₹$]*\)\s*[:\-]\s*([0-9,]+)",
        ]),
        "premium_second_year": _first_match(raw_text, [
            r"Premium\s*Instalment\s*from\s*second\s*policy\s*year\s*onwards\s*\(in [`₹$]*\)\s*[:\-]\s*([0-9,]+)",
        ]),
        "payment_frequency": _first_match(raw_text, [
            r"Payment\s*frequency\s*[:\-]\s*([A-Za-z0-9 ]+)"
        ]),
        "next_premium_due": _normalize_date(_first_match(raw_text, [
            r"Next\s*premium\s*due\s*date\s*[:\-]\s*([A-Za-z0-9 ,./-]+)"
        ])),
        "policy_term": _first_match(raw_text, [
            r"Policy\s*Term\s*[:\-]\s*([A-Za-z0-9 ]+)"
        ]),
        "effective_date": _normalize_date(_first_match(raw_text, [
            r"Date\s*of\s*commencement\s*of\s*risk\s*[:\-]\s*([A-Za-z0-9 ,./-]+)",
            r"Effective\s*date\s*[:\-]\s*([A-Za-z0-9 ,./-]+)",
        ])),
        "expiry_date": _normalize_date(_first_match(raw_text, [
            r"Date\s*of\s*Maturity\s*[:\-]\s*([A-Za-z0-9 ,./-]+)",
            r"Expiry\s*date\s*[:\-]\s*([A-Za-z0-9 ,./-]+)",
        ])),
        "exclusions": [],
        "claims_process": _first_match(raw_text, [
            r"Claims\s*process\s*[:\-]\s*(.+?)(?:\n|$)",
        ]),
        "riders": [],
        "raw_text": raw_text,
    }

    if not out["policy_type"] and out["plan_name"]:
        out["policy_type"] = out["plan_name"]
    if not out["issuer"]:
        out["issuer"] = out["broker_name"]

    exclusions_text = _extract_section(raw_text, "Exclusions")
    if exclusions_text:
        out["exclusions"] = _split_clauses(exclusions_text)

    rider_names = []
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    for line in lines:
        rider_match = re.match(r"Name\s*of\s*your\s*Rider\s*[:\-]\s*(.+)", line, re.IGNORECASE)
        if rider_match:
            rider_names.append(rider_match.group(1).strip())
        else:
            rider_match = re.match(r"Rider\s*[:\-]\s*(.+)", line, re.IGNORECASE)
            if rider_match:
                rider_text = rider_match.group(1).strip()
                if len(rider_text) > 10 and "UIN" not in rider_text:
                    rider_names.append(rider_text)

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

    for keyword, canonical in known_riders.items():
        if keyword in raw_text.lower() and canonical not in rider_names:
            rider_names.append(canonical)

    out["riders"] = [r for r in rider_names if r]
    return out
