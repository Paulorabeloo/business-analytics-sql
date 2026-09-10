# Business Analytics in SQL

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

More to come, one question at a time: who is quietly leaving, repeat-purchase
rate, which vial size sells, money sitting in unsold bottles.

## Reproduce

```bash
python scripts/generate_data.py            # writes data/*.csv and data/seed.sql
python scripts/run_analysis.py 01-pareto-customers
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

---

## Em português

Perguntas reais de um negócio real, respondidas em SQL no PostgreSQL.

O negócio vende decants de perfume: frasquinhos de 3, 5 e 10 ml tirados de
frascos inteiros, vendidos pra uma comunidade de entusiastas. Eu construí o
sistema de gestão dele ([estudo de caso aqui](https://github.com/Paulorabeloo/system-acervo-case-study))
e depois passei a perguntar aos dados o que o dono me pergunta.

**Os dados deste repositório são inventados.** Nomes, marcas, preços e datas
saem do `scripts/generate_data.py`, com a forma dos reais (poucos compradores
pesados, muitos leves, 5 ml dominando). As consultas são as mesmas que rodam
no banco de produção.

### Análises

| # | Pergunta | O que usa |
|---|---|---|
| [01](analyses/01-pareto-customers/) | Quantos clientes respondem por metade do faturamento? | `join`, `group by`, `count(distinct)`, funções de janela, acumulado |

Mais por vir, uma pergunta de cada vez: quem está sumindo, taxa de recompra,
qual tamanho mais sai, dinheiro parado em frasco não vendido.

### Reproduzir

```bash
python scripts/generate_data.py            # gera data/*.csv e data/seed.sql
python scripts/run_analysis.py 01-pareto-customers
```

O `run_analysis.py` usa [DuckDB](https://duckdb.org/), então não precisa de
servidor PostgreSQL; o SQL é escrito de um jeito que os dois aceitam. Pra
carregar no PostgreSQL: roda `schema.sql` e depois `data/seed.sql`.

Requisitos: Python 3.10+, `pip install duckdb matplotlib`.

### Como eu trabalho

Cada pasta de análise tem a pergunta, a consulta comentada nas decisões que
importam (por que bônus fica de fora, por que pedido com três itens é um
pedido), o resultado nos dados fictícios e a frase que eu diria pro dono. A
frase é a entrega; o SQL é o caminho.
