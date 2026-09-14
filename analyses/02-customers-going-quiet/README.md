# 02 · Which customers are going quiet?

**The sentence I gave the owner:** *"Five of your eight biggest customers
have stopped. Not 'slowed down': each one used to buy every few days and
has been silent for weeks. If you message five people this week, it is
these five."*

![Who is going quiet](chart.png)

## Why this question

"Has not bought in 30 days" is the usual alarm, and it is wrong in both
directions. Someone who buys every week and vanished for a month is a
problem; someone who buys twice a year is right on schedule. The alarm has
to be relative to each customer's own rhythm, otherwise the follow-up list
is noise and the owner stops reading it.

## How it is answered

[`query.sql`](query.sql), in five steps:

1. **One row per day a customer bought something.** Not per order: an
   order can stay open and collect items for weeks, so "order" would hide
   purchases (see [analysis 03](../03-repeat-purchase-rate/)). Gifts
   (`status = 'bonus'`) do not count. `distinct` does the collapsing.
2. **Days since the customer's previous purchase day**, with `lag()`. The
   window is `partition by customer_id order by purchase_day`, so each
   customer's list is read on its own and the first day gets `null`
   (nothing before it).
3. **One row per customer**: purchases, last one, and the usual gap
   (`avg` of the gaps; it ignores the `null` from the first day). Only
   customers with **3 or more purchase days** stay, via `having`: with one
   gap there is no rhythm to compare against.
4. **"Today" is the last day in the data**, taken with `max(created_at)`
   and attached with `cross join`. That keeps the result identical every
   time it runs; in production it is `current_date`.
5. **Flag whoever has been silent for more than twice their usual gap,
   and for at least 14 days.** The floor is not in the textbook version;
   it came from running the query on real data. When regulars buy every
   2 or 3 days, "twice the gap" flags a long weekend. The whole list is
   returned so the chart shows the healthy ones too.

In the chart (the 20 highest ratios), the grey bar is how long the
customer usually waits between purchases and the dot is how long they have
been waiting now. A dot far past its bar is the person to call.

## Result on the synthetic data

| customer | purchases | last purchase | days silent | usual gap | ratio | quiet |
|---|---|---|---|---|---|---|
| Juliana Almeida | 4 | 2026-05-13 | 120 | 3 | 40.0 | yes |
| Sabrina Oliveira | 22 | 2026-07-17 | 55 | 3 | 18.3 | yes |
| Vanessa Santos | 16 | 2026-06-01 | 101 | 7 | 14.4 | yes |
| Fernanda Dias | 19 | 2026-08-05 | 36 | 3 | 12.0 | yes |
| ... | | | | | | |
| Larissa Rocha | 3 | 2026-07-04 | 68 | 77 | 0.9 | no |

- **36 customers have a rhythm** (3 or more purchase days). **21 of them
  went quiet**, and five of those are in the top 8 of
  [analysis 01](../01-pareto-customers/).
- Larissa Rocha shows why the rule is relative: 68 days silent looks bad,
  but she buys roughly every 77 days, so she is not flagged.

## What came out of it

- The flagged names go to the owner as a short list, not a report: name,
  last order, what they used to buy. The message is personal, not a
  campaign.
- The threshold (twice the usual gap) is a choice, not a law. A stricter
  business would use 1.5; the query has one number to change.

## Reproduce

```bash
python scripts/generate_data.py
python scripts/run_analysis.py 02-customers-going-quiet
```

---

## Em português

![Quem está sumindo](chart-pt.png)

**A frase que eu dei pro dono:** *"Cinco dos seus oito maiores clientes
pararam. Não é 'diminuíram': cada um comprava a cada poucos dias, e está há
semanas sem aparecer. Se você mandar mensagem pra cinco pessoas essa
semana, são essas cinco."*

### Por que essa pergunta

"Não compra há 30 dias" é o alarme de sempre, e erra pros dois lados. Quem
compra toda semana e sumiu por um mês é problema; quem compra duas vezes
por ano está no prazo. O alarme tem que ser relativo ao ritmo de cada
cliente, senão a lista de contato vira ruído e o dono para de ler.

### Como é respondida

[`query.sql`](query.sql), em cinco passos:

1. **Uma linha por dia em que o cliente comprou algo.** Não por pedido:
   o pedido pode ficar aberto juntando itens por semanas, então "pedido"
   esconderia compras (ver [análise 03](../03-repeat-purchase-rate/)).
   Bônus (`status = 'bonus'`) não conta. O `distinct` faz o amassamento.
2. **Dias desde o dia de compra anterior do cliente**, com `lag()`. A
   janela é `partition by customer_id order by purchase_day`: a lista de
   cada cliente é lida separada, e o primeiro dia recebe `null` (não tem
   nada antes).
3. **Uma linha por cliente**: compras, última, e intervalo normal (`avg`
   dos intervalos; ele ignora o `null` do primeiro). Só fica quem tem
   **3 dias de compra ou mais**, via `having`: com um intervalo só, não
   existe ritmo pra comparar.
4. **"Hoje" é o último dia dos dados**, pego com `max(created_at)` e colado
   com `cross join`. Assim o resultado é o mesmo toda vez que roda; em
   produção é `current_date`.
5. **Marca quem está parado há mais que o dobro do intervalo normal, e há
   pelo menos 14 dias.** O piso não estava na versão de livro; veio de
   rodar a consulta em dado real. Quando os regulares compram a cada 2 ou
   3 dias, "o dobro" marca um fim de semana prolongado. A lista inteira
   volta, pra o gráfico mostrar também quem está saudável.

No gráfico (os 20 maiores), a barra cinza é quanto o cliente costuma
esperar entre compras e a bolinha é quanto está esperando agora. Bolinha
bem depois da barra é a pessoa pra chamar.

### Resultado nos dados fictícios

- **36 clientes têm ritmo** (3 dias de compra ou mais). **21 deles
  sumiram**, e cinco desses estão no top 8 da
  [análise 01](../01-pareto-customers/).
- Larissa Rocha mostra por que a regra é relativa: 68 dias parada parece
  ruim, mas ela compra mais ou menos a cada 77 dias, então não é marcada.

### O que saiu disso

- Os nomes marcados vão pro dono como lista curta, não como relatório:
  nome, último pedido, o que costumava comprar. A mensagem é pessoal, não
  campanha.
- O corte (dobro do intervalo normal) é escolha, não lei. Um negócio mais
  rígido usaria 1,5; a consulta tem um número só pra trocar.
