# 02 · Which customers are going quiet?

**The sentence I gave the owner:** *"Three of your eight biggest customers
have stopped. Not 'slowed down': each one used to buy every few days and
has been silent for weeks. If you message three people this week, it is
these three."*

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
| Thiago Pereira | 4 | 2026-04-08 | 155 | 4 | 38.8 | yes |
| Beatriz Souza | 5 | 2026-05-04 | 129 | 5 | 25.8 | yes |
| Natália Pereira | 4 | 2026-06-15 | 87 | 5 | 17.4 | yes |
| Mariana Gomes | 4 | 2026-03-09 | 185 | 11 | 16.8 | yes |
| ... | | | | | | |
| Diego Pereira | 3 | 2026-07-26 | 46 | 31 | 1.5 | no |

- **53 customers have a rhythm** (3 or more purchase days). **32 of them
  went quiet**, and three of those are in the top 8 of
  [analysis 01](../01-pareto-customers/). Many of the rest are one-time
  buyers who spread a single order over a few days and never came back.
- Diego Pereira shows why the rule is relative: 46 days silent looks bad,
  but they buy roughly every 31 days, so they are not flagged.

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

**A frase que eu dei pro dono:** *"Três dos seus oito maiores clientes
pararam. Não é 'diminuíram': cada um comprava a cada poucos dias, e está há
semanas sem aparecer. Se você mandar mensagem pra três pessoas essa
semana, são essas três."*

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

- **53 clientes têm ritmo** (3 dias de compra ou mais). **32 deles
  sumiram**, e três desses estão no top 8 da
  [análise 01](../01-pareto-customers/). Boa parte do resto é gente que
  comprou uma vez só, espalhada em alguns dias, e não voltou.
- Diego Pereira mostra por que a regra é relativa: 46 dias sem comprar
  parece ruim, mas o ritmo é de um pedido a cada 31 dias, então não entra na lista.

### O que saiu disso

- Os nomes marcados vão pro dono como lista curta, não como relatório:
  nome, último pedido, o que costumava comprar. A mensagem é pessoal, não
  campanha.
- O corte (dobro do intervalo normal) é escolha, não lei. Um negócio mais
  rígido usaria 1,5; a consulta tem um número só pra trocar.
