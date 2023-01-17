select table_name
       ,table_schema
       ,'IS EMPTY' as empty
       ,last_altered
from snowflake.account_usage.tables
where row_count = 0
order by table_schema, table_name;