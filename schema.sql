-- Simplified schema of a perfume decant business (PostgreSQL).
--
-- A "decant" is a small vial (3, 5, 10 ml) filled from a full bottle.
-- Each row in `bottles` is one physical bottle; sales draw millilitres
-- from it. An order groups several items for one customer until it ships.
--
-- The production schema has more tables (stock of vials, shipping
-- materials, audit trail, roles). This is the part the analyses need.

create table customers (
  id          integer primary key,
  name        text not null,
  city        text,
  state       text,
  created_at  date not null
);

create table bottles (
  id            integer primary key,
  name          text not null,
  brand         text,
  volume_ml     integer not null,
  cost_total    numeric(10,2) not null,   -- what the business paid for the bottle
  price_per_ml  numeric(10,2) not null,   -- selling price per ml
  created_at    date not null
);

create table orders (
  id           integer primary key,
  customer_id  integer not null references customers(id),
  created_at   date not null,
  shipped_at   date
);

create table order_items (
  id            integer primary key,
  order_id      integer not null references orders(id),
  bottle_id     integer not null references bottles(id),
  ml            integer not null,
  price         numeric(10,2) not null,   -- what the customer paid for this item
  cost          numeric(10,2) not null,   -- perfume + vial + label, stamped at sale time
  status        text not null check (status in ('paid', 'pending', 'bonus')),
  created_at    date not null
);

-- Business rules that the analyses respect:
--   * status = 'bonus' is a gift, not revenue. Its cost still counts.
--   * one order can have many items; "orders" is count(distinct order_id).
--   * cost is stamped at sale time, so a later bottle price change does
--     not rewrite the profit of what was already sold.
