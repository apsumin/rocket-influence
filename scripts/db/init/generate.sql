SELECT generate_simple_create_table_sql('public', 'youtube');

CREATE OR REPLACE FUNCTION generate_create_table_sql(
  target_schema TEXT,
  target_table TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY INVOKER AS $$
DECLARE
  create_table_sql TEXT;
  column_sql TEXT;
  constraint_sql TEXT;
  index_sql TEXT;
  trigger_sql TEXT;
  comment_sql TEXT;
  table_comment TEXT;
  column_record RECORD;
  constraint_record RECORD;
  index_record RECORD;
  trigger_record RECORD;
  column_comment_record RECORD;
BEGIN
  -- Initialize the CREATE TABLE statement
  create_table_sql := format('CREATE TABLE %I.%I (', target_schema, target_table);
  
  -- Get column definitions
  column_sql := '';
  FOR column_record IN 
    SELECT 
      a.attname AS column_name,
      pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
      CASE WHEN a.attnotnull THEN 'NOT NULL' ELSE 'NULL' END AS nullable,
      CASE 
        WHEN a.atthasdef THEN pg_get_expr(d.adbin, d.adrelid)
        ELSE NULL
      END AS default_value
    FROM 
      pg_catalog.pg_attribute a
    LEFT JOIN 
      pg_catalog.pg_attrdef d ON (a.attrelid = d.adrelid AND a.attnum = d.adnum)
    WHERE 
      a.attrelid = (target_schema || '.' || target_table)::regclass
      AND a.attnum > 0
      AND NOT a.attisdropped
    ORDER BY 
      a.attnum
  LOOP
    IF column_sql <> '' THEN
      column_sql := column_sql || E',\n  ';
    END IF;
    
    column_sql := column_sql || format('%I %s %s', 
      column_record.column_name,
      column_record.data_type,
      column_record.nullable
    );
    
    IF column_record.default_value IS NOT NULL THEN
      column_sql := column_sql || ' DEFAULT ' || column_record.default_value;
    END IF;
  END LOOP;
  
  -- Add column definitions to CREATE TABLE statement
  create_table_sql := create_table_sql || E'\n  ' || column_sql;
  
  -- Get primary key and other constraints
  constraint_sql := '';
  FOR constraint_record IN
    SELECT
      con.conname AS constraint_name,
      con.contype AS constraint_type,
      pg_get_constraintdef(con.oid) AS constraint_definition
    FROM
      pg_constraint con
      JOIN pg_class rel ON rel.oid = con.conrelid
      JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
    WHERE
      nsp.nspname = target_schema
      AND rel.relname = target_table
  LOOP
    constraint_sql := constraint_sql || E',\n  ';
    
    -- For primary keys and unique constraints, we get the full definition
    IF constraint_record.constraint_type IN ('p', 'u') THEN
      constraint_sql := constraint_sql || 'CONSTRAINT ' || quote_ident(constraint_record.constraint_name) || ' ' || 
                        substring(constraint_record.constraint_definition FROM position('(' in constraint_record.constraint_definition));
    -- For foreign keys, we get the full definition
    ELSIF constraint_record.constraint_type = 'f' THEN
      constraint_sql := constraint_sql || 'CONSTRAINT ' || quote_ident(constraint_record.constraint_name) || ' ' ||
                        constraint_record.constraint_definition;
    -- For check constraints
    ELSIF constraint_record.constraint_type = 'c' THEN
      constraint_sql := constraint_sql || 'CONSTRAINT ' || quote_ident(constraint_record.constraint_name) || ' ' ||
                        constraint_record.constraint_definition;
    END IF;
  END LOOP;
  
  -- Add constraints to CREATE TABLE statement
  IF constraint_sql <> '' THEN
    create_table_sql := create_table_sql || constraint_sql;
  END IF;
  
  -- Close the CREATE TABLE statement
  create_table_sql := create_table_sql || E'\n);\n';
  
  -- Get table comment if any
  SELECT pg_description.description INTO table_comment
  FROM pg_description
  JOIN pg_class ON pg_description.objoid = pg_class.oid
  JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid
  WHERE pg_namespace.nspname = target_schema
    AND pg_class.relname = target_table
    AND pg_description.objsubid = 0;
  
  IF table_comment IS NOT NULL THEN
    comment_sql := format(E'COMMENT ON TABLE %I.%I IS %L;\n', 
                        target_schema, target_table, table_comment);
    create_table_sql := create_table_sql || comment_sql;
  END IF;
  
  -- Get column comments
  FOR column_comment_record IN
    SELECT
      cols.column_name,
      pg_description.description
    FROM
      information_schema.columns cols
    JOIN
      pg_class ON cols.table_name = pg_class.relname
    JOIN
      pg_namespace ON cols.table_schema = pg_namespace.nspname AND pg_class.relnamespace = pg_namespace.oid
    JOIN
      pg_attribute ON pg_attribute.attrelid = pg_class.oid AND pg_attribute.attname = cols.column_name
    JOIN
      pg_description ON pg_description.objoid = pg_class.oid AND pg_description.objsubid = pg_attribute.attnum
    WHERE
      cols.table_schema = target_schema
      AND cols.table_name = target_table
  LOOP
    comment_sql := format(E'COMMENT ON COLUMN %I.%I.%I IS %L;\n',
                        target_schema, target_table, column_comment_record.column_name, column_comment_record.description);
    create_table_sql := create_table_sql || comment_sql;
  END LOOP;
  
  -- Get index definitions (excluding those created for constraints)
  FOR index_record IN
    SELECT
      indexname,
      pg_get_indexdef(indexrelid) AS indexdef
    FROM
      pg_indexes
    WHERE
      schemaname = target_schema
      AND tablename = target_table
      AND indexname NOT IN (
        SELECT conname FROM pg_constraint
        JOIN pg_class ON pg_constraint.conrelid = pg_class.oid
        JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid
        WHERE nspname = target_schema AND relname = target_table
      )
  LOOP
    index_sql := index_record.indexdef || E';\n';
    create_table_sql := create_table_sql || index_sql;
  END LOOP;
  
  -- Get trigger definitions
  FOR trigger_record IN
    SELECT
      trigger_name,
      pg_get_triggerdef(t.oid) AS trigger_definition
    FROM
      information_schema.triggers
    JOIN
      pg_trigger t ON trigger_name = t.tgname
    JOIN
      pg_class c ON t.tgrelid = c.oid
    JOIN
      pg_namespace n ON c.relnamespace = n.oid
    WHERE
      trigger_schema = target_schema
      AND event_object_table = target_table
      AND n.nspname = target_schema
      AND c.relname = target_table
  LOOP
    trigger_sql := trigger_record.trigger_definition || E';\n';
    create_table_sql := create_table_sql || trigger_sql;
  END LOOP;
  
  -- Add row level security if enabled
  PERFORM 1 FROM pg_class c
  JOIN pg_namespace n ON c.relnamespace = n.oid
  WHERE n.nspname = target_schema
    AND c.relname = target_table
    AND c.relrowsecurity = true;
    
  IF FOUND THEN
    create_table_sql := create_table_sql || format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY;\n', 
                                                target_schema, target_table);
  END IF;
  
  RETURN create_table_sql;
END;
$$;