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


QUIET_TEXTS = {
    "en": {
        "title": "Who is going quiet",
        "x": "days",
        "usual": "usual gap between orders",
        "silent": "days since last order",
        "flag": "silent for more than twice the usual gap",
    },
    "pt": {
        "title": "Quem está sumindo",
        "x": "dias",
        "usual": "intervalo normal entre pedidos",
        "silent": "dias desde o último pedido",
        "flag": "parado há mais que o dobro do normal",
    },
}


def quiet_chart(rows: list[tuple], cols: list[str], out: Path, lang: str = "en") -> None:
    """One line per regular customer: grey bar = usual gap, dot = days silent."""
    t = QUIET_TEXTS[lang]
    name = cols.index("customer")
    usual = cols.index("usual_gap_days")
    silent = cols.index("days_silent")
    flag = cols.index("going_quiet")
    data = list(reversed(rows[:20]))  # the 20 with the highest ratio, biggest on top
    y = list(range(len(data)))

    fig, ax = plt.subplots(figsize=(10, 0.42 * len(data) + 1.6), dpi=160)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    ax.barh(y, [float(r[usual]) for r in data], color="#d9d2c5", height=0.55, label=t["usual"])
    for yi, r in zip(y, data):
        quiet = bool(r[flag])
        ax.plot([0, float(r[silent])], [yi, yi], color=GOLD if quiet else MUTED, linewidth=1, alpha=0.6)
        ax.plot(float(r[silent]), yi, "o", color=GOLD if quiet else MUTED, markersize=7)
    ax.plot([], [], "o", color=GOLD, label=t["flag"])
    ax.plot([], [], "o", color=MUTED, label=t["silent"])
    ax.set_yticks(y)
    ax.set_yticklabels([r[name] for r in data], color=INK, fontsize=9)
    ax.set_xlabel(t["x"], color=MUTED)
    ax.tick_params(colors=MUTED)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#d9d2c5")
    ax.legend(loc="lower right", frameon=False, fontsize=9, labelcolor=MUTED)
    ax.set_title(t["title"], loc="left", color=INK, fontsize=13, pad=12)
    fig.tight_layout()
    fig.savefig(out, facecolor=PAPER)
    plt.close(fig)


REPEAT_TEXTS = {
    "en": {
        "title": "How many times customers bought",
        "x": "share of customers (%)",
        "y": "times bought",
        "units": {"orders": "by orders", "purchase days": "by purchase days"},
        "rate": "repeat rate {r}%",
    },
    "pt": {
        "title": "Quantas vezes os clientes compraram",
        "x": "fatia dos clientes (%)",
        "y": "vezes que comprou",
        "units": {"orders": "por pedido", "purchase days": "por dia de compra"},
        "rate": "recompra {r}%",
    },
}


def repeat_chart(rows: list[tuple], cols: list[str], out: Path, lang: str = "en") -> None:
    """Grouped bars: the same customers bucketed by two units of 'bought again'."""
    t = REPEAT_TEXTS[lang]
    unit = cols.index("unit")
    bucket = cols.index("bucket")
    pct = cols.index("pct_of_customers")
    rate = cols.index("repeat_rate_pct")
    order = ["1", "2", "3 to 5", "6+"]
    labels = order if lang == "en" else ["1", "2", "3 a 5", "6+"]
    units = ["orders", "purchase days"]
    colors = {"orders": "#d9d2c5", "purchase days": GOLD}
    data = {u: {r[bucket]: float(r[pct]) for r in rows if r[unit] == u} for u in units}
    rates = {u: next(float(r[rate]) for r in rows if r[unit] == u) for u in units}

    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=160)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    h = 0.36
    for k, u in enumerate(units):
        ys = [i + (k - 0.5) * h for i in range(len(order))]
        vals = [data[u].get(b, 0.0) for b in order]
        ax.barh(ys, vals, height=h, color=colors[u],
                label=f"{t['units'][u]}, {t['rate'].format(r=rates[u])}")
        for y, v in zip(ys, vals):
            ax.text(v + 0.8, y, f"{v:.0f}%", va="center", fontsize=8.5, color=MUTED)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(labels, color=INK)
    ax.invert_yaxis()
    ax.set_xlabel(t["x"], color=MUTED)
    ax.set_ylabel(t["y"], color=MUTED)
    ax.tick_params(colors=MUTED)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#d9d2c5")
    ax.legend(loc="lower right", frameon=False, fontsize=9, labelcolor=MUTED)
    ax.set_title(t["title"], loc="left", color=INK, fontsize=13, pad=12)
    fig.tight_layout()
    fig.savefig(out, facecolor=PAPER)
    plt.close(fig)


MIX_TEXTS = {
    "en": {
        "title": "Which size sells, which size pays",
        "x": "share (%)",
        "y": "vial size",
        "items": "share of items sold",
        "revenue": "share of revenue",
        "margin": "margin {m}%",
    },
    "pt": {
        "title": "Qual tamanho sai, qual tamanho paga",
        "x": "fatia (%)",
        "y": "tamanho",
        "items": "fatia dos itens vendidos",
        "revenue": "fatia do faturamento",
        "margin": "margem {m}%",
    },
}


def mix_chart(rows: list[tuple], cols: list[str], out: Path, lang: str = "en") -> None:
    """Grouped bars per size: share of items vs share of revenue, margin as a label."""
    t = MIX_TEXTS[lang]
    ml = cols.index("ml")
    pi = cols.index("pct_items")
    pr = cols.index("pct_revenue")
    mg = cols.index("margin_pct")
    sizes = [r[ml] for r in rows]
    labels = [f"{s} ml" for s in sizes]

    fig, ax = plt.subplots(figsize=(10, 4.4), dpi=160)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    h = 0.36
    ys = list(range(len(rows)))
    v_items = [float(r[pi]) for r in rows]
    v_rev = [float(r[pr]) for r in rows]
    ax.barh([y - h / 2 for y in ys], v_items, height=h, color="#d9d2c5", label=t["items"])
    ax.barh([y + h / 2 for y in ys], v_rev, height=h, color=GOLD, label=t["revenue"])
    for y, a, b, r in zip(ys, v_items, v_rev, rows):
        ax.text(a + 0.8, y - h / 2, f"{a:.0f}%", va="center", fontsize=8.5, color=MUTED)
        ax.text(b + 0.8, y + h / 2, f"{b:.0f}%  ·  " + t["margin"].format(m=f"{float(r[mg]):.0f}"),
                va="center", fontsize=8.5, color=MUTED)
    ax.set_yticks(ys)
    ax.set_yticklabels(labels, color=INK)
    ax.invert_yaxis()
    ax.set_xlabel(t["x"], color=MUTED)
    ax.set_ylabel(t["y"], color=MUTED)
    ax.set_xlim(0, max(v_items + v_rev) * 1.35)
    ax.tick_params(colors=MUTED)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#d9d2c5")
    ax.legend(loc="lower right", frameon=False, fontsize=9, labelcolor=MUTED)
    ax.set_title(t["title"], loc="left", color=INK, fontsize=13, pad=12)
    fig.tight_layout()
    fig.savefig(out, facecolor=PAPER)
    plt.close(fig)


MONEY_TEXTS = {
    "en": {
        "title": "Money sitting in bottles",
        "x": "cost still on the shelf (R$)",
        "moving": "sold something in the last 60 days",
        "stalled": "no sale in 60 days or more",
    },
    "pt": {
        "title": "Dinheiro parado em frasco",
        "x": "custo ainda na prateleira (R$)",
        "moving": "vendeu algo nos últimos 60 dias",
        "stalled": "sem venda há 60 dias ou mais",
    },
}


def money_chart(rows: list[tuple], cols: list[str], out: Path, lang: str = "en") -> None:
    """Horizontal bars, one per bottle, biggest amount on top; stalled ones in gold."""
    t = MONEY_TEXTS[lang]
    name = cols.index("name")
    cost = cols.index("cost_sitting")
    stalled = cols.index("stalled")
    pct = cols.index("pct_sold")
    data = list(reversed(rows[:20]))
    ys = list(range(len(data)))

    fig, ax = plt.subplots(figsize=(10, 0.36 * len(data) + 1.6), dpi=160)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    vals = [float(r[cost]) for r in data]
    colors = [GOLD if bool(r[stalled]) else "#d9d2c5" for r in data]
    ax.barh(ys, vals, color=colors, height=0.62)
    for y, v, r in zip(ys, vals, data):
        money = f"{v:,.0f}" if lang == "en" else f"{v:,.0f}".replace(",", ".")
        sold = f"{float(r[pct]):.0f}% sold" if lang == "en" else f"{float(r[pct]):.0f}% vendido"
        ax.text(v + max(vals) * 0.01, y, f"R$ {money}  ·  {sold}", va="center", fontsize=8, color=MUTED)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[name] for r in data], color=INK, fontsize=9)
    ax.set_xlabel(t["x"], color=MUTED)
    ax.set_xlim(0, max(vals) * 1.3)
    ax.tick_params(colors=MUTED)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#d9d2c5")
    from matplotlib.patches import Patch
    ax.legend(
        handles=[Patch(color="#d9d2c5", label=t["moving"]), Patch(color=GOLD, label=t["stalled"])],
        loc="lower right", frameon=False, fontsize=9, labelcolor=MUTED,
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
    elif name.startswith("02-customers"):
        quiet_chart(rows, cols, folder / "chart.png", "en")
        quiet_chart(rows, cols, folder / "chart-pt.png", "pt")
    elif name.startswith("03-repeat"):
        repeat_chart(rows, cols, folder / "chart.png", "en")
        repeat_chart(rows, cols, folder / "chart-pt.png", "pt")
    elif name.startswith("04-vial"):
        mix_chart(rows, cols, folder / "chart.png", "en")
        mix_chart(rows, cols, folder / "chart-pt.png", "pt")
    elif name.startswith("05-money"):
        money_chart(rows, cols, folder / "chart.png", "en")
        money_chart(rows, cols, folder / "chart-pt.png", "pt")

    # a small preview in the terminal
    print(" | ".join(cols))
    for r in rows[:12]:
        print(" | ".join(str(v) for v in r))
    print(f"... {len(rows)} rows")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "01-pareto-customers")
