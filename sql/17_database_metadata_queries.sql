USE AlbertaProductionDB;
GO
/* READ-ONLY. Database description for Claude.
   Run each query, then right-click the results grid -> "Save Results As..." -> CSV,
   into folder:  C:\Folder D\Data Projects\Alberta Production Data_2026\db_metadata
   File names: 1_tables.csv, 2_columns.csv, 3_views.csv, 4_view_columns.csv */

-- 1) Tables: row counts and column counts
SELECT s.name AS Schema_Name, t.name AS Table_Name,
       SUM(p.rows) AS Row_Count,
       (SELECT COUNT(*) FROM sys.columns c WHERE c.object_id = t.object_id) AS Column_Count,
       t.create_date, t.modify_date
FROM sys.tables t
JOIN sys.schemas s ON s.schema_id = t.schema_id
JOIN sys.partitions p ON p.object_id = t.object_id AND p.index_id IN (0, 1)
GROUP BY s.name, t.name, t.object_id, t.create_date, t.modify_date
ORDER BY t.name;

-- 2) Columns of all tables
SELECT c.TABLE_NAME, c.ORDINAL_POSITION, c.COLUMN_NAME, c.DATA_TYPE,
       c.CHARACTER_MAXIMUM_LENGTH, c.NUMERIC_PRECISION, c.NUMERIC_SCALE, c.IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS c
JOIN INFORMATION_SCHEMA.TABLES t
  ON t.TABLE_NAME = c.TABLE_NAME AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
WHERE t.TABLE_TYPE = 'BASE TABLE'
ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION;

-- 3) Views and their SQL definitions
SELECT v.name AS View_Name, v.create_date, v.modify_date,
       REPLACE(REPLACE(m.definition, CHAR(13), ' '), CHAR(10), ' ') AS View_Definition
FROM sys.views v
JOIN sys.sql_modules m ON m.object_id = v.object_id
ORDER BY v.name;

-- 4) Columns of all views
SELECT c.TABLE_NAME AS View_Name, c.ORDINAL_POSITION, c.COLUMN_NAME, c.DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS c
JOIN INFORMATION_SCHEMA.VIEWS v
  ON v.TABLE_NAME = c.TABLE_NAME AND v.TABLE_SCHEMA = c.TABLE_SCHEMA
ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION;
