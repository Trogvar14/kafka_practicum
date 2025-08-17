CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS products(
  product_id text PRIMARY KEY,
  name text,
  description text,
  category text,
  brand text,
  price numeric,
  currency text
);

CREATE INDEX IF NOT EXISTS idx_products_name_trgm ON products USING gin (name gin_trgm_ops);

CREATE TABLE IF NOT EXISTS client_queries(
  id bigserial PRIMARY KEY,
  ts timestamptz DEFAULT now(),
  user_id text,
  query text
);

CREATE TABLE IF NOT EXISTS recommendations(
  id bigserial PRIMARY KEY,
  ts timestamptz DEFAULT now(),
  user_id text,
  items jsonb
);
