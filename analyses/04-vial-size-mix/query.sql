-- Question: which vial size sells, and which one makes the money?
--
-- Why it matters: vials, labels and boxes are bought per size. The owner
-- restocks by feel ("5 ml goes fast"). This turns the feel into a number,
-- and separates two things that are easy to confuse: the size that moves
-- the most units and the size that brings the most revenue and profit.
--
-- Method:
--   1. one row per sold item (gifts out), with price and stamped cost
--   2. group by size: items, revenue, gross profit
--   3. two shares with a window over the whole table: share of items and
--      share of revenue. If they disagree, the "best seller" is not the
--      size that pays the bills.
--   4. margin per size, so a size that sells a lot at a thin margin shows

with sold as (
  select
    i.ml,
    i.price,
    i.cost                                       -- perfume + vial + label, stamped at sale time
  from order_items i
  where i.status <> 'bonus'
)
select
  ml,
  count(*)                                                        as items,
  round(100.0 * count(*) / sum(count(*)) over (), 1)              as pct_items,
  round(sum(price), 2)                                            as revenue,
  round(100.0 * sum(price) / sum(sum(price)) over (), 1)          as pct_revenue,
  round(sum(price - cost), 2)                                     as gross_profit,
  round(100.0 * sum(price - cost) / sum(price), 1)                as margin_pct,
  round(avg(price), 2)                                            as avg_ticket
from sold
group by ml
order by ml;
