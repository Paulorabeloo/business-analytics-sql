"""Runs one analysis against the synthetic data and renders its chart.

    python scripts/run_analysis.py 01-pareto-customers

Uses DuckDB so nobody needs a PostgreSQL server to reproduce the numbers;
the queries are written in PostgreSQL syntax that DuckDB also accepts.
Writes analyses/<name>/result.csv and chart.png.
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

INK = "#1f1d1a"
GOLD = "#b8934a"
MUTED = "#8a8378"
PAPER = "#faf7f2"


def load(con: duckdb.DuckDBPyConnection) -> None:
    for t in ("customers", "bottles", "orders", "order_items"):
        con.execute(f"create table {t} as select * from read_csv_auto('{(DATA / t).as_posix()}.csv')")


TEXTS = {
    "en": {
        "title": "Who the revenue depends on",
        "y": "spent (R$)",
        "x": "customers, ranked by spend",
        "y2": "running share of revenue (%)",
        "cut": "{n} customers = half of revenue",
    },
    "pt": {
        "title": "De quem o faturamento depende",
        "y": "gasto (R$)",
        "x": "clientes, do que mais gastou pro que menos",
        "y2": "fatia acumulada do faturamento (%)",
        "cut": "{n} clientes = metade do faturamento",
    },
}


def pareto_chart(rows: list[tuple], cols: list[str], out: Path, lang: str = "en") -> None:
    t = TEXTS[lang]
    pos = cols.index("position")
    spent = cols.index("spent")
    running = cols.index("running_pct")
    x = [r[pos] for r in rows]
    y_bar = [float(r[spent]) for r in rows]
    y_line = [float(r[running]) for r in rows]
    cut = next((r[pos] for r in rows if float(r[running]) >= 50), None)

    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=160)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    colors = [GOLD if cut and p <= cut else "#d9d2c5" for p in x]
    ax.bar(x, y_bar, color=colors, width=0.8)
    ax.set_ylabel(t["y"], color=MUTED)
    ax.set_xlabel(t["x"], color=MUTED)
    ax.tick_params(colors=MUTED)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#d9d2c5")

    ax2 = ax.twinx()
    ax2.plot(x, y_line, color=INK, linewidth=1.8)
    ax2.set_ylim(0, 100)
    ax2.set_ylabel(t["y2"], color=MUTED)
    ax2.tick_params(colors=MUTED)
    ax2.axhline(50, color=MUTED, linewidth=0.8, linestyle=(0, (4, 4)))
    for s in ("top",):
        ax2.spines[s].set_visible(False)
    ax2.spines["right"].set_color("#d9d2c5")
    if cut:
        ax2.axvline(cut, color=GOLD, linewidth=1, linestyle=(0, (3, 3)))
        ax2.annotate(
            t["cut"].format(n=cut),
            xy=(cut, 50), xytext=(cut + 10, 40), color=INK, fontsize=10,
            arrowprops={"arrowstyle": "-", "color": GOLD},
        )
    ax.set_title(t["title"], loc="left", color=INK, fontsize=13, pad=12)
    fig.tight_layout()
    fig.savefig(out, facecolor=PAPER)
    plt.close(fig)


def main(name: str) -> None:
    folder = ROOT / "analyses" / name
    sql = (folder / "query.sql").read_text(encoding="utf-8")
    con = duckdb.connect()
    load(con)
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()

    with open(folder / "result.csv", "w", encoding="utf-8") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(str(v) for v in r) + "\n")

    if name.startswith("01-pareto"):
        pareto_chart(rows, cols, folder / "chart.png", "en")
        pareto_chart(rows, cols, folder / "chart-pt.png", "pt")

    # a small preview in the terminal
    print(" | ".join(cols))
    for r in rows[:12]:
        print(" | ".join(str(v) for v in r))
    print(f"... {len(rows)} rows")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "01-pareto-customers")
