-- Question: which customers are going quiet?
--
-- Why it matters: "has not bought in 30 days" means nothing on its own.
-- Someone who buys every week and vanished for a month is a problem;
-- someone who buys twice a year is right on schedule. The alarm has to be
-- relative to each customer's own rhythm, or the follow-up list is noise.
--
-- Method:
--   1. one row per order that had at least one sold item (gifts excluded)
--   2. for each order, how many days since that customer's previous order
--      (lag() looks at the row above, inside the customer's own partition)
--   3. collapse to one row per customer: orders, last order, usual gap
--      (customers with fewer than 3 orders have no rhythm to compare with)
--   4. "today" is the last day in the data, so the result is reproducible
--   5. flag whoever has been silent for more than twice their usual gap
--      (the whole list is returned so the chart can show the healthy ones too)

with orders_sold as (
  select
    c.id         as customer_id,
    c.name       as customer,
    o.id         as order_id,
    o.created_at as order_date
  from orders o
  join customers   c on c.id = o.customer_id
  join order_items i on i.order_id = o.id
  where i.status <> 'bonus'                     -- an order with only gifts is not a purchase
  group by 1, 2, 3, 4                           -- one row per order, not per item
),
gaps as (
  select
    customer_id,
    customer,
    order_date,
    order_date - lag(order_date) over (partition by customer_id
                                       order by order_date) as days_since_previous
  from orders_sold
),
rhythm as (
  select
    customer_id,
    customer,
    count(*)                           as orders,
    max(order_date)                    as last_order,
    round(avg(days_since_previous), 0) as usual_gap_days   -- the first order has no gap; avg ignores null
  from gaps
  group by 1, 2
  having count(*) >= 3
),
today as (
  select max(created_at) as today from orders
)
select
  r.customer,
  r.orders,
  r.last_order,
  t.today - r.last_order                                  as days_silent,
  r.usual_gap_days,
  round((t.today - r.last_order) / r.usual_gap_days, 1)   as times_usual_gap,
  (t.today - r.last_order) > 2 * r.usual_gap_days         as going_quiet
from rhythm r
cross join today t
order by times_usual_gap desc;
