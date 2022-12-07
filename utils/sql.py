#-------------- RESOURCE MONITORING ------------------
STREAMLIT_CREDITS_USED = '''
select
sum(credits_used_cloud_services)
from query_history
where query_tag = 'StreamlitQuery';'''

SNOWFLAKE_ACCOUNT_PARAMS = '''
select current_database() 
,current_schema()
,current_role()
,current_session()
,current_user()
,current_warehouse()
,current_region()
,current_time();'''

METERING_HISTORY = ''' 
select 
name
,credits_used 
from metering_history;'''

METERING_TOP_10 = '''
select top 10 
name 
,sum(credits_used)
from metering_history 
group by name
order by sum(credits_used) desc; '''

WH_USAGE_LAST_7_DAYS = '''
-- WAREHOUSE USAGE OVER LAST 7 DAYS
WITH usage_detail_rows AS
(
SELECT
convert_timezone('America/Los_Angeles',current_timestamp()) AS local_cts,
convert_timezone('America/Los_Angeles',start_time) AS local_start_time,
CASE WHEN local_start_time BETWEEN date_trunc('day', dateadd('day',-6,local_cts)) AND local_cts THEN credits_used_compute + credits_used_cloud_services ELSE 0 END AS credits_used_last_period,
CASE WHEN local_start_time BETWEEN date_trunc('day', dateadd('day',-6,local_cts)) AND local_cts THEN 0 ELSE credits_used_compute + credits_used_cloud_services END AS credits_used_prior_period
    FROM snowflake.account_usage.warehouse_metering_history
WHERE local_start_time BETWEEN date_trunc('day', dateadd('day',-13,local_cts)) AND local_cts
    )
SELECT 
ROUND(SUM(credits_used_last_period),0) AS credits_used_last_period,
ROUND(SUM(credits_used_prior_period),0) AS credits_used_prior_period,
100*(SUM(credits_used_last_period) - nullif(SUM(credits_used_prior_period),0)) / (SUM(credits_used_prior_period) ) AS pct_change
FROM usage_detail_rows 
;
'''

#-------------- RBAC SUMMARY ------------------
ALL_RBAC_ROLES = '''
select 
CREATED_ON
,NAME 
,COMMENT
,OWNER 
from roles;'''

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
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY 
GROUP BY user_name
ORDER BY avg(partitions_total) DESC
;
'''


if __name__ == "__main__":
    pass