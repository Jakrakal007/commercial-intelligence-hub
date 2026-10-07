"""Synthetic commercial CSVs. Fixed snapshot and seed ensure reproducibility.

Run: python scripts/generate_data.py [--as-of YYYY-MM-DD] [--seed 42]
Probabilities are fractions (1 = 100%); amounts are whole PEN.
Uses only the Python standard library. Names are synthetic combinations.
"""

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = {
    "leads": "lead_id company_name contact_name sector city lead_source assigned_executive created_date last_contact_date status".split(),
    "opportunities": "opportunity_id lead_id company_name assigned_executive product stage potential_amount probability created_date expected_close_date last_contact_date closed_date result".split(),
    "activities": "activity_id lead_id opportunity_id executive activity_type activity_date notes".split(),
}
SECTORS = ["Retail", "Minería", "Construcción", "Tecnología", "Agroindustria", "Servicios", "Logística", "Manufactura", "Turismo"]
PREFIXES = ["Comercial", "Minera", "Constructora", "Tecnología", "Agroexportadora", "Servicios", "Logística", "Industrias", "Turismo"]
CITIES = ["Lima", "Arequipa", "Trujillo", "Cusco", "Piura", "Chiclayo", "Huánuco", "Ica"]
SOURCES = ["LinkedIn", "Referido", "Website", "Evento", "Email", "Prospección directa"]
EXECUTIVES = ["Andrea Torres", "Carlos Mendoza", "Lucía Vega", "Diego Salazar"]
PRODUCTS = ["Fondo Conservador", "Fondo Balanceado", "Fondo Crecimiento", "Gestión Patrimonial", "Inversión Corporativa"]
STAGES = {"Evaluación": (10, 30), "Reunión": (25, 45), "Propuesta": (45, 65), "Negociación": (65, 85)}
NOTES = {
    "Llamada": ["Cliente solicita información adicional.", "Se coordinó una próxima conversación."],
    "Email": ["Se recibió una consulta comercial inicial.", "Se compartió información del producto."],
    "Reunión": ["Se realizó reunión de presentación.", "Se revisaron las necesidades del cliente."],
    "Seguimiento": ["Pendiente confirmación del cliente.", "Cliente evaluando alternativas."],
    "Presentación": ["Se presentaron las características del producto."],
    "Propuesta enviada": ["Se envió propuesta comercial."],
}
STATUS_COUNTS = {"Nuevo": 30, "Contactado": 50, "Calificado": 65, "Descartado": 45, "Convertido": 60}


def require(condition, message):
    if not condition:
        raise ValueError(f"Commercial data validation failed: {message}")


def year_start(as_of):
    try:
        return as_of.replace(year=as_of.year - 1)
    except ValueError:  # February 29 in a leap year.
        return as_of.replace(year=as_of.year - 1, day=28)


def generate(as_of, seed):
    rng = random.Random(seed)
    start = year_start(as_of)
    statuses = [status for status, count in STATUS_COUNTS.items() for _ in range(count)]
    cities = [city for city, count in zip(CITIES, [125, 30, 25, 20, 18, 14, 8, 10]) for _ in range(count)]
    executives = (EXECUTIVES * 63)[:250]
    for values in (statuses, cities, executives):
        rng.shuffle(values)
    names = ["Valeria", "Mateo", "Camila", "Joaquín", "Renata", "Alonso", "Daniela", "Gabriel", "Mariana", "Sebastián"]
    surnames = ["Rivas", "Paredes", "Soto", "Cáceres", "Vidal", "Lozano", "Campos", "Aranda", "Robles", "Delgado", "Linares", "Medina", "Fuentes", "Navarro", "Aguilar", "Ponce"]
    brands = ["Solaris", "Horizonte", "Pacífico", "Altavista", "Nova", "Andina", "Aurora", "Cumbre", "Brisa", "Prisma"]
    modifiers = ["Central", "del Sur", "del Norte", "Integral", "Global", "del Valle", "del Sol", "del Pacífico", "Regional", "Perú"]
    company_pool = {sector: rng.sample([f"{prefix} {brand} {suffix} SAC" for brand in brands for suffix in modifiers], 100) for sector, prefix in zip(SECTORS, PREFIXES)}
    leads = []
    for i, status in enumerate(statuses, 1):
        sector = rng.choices(SECTORS, weights=[16, 10, 12, 14, 10, 16, 10, 8, 4])[0]
        # Mature leads leave time for qualification and a possible close.
        end = as_of if status == "Nuevo" else as_of - timedelta(days=90)
        created = start + timedelta(days=rng.randint(0, (end - start).days))
        leads.append(dict(zip(FIELDS["leads"], [f"LEAD-{i:04d}", company_pool[sector].pop(), f"{rng.choice(names)} {rng.choice(surnames)} {rng.choice(surnames)}", sector, cities[i - 1], rng.choices(SOURCES, weights=[25, 23, 15, 10, 7, 20])[0], executives[i - 1], created, created, status])))

    selected = rng.sample([lead for lead in leads if lead["status"] in ("Calificado", "Convertido")], 120)
    results = ["Open"] * 76 + ["Won"] * 26 + ["Lost"] * 18
    rng.shuffle(results)
    opportunities = []
    for i, (lead, result) in enumerate(zip(selected, results), 1):
        created = lead["created_date"] + timedelta(days=rng.randint(5, 30))
        product = rng.choices(PRODUCTS, weights=[25, 30, 20, 15, 10])[0]
        large = rng.random() < (0.55 if product == "Inversión Corporativa" else 0.08)
        amount = rng.triangular(255000, 500000, 310000) if large else rng.triangular(20000, 200000, 70000)
        stage = rng.choices(list(STAGES), weights=[30, 25, 28, 17])[0] if result == "Open" else "Cerrado"
        probability = rng.randint(*STAGES[stage]) / 100 if result == "Open" else int(result == "Won")
        closed = None if result == "Open" else created + timedelta(days=rng.randint(15, min(100, (as_of - created).days)))
        opportunities.append(dict(zip(FIELDS["opportunities"], [f"OPP-{i:04d}", lead["lead_id"], lead["company_name"], lead["assigned_executive"], product, stage, round(amount / 1000) * 1000, probability, created, created + timedelta(days=rng.randint(15, 120)), created, closed, result])))

    lead_map = {lead["lead_id"]: lead for lead in leads}
    opp_by_lead = {opp["lead_id"]: opp for opp in opportunities}
    activities = []

    def add_activity(lead, opp=None):
        lower = opp["created_date"] if opp else lead["created_date"]
        upper = (opp["closed_date"] or as_of) if opp else (opp_by_lead[lead["lead_id"]]["created_date"] - timedelta(days=1) if lead["lead_id"] in opp_by_lead else as_of)
        weights = [32, 30, 12, 18, 5, 3]
        if not opp or opp["stage"] in ("Evaluación", "Reunión"):
            weights[-1] = 0
        kind = "Email" if lead["status"] == "Nuevo" else rng.choices(list(NOTES), weights=weights)[0]
        activity_date = lower + timedelta(days=rng.randint(0, (upper - lower).days))
        note = NOTES["Email"][0] if lead["status"] == "Nuevo" else rng.choice(NOTES[kind])
        activities.append(dict(zip(FIELDS["activities"], [f"ACT-{len(activities) + 1:04d}", lead["lead_id"], opp["opportunity_id"] if opp else "", lead["assigned_executive"], kind, activity_date, note])))

    # New leads have an inbound email, before outbound qualification.
    for lead in leads:
        add_activity(lead)
    for opp in opportunities:
        add_activity(lead_map[opp["lead_id"]], opp)
    for opp in rng.choices(opportunities, k=30):
        add_activity(lead_map[opp["lead_id"]], opp)
    for lead in leads:
        lead["last_contact_date"] = max(a["activity_date"] for a in activities if a["lead_id"] == lead["lead_id"])
    for opp in opportunities:
        opp["last_contact_date"] = max(a["activity_date"] for a in activities if a["opportunity_id"] == opp["opportunity_id"])
    return leads, opportunities, activities


def validate(leads, opportunities, activities, as_of):
    for rows, name, count, prefix, key in [(leads, "leads", 250, "LEAD", "lead_id"), (opportunities, "opportunities", 120, "OPP", "opportunity_id"), (activities, "activities", 400, "ACT", "activity_id")]:
        require(len(rows) == count, f"{name}: expected {count} rows")
        require({r[key] for r in rows} == {f"{prefix}-{i:04d}" for i in range(1, count + 1)}, f"{name}: duplicate or invalid IDs")
        require(all(set(r) == set(FIELDS[name]) for r in rows), f"{name}: invalid columns")
    lead_map = {r["lead_id"]: r for r in leads}
    opp_map = {r["opportunity_id"]: r for r in opportunities}
    for lead in leads:
        tag = lead["lead_id"]
        require(lead["sector"] in SECTORS and lead["city"] in CITIES and lead["lead_source"] in SOURCES and lead["assigned_executive"] in EXECUTIVES, f"{tag}: invalid category")
        require(lead["status"] in STATUS_COUNTS, f"{tag}: invalid status")
        require(year_start(as_of) <= lead["created_date"] <= lead["last_contact_date"] <= as_of, f"{tag}: invalid dates")
    for opp in opportunities:
        tag = opp["opportunity_id"]
        require(opp["lead_id"] in lead_map, f"{tag}: orphan lead")
        lead = lead_map[opp["lead_id"]]
        require(lead["status"] in ("Calificado", "Convertido"), f"{tag}: ineligible lead")
        require(all(opp[k] == lead[k] for k in ("company_name", "assigned_executive")), f"{tag}: company/executive mismatch")
        require(opp["product"] in PRODUCTS and 20000 <= opp["potential_amount"] <= 500000 and opp["potential_amount"] % 1000 == 0, f"{tag}: invalid product/amount")
        require(lead["created_date"] <= opp["created_date"] <= opp["last_contact_date"] <= lead["last_contact_date"] <= as_of, f"{tag}: invalid contact chronology")
        require(15 <= (opp["expected_close_date"] - opp["created_date"]).days <= 120, f"{tag}: invalid expected close")
        require(opp["result"] in ("Open", "Won", "Lost"), f"{tag}: invalid result")
        if opp["result"] == "Open":
            require(opp["stage"] in STAGES and opp["closed_date"] is None, f"{tag}: invalid open state")
            low, high = STAGES[opp["stage"]]
            require(low / 100 <= opp["probability"] <= high / 100, f"{tag}: invalid stage probability")
        else:
            require(opp["stage"] == "Cerrado" and opp["closed_date"] is not None, f"{tag}: missing closure")
            require(opp["created_date"] <= opp["last_contact_date"] <= opp["closed_date"] <= as_of, f"{tag}: invalid closure dates")
            require(opp["probability"] == int(opp["result"] == "Won"), f"{tag}: invalid closing probability")
    for activity in activities:
        tag = activity["activity_id"]
        require(activity["lead_id"] in lead_map, f"{tag}: orphan lead")
        lead = lead_map[activity["lead_id"]]
        require(activity["executive"] == lead["assigned_executive"] and activity["activity_type"] in NOTES, f"{tag}: invalid executive/type")
        require(lead["created_date"] <= activity["activity_date"] <= lead["last_contact_date"] <= as_of, f"{tag}: invalid activity chronology")
        if activity["opportunity_id"]:
            require(activity["opportunity_id"] in opp_map, f"{tag}: orphan opportunity")
            opp = opp_map[activity["opportunity_id"]]
            require(opp["lead_id"] == activity["lead_id"], f"{tag}: unrelated opportunity")
            require(opp["created_date"] <= activity["activity_date"] <= opp["last_contact_date"], f"{tag}: activity outside opportunity timeline")
        else:
            require(all(activity["activity_date"] < o["created_date"] for o in opportunities if o["lead_id"] == activity["lead_id"]), f"{tag}: unlinked activity after opportunity creation")
    for rows, key in [(leads, "lead_id"), (opportunities, "opportunity_id")]:
        for row in rows:
            contacts = [a["activity_date"] for a in activities if a[key] == row[key]]
            require(bool(contacts) and row["last_contact_date"] == max(contacts), f"{row[key]}: last contact differs from history")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date(2026, 9, 21))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    require(args.as_of <= date.today(), "snapshot date cannot be in the future")
    datasets = generate(args.as_of, args.seed)
    validate(*datasets, args.as_of)
    (ROOT / "data").mkdir(exist_ok=True)
    for name, rows in zip(FIELDS, datasets):
        with (ROOT / "data" / f"{name}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS[name], lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    print("Commercial data generated successfully.\n")
    for name, rows in zip(FIELDS, datasets):
        print(f"{name.title()}: {len(rows)}")
    print(f"\nSnapshot: {args.as_of}; seed: {args.seed}")
    print("\nFiles created:")
    for name in FIELDS:
        print(f"data/{name}.csv")


if __name__ == "__main__":
    main()
