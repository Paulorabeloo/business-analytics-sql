-- Question: how many customers account for half of the revenue?
--
-- Why it matters: a small business that depends on a handful of buyers
-- should treat them differently (early access to launches, free shipping
-- now and then, a message on their birthday) and notice fast when one
-- of them stops buying.
--
-- Method:
--   1. one row per sold item, with the customer attached (gifts excluded)
--   2. collapse to one row per customer: orders, items, total spent
--   3. rank by spend and add each customer's share and the running share
--   4. the first row whose running share reaches 50% answers the question

with sold as (
  select
    c.id   as customer_id,
    c.name as customer,
    o.id   as order_id,
    i.price,
    i.created_at
  from order_items i
  join orders    o on o.id = i.order_id
  join customers c on c.id = o.customer_id
  where i.status <> 'bonus'                     -- gifts are not revenue
),
per_customer as (
  select
    customer_id,
    customer,
    count(distinct order_id) as orders,          -- an order with 3 items is still one order
    count(*)                 as items,
    round(sum(price), 2)     as spent,
    max(created_at)          as last_purchase
  from sold
  group by 1, 2
)
select
  row_number() over (order by spent desc)                            as position,
  customer,
  orders,
  items,
  spent,
  round(100.0 * spent / sum(spent) over (), 1)                       as share_pct,
  round(100.0 * sum(spent) over (order by spent desc
                                 rows unbounded preceding)
             / sum(spent) over (), 1)                                as running_pct,
  last_purchase
from per_customer
order by spent desc;
