# Análise de negócio em SQL

[English version](README.md) · Versão em português

Perguntas reais de um negócio real, respondidas em SQL no PostgreSQL.

O negócio vende decants de perfume: frasquinhos de 3, 5 e 10 ml tirados de
frascos inteiros, vendidos pra uma comunidade de entusiastas. Eu construí o
sistema de gestão dele ([estudo de caso aqui](https://github.com/Paulorabeloo/system-acervo-case-study))
e depois passei a perguntar aos dados o que o dono me pergunta.

**Os dados deste repositório são inventados.** Nomes, marcas, preços e datas
saem do `scripts/generate_data.py`, com a forma dos reais (poucos compradores
pesados, muitos leves, 5 ml dominando). As consultas são as mesmas que rodam
no banco de produção.

## Análises

| # | Pergunta | O que usa |
|---|---|---|
| [01](analyses/01-pareto-customers/#em-português) | Quantos clientes respondem por metade do faturamento? | `join`, `group by`, `count(distinct)`, funções de janela, acumulado |
| [02](analyses/02-customers-going-quiet/#em-português) | Quais clientes estão sumindo, medido contra o ritmo de cada um? | `lag()` com partição, conta com datas, `having`, `cross join` |
| [03](analyses/03-repeat-purchase-rate/#em-português) | Quantos clientes voltam, e por que a resposta depende da unidade? | `count(distinct)`, `union all`, faixas com `case`, `filter`, janela com partição |
| [04](analyses/04-vial-size-mix/#em-português) | Qual tamanho mais sai, e qual traz o dinheiro? | `group by`, duas fatias com `sum() over ()`, margem por grupo |
| [05](analyses/05-money-in-bottles/#em-português) | Quanto dinheiro está parado em frasco não vendido, e quais pararam de girar? | `left join`, `coalesce`, `greatest`, conta com datas, fatia do total |

Cinco perguntas até aqui. As próximas vêm do que o dono perguntar; foi
assim que a lista nasceu.

## Reproduzir

```bash
python scripts/generate_data.py            # gera data/*.csv e data/seed.sql
python scripts/run_analysis.py 01-pareto-customers
python scripts/run_analysis.py 02-customers-going-quiet
python scripts/run_analysis.py 03-repeat-purchase-rate
python scripts/run_analysis.py 04-vial-size-mix
python scripts/run_analysis.py 05-money-in-bottles
```

O `run_analysis.py` usa [DuckDB](https://duckdb.org/), então não precisa de
servidor PostgreSQL; o SQL é escrito de um jeito que os dois aceitam. Pra
carregar no PostgreSQL: roda `schema.sql` e depois `data/seed.sql`.

Requisitos: Python 3.10+, `pip install duckdb matplotlib`.

## Como eu trabalho

Cada pasta de análise tem a pergunta, a consulta comentada nas decisões que
importam (por que bônus fica de fora, por que pedido com três itens é um
pedido), o resultado nos dados fictícios e a frase que eu diria pro dono. A
frase é a entrega; o SQL é o caminho.
