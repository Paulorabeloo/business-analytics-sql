-- Question: of the customers who bought once, how many came back?
--
-- Why it matters: the repeat rate says whether the business is a bucket
-- with a hole in it. Acquiring a customer costs money; the second purchase
-- is where that money is paid back.
--
-- The catch: "came back" depends on the unit. An order can stay open and
-- collect items for weeks (the customer waits to ship everything at once),
-- so counting orders undercounts buying decisions. The same customer can
-- be "bought once" by orders and "bought five times" by purchase days.
-- This query computes both so the gap is visible, then buckets customers
-- by how many times they bought.
--
-- Method:
--   1. per customer: distinct orders and distinct purchase days (gifts out)
--   2. the same customers under each unit, side by side (union all)
--   3. buckets (1, 2, 3 to 5, 6+) per unit; the repeat rate is everyone
--      outside the "1" bucket, computed with a window so each row carries it

with per_customer as (
  select
    o.customer_id,
    count(distinct o.id)          as orders,
    count(distinct i.created_at)  as purchase_days
  from order_items i
  join orders o on o.id = i.order_id
  where i.status <> 'bonus'
  group by 1
),
by_unit as (
  select 'orders' as unit, customer_id, orders as times from per_customer
  union all
  select 'purchase days', customer_id, purchase_days from per_customer
),
buckets as (
  select
    unit,
    case
      when times = 1 then '1'
      when times = 2 then '2'
      when times <= 5 then '3 to 5'
      else '6+'
    end as bucket,
    customer_id
  from by_unit
)
select
  unit,
  bucket,
  count(*)                                                            as customers,
  round(100.0 * count(*) / sum(count(*)) over (partition by unit), 1) as pct_of_customers,
  round(100.0 * sum(count(*)) filter (where bucket <> '1')
                  over (partition by unit)
              / sum(count(*)) over (partition by unit), 1)            as repeat_rate_pct
from buckets
group by unit, bucket
order by unit, bucket;
