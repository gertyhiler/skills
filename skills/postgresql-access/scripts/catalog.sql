WITH tables AS (
  SELECT
    n.nspname AS schema_name,
    c.relname AS table_name,
    c.relkind AS relkind
  FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
  WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
)
SELECT
  t.schema_name,
  t.table_name,
  CASE t.relkind
    WHEN 'r' THEN 'table'
    WHEN 'p' THEN 'partitioned table'
    WHEN 'v' THEN 'view'
    WHEN 'm' THEN 'materialized view'
    WHEN 'f' THEN 'foreign table'
    ELSE t.relkind::text
  END AS object_type,
  a.attname AS column_name,
  pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
  a.attnotnull AS not_null
FROM tables t
JOIN pg_class c ON c.relname = t.table_name
JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.schema_name
JOIN pg_attribute a ON a.attrelid = c.oid
WHERE a.attnum > 0
  AND NOT a.attisdropped
ORDER BY t.schema_name, t.table_name, a.attnum
