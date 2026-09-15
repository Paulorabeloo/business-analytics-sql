-- Question: how much money is sitting in bottles that have not sold yet?
--
-- Why it matters: every bottle is cash paid up front that only comes back
-- millilitre by millilitre. A shelf full of half-sold bottles looks like
-- stock; to the bank account it is money that left and has not returned.
-- The owner needs the list by bottle, biggest amount first, and a flag
-- for the ones that stopped moving.
--
-- Method:
--   1. per bottle: ml sold (gifts consume perfume too, so they count here),
--      last sale date. left join keeps bottles that never sold anything.
--   2. ml left = volume - sold (never below zero); cost sitting = ml left
--      at the cost per ml the business paid; revenue potential = ml left
--      at the selling price
--   3. "today" is the last day in the data; days since the last sale, or
--      since the bottle was registered if it never sold
--   4. share of all the money sitting, so the top rows can be read as
--      "these five bottles are 40% of the problem"
--   5. stalled = no sale in 60 days

with per_bottle as (
  select
    b.id,
    b.name,
    b.brand,
    b.volume_ml,
    b.cost_total,
    b.price_per_ml,
    b.created_at,
    coalesce(sum(i.ml), 0)  as ml_sold,
    max(i.created_at)       as last_sale
  from bottles b
  left join order_items i on i.bottle_id = b.id
  group by 1, 2, 3, 4, 5, 6, 7
),
today as (
  select max(created_at) as today from order_items
),
sitting as (
  select
    p.*,
    greatest(p.volume_ml - p.ml_sold, 0)                                  as ml_left,
    round(greatest(p.volume_ml - p.ml_sold, 0) * p.cost_total / p.volume_ml, 2) as cost_sitting,
    round(greatest(p.volume_ml - p.ml_sold, 0) * p.price_per_ml, 2)       as revenue_potential,
    t.today - coalesce(p.last_sale, p.created_at)                         as days_since_sale
  from per_bottle p
  cross join today t
)
select
  name,
  brand,
  volume_ml,
  ml_sold,
  ml_left,
  round(100.0 * ml_sold / volume_ml, 1)                       as pct_sold,
  cost_sitting,
  round(100.0 * cost_sitting / sum(cost_sitting) over (), 1)  as pct_of_total,
  revenue_potential,
  last_sale,
  days_since_sale,
  days_since_sale >= 60                                       as stalled
from sitting
where ml_left > 0
order by cost_sitting desc;
