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
START = date(2026, 1, 5)
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
        "created_at": rand_date(START, END - timedelta(days=60)).isoformat(),
    })

# appetite: how many orders each customer tends to make (Pareto-shaped)
appetite = {}
for c in customers:
    r = random.random()
    appetite[c["id"]] = 14 if r < 0.05 else 6 if r < 0.15 else 2 if r < 0.45 else 1

# some repeat buyers stop at some point: real customer bases leak, and the
# "who is going quiet" analysis needs people who actually went quiet
stops = {}
for c in customers:
    first = date.fromisoformat(c["created_at"])
    earliest, latest = first + timedelta(days=45), END - timedelta(days=30)
    if appetite[c["id"]] >= 2 and earliest < latest and random.random() < 0.3:
        stops[c["id"]] = rand_date(earliest, latest)

# ── bottles: 60 (two batches of the same 30 names), stock tracked ──
# Real shelves are uneven: a few bottles everyone wants, many that move
# slowly, and some that were bought and barely sold. popularity drives the
# draw below; remaining_ml stops a bottle from selling more than it holds.
bottles = []
popularity = {}
remaining_ml = {}
for i, n in enumerate(NAMES * 2, start=1):
    volume = random.choice([50, 75, 100, 100, 100])
    cost_per_ml = round(random.uniform(6, 26), 2)
    batch = 1 if i <= len(NAMES) else 2
    created = rand_date(START - timedelta(days=20), START + timedelta(days=40)) if batch == 1 \
        else rand_date(START + timedelta(days=90), END - timedelta(days=20))
    bottles.append({
        "id": i,
        "name": n if batch == 1 else f"{n} II",
        "brand": random.choice(BRANDS),
        "volume_ml": volume,
        "cost_total": round(cost_per_ml * volume, 2),
        "price_per_ml": round(cost_per_ml * random.uniform(1.9, 2.6), 2),
        "created_at": created.isoformat(),
    })
    popularity[i] = random.choice([1, 1, 2, 3, 5, 8, 13])
    remaining_ml[i] = volume

# ── orders and items ─────────────────────────────────────────────────
orders, items = [], []
oid = iid = 0
for c in customers:
    first = date.fromisoformat(c["created_at"])
    for _ in range(appetite[c["id"]]):
        oid += 1
        when = rand_date(first, stops.get(c["id"], END))
        # some customers keep the order open and add to it over a few weeks
        # (they wait and ship everything together); the order date is the
        # first item, each item keeps the day it was actually bought
        accumulates = random.random() < 0.4
        n_items = random.choice([1, 1, 1, 2, 2, 3]) + (random.choice([1, 2]) if accumulates else 0)
        item_days = sorted(
            min(when + timedelta(days=random.randint(0, 21) if accumulates else 0), END)
            for _ in range(n_items)
        )
        shipped = item_days[-1] + timedelta(days=random.randint(1, 6))
        orders.append({
            "id": oid,
            "customer_id": c["id"],
            "created_at": when.isoformat(),
            "shipped_at": shipped.isoformat() if shipped <= END and random.random() < 0.85 else "",
        })
        for item_day in item_days:
            heavy = appetite[c["id"]] >= 6
            ml = random.choices([3, 5, 10, 30], weights=[15, 45, 30, 10] if heavy else [30, 50, 20, 0])[0]
            # only bottles already on the shelf that day, with enough left
            candidates = [
                x for x in bottles
                if x["created_at"] <= item_day.isoformat() and remaining_ml[x["id"]] >= ml
            ]
            if not candidates:
                continue
            b = random.choices(candidates, weights=[popularity[x["id"]] for x in candidates])[0]
            remaining_ml[b["id"]] -= ml
            iid += 1
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
                "created_at": item_day.isoformat(),
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
