-- Question: which customers are going quiet?
--
-- Why it matters: "has not bought in 30 days" means nothing on its own.
-- Someone who buys every week and vanished for a month is a problem;
-- someone who buys twice a year is right on schedule. The alarm has to be
-- relative to each customer's own rhythm, or the follow-up list is noise.
--
-- Method:
--   1. one row per day a customer bought something (gifts excluded).
--      Not per order: an order can stay open and collect items for weeks,
--      so "order" would hide purchases. The day is the buying decision.
--   2. for each purchase day, how many days since that customer's previous
--      one (lag() looks at the row above, inside the customer's partition)
--   3. collapse to one row per customer: purchases, last one, usual gap
--      (customers with fewer than 3 purchase days have no rhythm to compare)
--   4. "today" is the last day in the data, so the result is reproducible
--   5. flag whoever has been silent for more than twice their usual gap
--      AND for at least 14 days. The floor came from running this on real
--      data: when regulars buy every 2 or 3 days, "twice the gap" flags a
--      long weekend. The whole list is returned so the chart shows the
--      healthy ones too.

with purchase_days as (
  select distinct
    c.id         as customer_id,
    c.name       as customer,
    i.created_at as purchase_day
  from order_items i
  join orders    o on o.id = i.order_id
  join customers c on c.id = o.customer_id
  where i.status <> 'bonus'                     -- a gift is not a purchase
),
gaps as (
  select
    customer_id,
    customer,
    purchase_day,
    purchase_day - lag(purchase_day) over (partition by customer_id
                                           order by purchase_day) as days_since_previous
  from purchase_days
),
rhythm as (
  select
    customer_id,
    customer,
    count(*)                           as purchases,
    max(purchase_day)                  as last_purchase,
    round(avg(days_since_previous), 0) as usual_gap_days   -- the first day has no gap; avg ignores null
  from gaps
  group by 1, 2
  having count(*) >= 3
),
today as (
  select max(created_at) as today from order_items
)
select
  r.customer,
  r.purchases,
  r.last_purchase,
  t.today - r.last_purchase                                  as days_silent,
  r.usual_gap_days,
  round((t.today - r.last_purchase) / r.usual_gap_days, 1)   as times_usual_gap,
  (t.today - r.last_purchase) > 2 * r.usual_gap_days
    and t.today - r.last_purchase >= 14                      as going_quiet
from rhythm r
cross join today t
order by times_usual_gap desc;
