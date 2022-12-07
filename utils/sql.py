TEST_QUERY = '''select current_database() 
,current_schema()
,current_role()
,current_session()
,current_user()
,current_warehouse()
,current_region()
,current_time();'''

STREAMLIT_CREDITS_USED = '''select
sum(credits_used_cloud_services)
from query_history
where query_tag = 'StreamlitQuery';'''

SNOWFLAKE_SESSION_VARIABLES = '''select current_database() 
,current_schema()
,current_role()
,current_session()
,current_user()
,current_warehouse()
,current_region()
,current_time();'''

USER_LIST = ''' SELECT distinct(user_name)
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY'''

USER_QUERY_HISTORY =  '''SELECT user_name
    , avg(percentage_scanned_from_cache)
    , avg(partitions_scanned)
    , avg(partitions_total)
    , avg(execution_time)
    , avg(query_load_percent)
    , avg(credits_used_cloud_services)
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY 
    GROUP BY user_name
    ORDER BY avg(partitions_total) DESC;
    '''

if __name__ == "__main__":
    pass