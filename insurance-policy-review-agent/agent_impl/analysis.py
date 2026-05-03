import re
from datetime import datetime
from pathlib import Path

from .parser import extract_fields
from .llm import run_llm_assessment


RIDER_KEYWORDS = {
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


def risk_analysis(fields: dict) -> list:
    findings = []

    if fields["sum_insured"]:
        value = int(fields["sum_insured"].replace(",", ""))
        if value < 50000:
            findings.append({"risk": "Low sum insured", "severity": "medium", "note": "May not cover high-cost claims."})

    raw_lower = fields["raw_text"].lower()
    if "pre-existing" in raw_lower and "not declared" in raw_lower:
        findings.append({"risk": "Undeclared pre-existing condition exclusion", "severity": "high", "note": "Can cause claim denial if linked to claim event."})

    if fields["claims_process"] and "30" in fields["claims_process"]:
        findings.append({"risk": "Short claims submission window", "severity": "high", "note": "30-day deadline increases risk of late filing."})

    if fields["effective_date"] and fields["expiry_date"]:
        try:
            eff = datetime.fromisoformat(fields["effective_date"])
            exp = datetime.fromisoformat(fields["expiry_date"])
            if exp <= eff:
                findings.append({"risk": "Invalid policy dates", "severity": "high", "note": "Expiry date is not after effective date."})
        except ValueError:
            findings.append({"risk": "Date parsing issue", "severity": "low", "note": "Policy dates could not be validated."})

    return findings


def analyze_riders(fields: dict) -> list:
    riders = fields.get("riders", [])
    findings = []
    raw_text = fields.get("raw_text", "").lower()

    if not riders:
        if "rider" in raw_text or "add-on" in raw_text or "optional benefit" in raw_text:
            findings.append({
                "rider": "Unclear rider wording",
                "status": "present",
                "severity": "medium",
                "note": "Rider-related language appears in policy text, but explicit rider names or structures are not clearly defined.",
            })
        else:
            findings.append({
                "rider": "No riders detected",
                "status": "absent",
                "severity": "info",
                "note": "No optional rider endorsements were explicitly identified. Confirm whether riders are documented separately or were omitted.",
            })
        return findings

    for rider in riders:
        normalized = rider.strip()
        severity = "low"
        note = "Rider is referenced in the policy text."

        if "critical illness" in normalized.lower():
            if not re.search(r"(critical illness|specified illnesses|covered illnesses|dread disease)", raw_text):
                severity = "medium"
                note = "Critical illness rider is present, but the covered illness list or payout triggers are not clearly defined."
        elif "accidental death" in normalized.lower():
            if not re.search(r"(accidental death|double indemnity|permanent disability|accidental death benefit)", raw_text):
                severity = "medium"
                note = "Accidental death benefit rider appears without clearly defined claim triggers or coverage limits."
        elif "waiver of premium" in normalized.lower() or "premium waiver" in normalized.lower():
            if not re.search(r"(waiting period|disability|total disablement|waiver of premium)", raw_text):
                severity = "medium"
                note = "Waiver of premium rider is referenced, but the qualifying disability or waiting period conditions are not clearly stated."
        elif "hospital cash" in normalized.lower():
            if not re.search(r"(daily benefit|per day|hospital cash|cash benefit)", raw_text):
                severity = "medium"
                note = "Hospital cash rider is mentioned without clear daily benefit amounts or limits."
        elif "family floater" in normalized.lower():
            if not re.search(r"(spouse|children|family member|family coverage)", raw_text):
                severity = "medium"
                note = "Family floater rider is referenced, but the covered family members are not clearly specified."
        elif "return of premium" in normalized.lower():
            if not re.search(r"(return of premium|refund of premium|no claim bonus|policy maturity)", raw_text):
                severity = "medium"
                note = "Return of premium rider is present, but the refund conditions and maturity terms are not clearly defined."
        elif "disability income" in normalized.lower():
            if not re.search(r"(income benefit|loss of income|monthly benefit|disability income)", raw_text):
                severity = "medium"
                note = "Disability income rider appears without clearly defined benefit amounts or payment terms."

        findings.append({
            "rider": normalized,
            "status": "present",
            "severity": severity,
            "note": note,
        })

    if len(riders) > 3:
        findings.append({
            "rider": "Multiple riders attached",
            "status": "present",
            "severity": "medium",
            "note": "More than three riders are attached to the policy. Review premium impact, overlap, and termination clauses carefully.",
        })

    if re.search(r"(rider premium|premium loading|additional premium|rider fee|extra premium)", raw_text):
        findings.append({
            "rider": "Rider premium loading",
            "status": "present",
            "severity": "medium",
            "note": "The policy references additional rider premium loading or fees. Ensure these are clearly explained and justified.",
        })

    return findings


def find_discrepancies(fields: dict) -> list:
    discrepancies = []
    required_fields = {
        "policy_number": "missing",
        "issuer": "missing",
        "policy_type": "missing",
        "sum_insured": "missing",
        "expiry_date": "missing",
    }
    for field, issue in required_fields.items():
        if not fields.get(field):
            severity = "high" if field in {"issuer", "policy_type", "sum_insured", "expiry_date"} else "medium"
            discrepancies.append({"field": field, "issue": issue, "severity": severity})
    return discrepancies


def find_missing_criteria(fields: dict) -> list:
    missing = []
    relationship_clauses = ["cancellation", "grace period", "sub-limit", "co-pay", "waiting period"]
    text_lower = fields["raw_text"].lower()
    for item in relationship_clauses:
        if item not in text_lower:
            missing.append({"criteria": item, "recommendation": f"Include {item} clause for better policy clarity."})
    return missing


def generate_report(policy_text: str, model_path: str):
    if isinstance(policy_text, str) and Path(policy_text).exists():
        from .io import load_policy_text
        policy_text = load_policy_text(Path(policy_text))

    fields = extract_fields(policy_text)
    return {
        "policy_summary": fields,
        "critical_findings": risk_analysis(fields),
        "discrepancies": find_discrepancies(fields),
        "missing_criteria": find_missing_criteria(fields),
        "rider_analysis": analyze_riders(fields),
        "llm_summary": run_llm_assessment(policy_text, model_path),
    }
