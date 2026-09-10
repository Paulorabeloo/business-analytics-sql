# 01 · How many customers account for half of the revenue?

**The sentence I gave the owner:** *"Seven customers pay for half of everything
we have ever sold. The other ninety split the rest. Losing one of those seven
hurts more than losing ten of the others."*

![Pareto chart](chart.png)

## Why this question

A small business feels like it has "many customers". The data usually says
something else: a few people carry it. Knowing who they are changes what
you do on Monday: who hears about a launch first, who gets free shipping
once in a while, who gets a message on their birthday, and who you call
when they go quiet.

## How it is answered

[`query.sql`](query.sql), in four steps:

1. **One row per sold item** with the customer attached. Gifts (`status =
   'bonus'`) are excluded: they are a cost, not revenue.
2. **Collapse to one row per customer**: orders, items, total spent.
   `count(distinct order_id)` matters here; an order with three items is
   one order, not three.
3. **Rank by spend** and compute two shares with window functions: the
   customer's own share (`sum() over ()`) and the running share
   (`sum() over (order by spent desc rows unbounded preceding)`).
4. **Read the first row where the running share reaches 50%.** Its position
   is the answer.

The chart is the same table drawn: bars are each customer's spend, the line
is the running share, and the dashed line marks 50%.

## Result on the synthetic data

| position | customer | orders | spent | share | running |
|---|---|---|---|---|---|
| 1 | Helena Correia | 14 | 8,049.58 | 8.7% | 8.7% |
| 2 | Bruno Nunes | 14 | 8,049.26 | 8.7% | 17.4% |
| 3 | Fernanda Cardoso | 14 | 7,542.88 | 8.2% | 25.6% |
| ... | | | | | |
| 7 | Igor Santos | 6 | 4,261.27 | 4.6% | 50.2% |
| 33 | | | | | 80.5% |
| 97 | | | | | 100% |

- **7 of 97 customers = half of the revenue** (R$ 92.4k in total).
- **33 customers = 80%.** The remaining 64 share the last 20%.

The production numbers are different, but the shape is the same: half of
the revenue comes from roughly a tenth of the customers.

## What came out of it

- The seven names became a list the owner keeps. Two of them had not bought
  in over a month; they got a message the same week.
- The same query, filtered by period, went into the management system's
  reports page, so the owner can see "where the money comes from" for any
  month without asking.

## Reproduce

```bash
python scripts/generate_data.py
python scripts/run_analysis.py 01-pareto-customers
```
