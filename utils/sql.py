#-------------------- SIDEBAR ------------------------

SNOWFLAKE_ACCOUNT_PARAMS = '''select current_database() 
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

#-------------- RESOURCE MONITORING ------------------

SNOWFLAKE_SESSION_VARIABLES = '''select 
current_database() 
,current_schema()
,current_role()
,current_session()
,current_user()
,current_warehouse()
,current_region()
,current_time();'''

METERING_HISTORY = ''' select 
name
,credits_used 
from metering_history;'''

METERING_TOP_10 = '''select top 10 
name 
,sum(credits_used) 
from metering_history 
group by name; '''

#-------------- RBAC SUMMARY ------------------

#-------------- QUERY MONITORING ------------------
USER_LIST = ''' 
SELECT distinct(user_name)
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
;
    '''

USER_QUERY_HISTORY = '''
SELECT user_name
    , avg(percentage_scanned_from_cache)
    , avg(partitions_scanned)
    , avg(partitions_total)
    , avg(execution_time)
    , avg(query_load_percent)
    , avg(credits_used_cloud_services)
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY 
GROUP BY user_name
ORDER BY avg(partitions_total) DESC
;
'''


if __name__ == "__main__":
    pass