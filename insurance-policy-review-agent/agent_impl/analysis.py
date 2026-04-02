from datetime import datetime

from .parser import extract_fields
from .llm import run_llm_assessment


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


def find_discrepancies(fields: dict) -> list:
    discrepancies = []
    if not fields["policy_number"]:
        discrepancies.append({"field": "policy_number", "issue": "missing", "severity": "medium"})
    if not fields["issuer"]:
        discrepancies.append({"field": "issuer", "issue": "missing", "severity": "high"})
    if not fields["policy_type"]:
        discrepancies.append({"field": "policy_type", "issue": "missing", "severity": "high"})
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
    fields = extract_fields(policy_text)
    return {
        "policy_summary": fields,
        "critical_findings": risk_analysis(fields),
        "discrepancies": find_discrepancies(fields),
        "missing_criteria": find_missing_criteria(fields),
        "llm_summary": run_llm_assessment(policy_text, model_path),
    }
