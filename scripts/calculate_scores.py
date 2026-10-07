"""Commercial Opportunity Priority Score: deterministic rules, not a prediction.

Run from the project root: python scripts/calculate_scores.py
Reads source CSVs without modifying them. Snapshot: 2026-09-21.
"""

import csv
import math
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCORE_DATE = date(2026, 9, 21)
STAGE_POINTS = {"Evaluación": 5, "Reunión": 10, "Propuesta": 18, "Negociación": 25}
COMPONENT_MAX = {
    "stage_score": 25, "probability_score": 25, "recency_score": 20,
    "age_score": 10, "deal_value_score": 10, "expected_close_score": 10,
}
EXTRA_FIELDS = [
    "sector", "city", "lead_source", "lead_status", "score_date",
    "days_since_last_contact", "opportunity_age_days", "days_overdue",
    *COMPONENT_MAX, "opportunity_score", "risk_level",
]
OPPORTUNITY_FIELDS = "opportunity_id lead_id company_name assigned_executive product stage potential_amount probability created_date expected_close_date last_contact_date closed_date result".split()


def require(condition, message):
    if not condition:
        raise ValueError(f"Scoring validation failed: {message}")


def read_csv(path, required_fields):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        require(len(fields) == len(set(fields)), f"{path.name}: duplicate columns")
        require(set(required_fields) <= set(fields), f"{path.name}: missing required columns")
        rows = list(reader)
    require(all(None not in row and all(value is not None for value in row.values()) for row in rows), f"{path.name}: malformed CSV row")
    return rows, fields


def parse_date(row, field):
    try:
        value = date.fromisoformat(row[field])
        require(value.isoformat() == row[field], f"{field}: expected YYYY-MM-DD")
        return value
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Scoring validation failed: {row.get('opportunity_id', row.get('lead_id'))}: invalid {field}") from exc


def parse_number(row, field):
    try:
        value = float(row[field])
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Scoring validation failed: {row['opportunity_id']}: invalid {field}") from exc
    require(math.isfinite(value), f"{row['opportunity_id']}: non-finite {field}")
    return value


def band_score(value, bands, default=0):
    for upper, points in bands:
        if value <= upper:
            return points
    return default


def risk_for_score(score):
    return "LOW" if score >= 70 else "MEDIUM" if score >= 45 else "HIGH"


def open_components(stage, probability, recency, age, amount, overdue):
    return {
        "stage_score": STAGE_POINTS[stage],
        "probability_score": probability * 25,
        "recency_score": band_score(recency, [(7, 20), (14, 16), (30, 12), (60, 6), (90, 2)]),
        "age_score": band_score(age, [(30, 10), (60, 8), (90, 6), (120, 3)]),
        "deal_value_score": 2 if amount < 50000 else 4 if amount < 100000 else 6 if amount < 180000 else 8 if amount < 250000 else 10,
        "expected_close_score": 10 if overdue == 0 else 5 if overdue <= 30 else 0,
    }


def calculate_scores(leads, opportunities):
    require(len(opportunities) == 120, "expected exactly 120 opportunities")
    lead_map = {lead["lead_id"]: lead for lead in leads}
    require(len(lead_map) == len(leads) and all(lead_map), "duplicate or blank lead IDs")
    ids = [opp["opportunity_id"] for opp in opportunities]
    require(len(set(ids)) == len(ids) and all(ids), "duplicate or blank opportunity IDs")
    output = []
    for opp in opportunities:
        tag = opp["opportunity_id"]
        require(opp["lead_id"] in lead_map, f"{tag}: invalid lead_id")
        lead = lead_map[opp["lead_id"]]
        require(all(opp[field] == lead[field] for field in ("company_name", "assigned_executive")), f"{tag}: company or executive differs from lead")
        require(all(lead[field] for field in ("sector", "city", "lead_source", "status")), f"{tag}: missing lead attributes")
        probability = parse_number(opp, "probability")
        amount = parse_number(opp, "potential_amount")
        require(0 <= probability <= 1, f"{tag}: probability must be between 0 and 1")
        require(amount >= 0, f"{tag}: negative amount")
        created = parse_date(opp, "created_date")
        contact = parse_date(opp, "last_contact_date")
        expected = parse_date(opp, "expected_close_date")
        require(parse_date(lead, "created_date") <= created <= contact <= SCORE_DATE, f"{tag}: invalid creation/contact chronology")
        require(expected > created, f"{tag}: expected close must follow creation")
        result = opp["result"]
        require(result in ("Open", "Won", "Lost"), f"{tag}: invalid result")
        if result == "Open":
            require(opp["stage"] in STAGE_POINTS and not opp["closed_date"], f"{tag}: invalid open stage or closed_date")
        else:
            require(opp["stage"] == "Cerrado", f"{tag}: closed result requires Cerrado")
            require(contact <= parse_date(opp, "closed_date") <= SCORE_DATE, f"{tag}: invalid closed_date")
            require(probability == (1 if result == "Won" else 0), f"{tag}: inconsistent closed probability")
        recency = (SCORE_DATE - contact).days
        age = (SCORE_DATE - created).days
        overdue = max(0, (SCORE_DATE - expected).days)
        # Components apply only to Open. Closed rows use explicit outcome overrides.
        components = open_components(opp["stage"], probability, recency, age, amount, overdue) if result == "Open" else dict.fromkeys(COMPONENT_MAX, 0)
        score = round(min(100, max(0, sum(components.values()))), 2) if result == "Open" else (100 if result == "Won" else 0)
        output.append({
            **opp, "sector": lead["sector"], "city": lead["city"],
            "lead_source": lead["lead_source"], "lead_status": lead["status"],
            "score_date": SCORE_DATE.isoformat(), "days_since_last_contact": recency,
            "opportunity_age_days": age, "days_overdue": overdue, **components,
            "opportunity_score": score, "risk_level": risk_for_score(score),
        })
    validate_output(output, lead_map)
    return output


def validate_output(rows, lead_map):
    require(len(rows) == 120, "output must contain 120 rows")
    require(len({row["opportunity_id"] for row in rows}) == 120, "duplicate output IDs")
    for row in rows:
        tag = row["opportunity_id"]
        require(row["lead_id"] in lead_map, f"{tag}: invalid output lead")
        score = row["opportunity_score"]
        require(math.isfinite(score) and 0 <= score <= 100, f"{tag}: score outside 0–100")
        require(0 <= float(row["probability"]) <= 1, f"{tag}: invalid probability")
        require(row["risk_level"] in ("LOW", "MEDIUM", "HIGH") and row["risk_level"] == risk_for_score(score), f"{tag}: invalid risk level")
        require(all(isinstance(row[key], int) and row[key] >= 0 for key in ("days_since_last_contact", "opportunity_age_days", "days_overdue")), f"{tag}: invalid day metrics")
        for key, maximum in COMPONENT_MAX.items():
            require(math.isfinite(row[key]) and 0 <= row[key] <= maximum, f"{tag}: {key} outside 0–{maximum}")
        result = row["result"]
        require(result in ("Open", "Won", "Lost"), f"{tag}: invalid result")
        if result == "Open":
            require(row["stage"] in STAGE_POINTS, f"{tag}: invalid open stage")
            require(math.isclose(round(sum(row[key] for key in COMPONENT_MAX), 2), score, abs_tol=1e-9), f"{tag}: component sum differs from score")
        else:
            require(row["stage"] == "Cerrado", f"{tag}: invalid closed stage")
            require(score == (100 if result == "Won" else 0), f"{tag}: invalid closed score")
            require(all(row[key] == 0 for key in COMPONENT_MAX), f"{tag}: closed components must be zero (not applicable)")


def main():
    leads, _ = read_csv(ROOT / "data/leads.csv", "lead_id company_name assigned_executive sector city lead_source status created_date".split())
    opportunities, original_fields = read_csv(ROOT / "data/opportunities.csv", OPPORTUNITY_FIELDS)
    require(not set(original_fields) & set(EXTRA_FIELDS), "source contains scoring columns")
    rows = calculate_scores(leads, opportunities)
    output_path = ROOT / "output/commercial_dataset.csv"
    output_path.parent.mkdir(exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=original_fields + EXTRA_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "opportunity_score": f"{row['opportunity_score']:.2f}"})
    results = Counter(row["result"] for row in rows)
    opened = [row for row in rows if row["result"] == "Open"]
    risks = Counter(row["risk_level"] for row in opened)
    print("Commercial opportunity scoring completed successfully.")
    print(f"\nOpportunities processed: {len(rows)}")
    for result in ("Open", "Won", "Lost"):
        print(f"{result}: {results[result]}")
    print("\nRisk distribution for open opportunities:")
    for risk in ("LOW", "MEDIUM", "HIGH"):
        print(f"{risk}: {risks[risk]}")
    average = f"{sum(row['opportunity_score'] for row in opened) / len(opened):.2f}" if opened else "N/A (no open opportunities)"
    print(f"\nAverage open opportunity score: {average}")
    print("\nOutput:\noutput/commercial_dataset.csv")


if __name__ == "__main__":
    main()
