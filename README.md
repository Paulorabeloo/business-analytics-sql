# Business Analytics in SQL

English version · [Versão em português](README.pt-BR.md)

Real questions from a real business, answered in SQL on PostgreSQL.

The business sells perfume decants: small vials (3, 5, 10 ml) filled from
full bottles, sold to a community of enthusiasts. I built its management
system ([case study here](https://github.com/Paulorabeloo/system-acervo-case-study))
and then started asking the data the questions the owner asks me.

**The data in this repository is synthetic.** Names, brands, prices and
dates are invented by `scripts/generate_data.py`, shaped to look like the
real thing (a few heavy buyers, many light ones, most sales in 5 ml). The
queries are the ones that run against the production database.

## Analyses

| # | Question | What it uses |
|---|---|---|
| [01](analyses/01-pareto-customers/) | How many customers account for half of the revenue? | `join`, `group by`, `count(distinct)`, window functions, running total |
| [02](analyses/02-customers-going-quiet/) | Which customers are going quiet, measured against their own rhythm? | `lag()` over a partition, date arithmetic, `having`, `cross join` |
| [03](analyses/03-repeat-purchase-rate/) | How many customers come back, and why the answer depends on the unit? | `count(distinct)`, `union all`, `case` buckets, `filter`, window over a partition |
| [04](analyses/04-vial-size-mix/) | Which vial size sells, and which one makes the money? | `group by`, two shares with `sum() over ()`, margin per group |
| [05](analyses/05-money-in-bottles/) | How much money is sitting in bottles that have not sold yet, and which ones stopped moving? | `left join`, `coalesce`, `greatest`, date arithmetic, share of total |

Five questions so far. The next ones come from whatever the owner asks
next; that is how the list was built.

## Reproduce

```bash
python scripts/generate_data.py            # writes data/*.csv and data/seed.sql
python scripts/run_analysis.py 01-pareto-customers
python scripts/run_analysis.py 02-customers-going-quiet
python scripts/run_analysis.py 03-repeat-purchase-rate
python scripts/run_analysis.py 04-vial-size-mix
python scripts/run_analysis.py 05-money-in-bottles
```

`run_analysis.py` uses [DuckDB](https://duckdb.org/) so you do not need a
PostgreSQL server; the SQL is written so both accept it. To load the data
into PostgreSQL instead: run `schema.sql`, then `data/seed.sql`.

Requirements: Python 3.10+, `pip install duckdb matplotlib`.

## How I work

Each analysis folder has the question, the query with comments on the
choices that matter (why gifts are excluded, why an order with three items
is one order), the result on the synthetic data, and the one sentence I
would say to the owner. The sentence is the deliverable; the SQL is how I
got there.
