"""Synthetic dataset for the analyses.

Everything here is invented: names, brands, prices, dates. The shape of the
data mimics a small decant business (a few heavy buyers, many light ones,
most sales in 5 ml), so the analyses produce realistic-looking results.

Writes data/customers.csv, bottles.csv, orders.csv, order_items.csv and a
single data/seed.sql you can load into PostgreSQL after schema.sql.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

FIRST = [
    "Marina", "Beatriz", "Camila", "Larissa", "Juliana", "Fernanda", "Patrícia",
    "Renata", "Tatiane", "Vanessa", "Aline", "Bruna", "Carla", "Daniela", "Elaine",
    "Gabriela", "Helena", "Isabela", "Lívia", "Mariana", "Natália", "Priscila",
    "Rafaela", "Sabrina", "Thais", "Viviane", "André", "Bruno", "Carlos", "Diego",
    "Eduardo", "Felipe", "Gustavo", "Henrique", "Igor", "João", "Leandro", "Marcos",
    "Nelson", "Otávio", "Paulo", "Rafael", "Sérgio", "Thiago", "Vinícius",
]
LAST = [
    "Costa", "Almeida", "Ribeiro", "Souza", "Ferreira", "Oliveira", "Santos",
    "Pereira", "Carvalho", "Martins", "Rocha", "Barbosa", "Cardoso", "Nunes",
    "Moreira", "Teixeira", "Correia", "Dias", "Freitas", "Gomes", "Lima", "Melo",
]
CITIES = [
    ("São Paulo", "SP"), ("Campinas", "SP"), ("Santos", "SP"), ("Rio de Janeiro", "RJ"),
    ("Belo Horizonte", "MG"), ("Curitiba", "PR"), ("Porto Alegre", "RS"),
    ("Florianópolis", "SC"), ("Goiânia", "GO"), ("Brasília", "DF"),
]
BRANDS = ["Maison Aurelle", "Casa Vetiver", "Atelier Nocturne", "Oud & Co", "Verdant"]
NAMES = [
    "Nocturne 42", "Cedar Line", "Ambre Sauvage", "Rose Noire", "Santal Blanc",
    "Iris Gris", "Vetiver Fumé", "Oud Impérial", "Neroli Solaire", "Musc Pâle",
    "Tabac Doux", "Fig Verte", "Cuir Velours", "Jasmin Nuit", "Encens Froid",
    "Pêche Ambrée", "Bois Sec", "Menthe Sauvage", "Safran Doré", "Lavande Noire",
    "Cardamome", "Poivre Rose", "Tonka Brune", "Benjoin Clair", "Gingembre Vif",
    "Mimosa Tendre", "Patchouli 7", "Héliotrope", "Ambrette", "Cade Fumé",
]
VIAL_COST = {3: 1.80, 5: 2.10, 10: 3.40, 30: 0.0}
LABEL_COST = 0.35
START = date(2026, 6, 1)
END = date(2026, 9, 10)


def rand_date(a: date, b: date) -> date:
    return a + timedelta(days=random.randint(0, (b - a).days))


# ── customers: 100, with a few "heavy" ones ─────────────────────────
customers = []
seen = set()
while len(customers) < 100:
    name = f"{random.choice(FIRST)} {random.choice(LAST)}"
    if name in seen:
        continue
    seen.add(name)
    city, state = random.choice(CITIES)
    customers.append({
        "id": len(customers) + 1,
        "name": name,
        "city": city,
        "state": state,
        "created_at": rand_date(START, END - timedelta(days=10)).isoformat(),
    })

# appetite: how many orders each customer tends to make (Pareto-shaped)
appetite = {}
for c in customers:
    r = random.random()
    appetite[c["id"]] = 14 if r < 0.05 else 6 if r < 0.15 else 2 if r < 0.45 else 1

# ── bottles: 30 ───────────────────────────────────────────────────────
bottles = []
for i, n in enumerate(NAMES, start=1):
    volume = random.choice([50, 75, 100, 100, 100])
    cost_per_ml = round(random.uniform(6, 26), 2)
    bottles.append({
        "id": i,
        "name": n,
        "brand": random.choice(BRANDS),
        "volume_ml": volume,
        "cost_total": round(cost_per_ml * volume, 2),
        "price_per_ml": round(cost_per_ml * random.uniform(1.9, 2.6), 2),
        "created_at": rand_date(START - timedelta(days=20), START + timedelta(days=40)).isoformat(),
    })

# ── orders and items ─────────────────────────────────────────────────
orders, items = [], []
oid = iid = 0
for c in customers:
    first = date.fromisoformat(c["created_at"])
    for _ in range(appetite[c["id"]]):
        oid += 1
        when = rand_date(first, END)
        shipped = when + timedelta(days=random.randint(1, 6))
        orders.append({
            "id": oid,
            "customer_id": c["id"],
            "created_at": when.isoformat(),
            "shipped_at": shipped.isoformat() if shipped <= END and random.random() < 0.85 else "",
        })
        for _ in range(random.choice([1, 1, 1, 2, 2, 3])):
            iid += 1
            b = random.choice(bottles)
            heavy = appetite[c["id"]] >= 6
            ml = random.choices([3, 5, 10, 30], weights=[15, 45, 30, 10] if heavy else [30, 50, 20, 0])[0]
            cost_per_ml = b["cost_total"] / b["volume_ml"]
            status = random.choices(["paid", "pending", "bonus"], weights=[70, 24, 6])[0]
            items.append({
                "id": iid,
                "order_id": oid,
                "bottle_id": b["id"],
                "ml": ml,
                "price": round(ml * b["price_per_ml"], 2),
                "cost": round(ml * cost_per_ml + VIAL_COST[ml] + LABEL_COST, 2),
                "status": status,
                "created_at": when.isoformat(),
            })


def write_csv(name: str, rows: list[dict]) -> None:
    with open(OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def sql_value(v) -> str:
    if v == "" or v is None:
        return "null"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def write_seed() -> None:
    with open(OUT / "seed.sql", "w", encoding="utf-8") as f:
        f.write("-- Synthetic data. Load after schema.sql.\n")
        for table, rows in [("customers", customers), ("bottles", bottles),
                            ("orders", orders), ("order_items", items)]:
            cols = ", ".join(rows[0].keys())
            f.write(f"\ninsert into {table} ({cols}) values\n")
            f.write(",\n".join("  (" + ", ".join(sql_value(v) for v in r.values()) + ")" for r in rows))
            f.write(";\n")


for name, rows in [("customers", customers), ("bottles", bottles), ("orders", orders), ("order_items", items)]:
    write_csv(name, rows)
write_seed()
print(f"customers={len(customers)} bottles={len(bottles)} orders={len(orders)} items={len(items)}")
