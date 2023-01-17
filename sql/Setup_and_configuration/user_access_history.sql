select query_id, 
convert_timezone('Europe/London', query_start_time) as "query_start_time", 
direct_objects_accessed,
base_objects_accessed,
objects_modified
from snowflake.account_usage.access_history
where user_name = '{user}'
order by query_start_time desc;