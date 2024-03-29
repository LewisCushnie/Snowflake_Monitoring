#-------------- ACCOUNT LEVEL DETAILS -------------

SNOWFLAKE_ACCOUNT_PARAMS = '''
select 
current_database() as DATABASE
,current_schema() as SHEMA
,current_role() as CURRENT_ROLE
,current_session() as SESSION_ID
,current_user() as CURRENT_USER
,current_warehouse() as WAREHOUSE
,current_region() as ACCOUNT_REGION
,current_time() as REGION_TIME
;'''

BUSINESS_DOMAINS = '''
select DOMAIN_NAME from admin_db.deploy.business_domains;
'''

#-------------- BEST PRACTICE MONITORING -------------

EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT = '''
select table_name
       ,table_schema
       ,'IS EMPTY' as empty
       ,last_altered
from snowflake.account_usage.tables
where row_count = 0
order by table_schema, table_name;
'''

def UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT(days):
    query = f'''
    select
        table_name
        ,table_schema
        ,datediff(day, last_altered, current_timestamp()) as days_unused
        ,table_type
        ,last_altered
    from snowflake.account_usage.tables
    where last_altered < dateadd( 'DAY', -{days}, current_timestamp() ) 
    order by days_unused desc;
    '''
    return query

TABLE_AND_VIEW_BREAKDOWN = '''
select
    SUM(CASE WHEN TABLE_TYPE = 'VIEW' THEN 1 ELSE 0 END) as view_count
    ,SUM(CASE WHEN TABLE_TYPE = 'MATERIALIZED VIEW' THEN 1 ELSE 0 END) as materialized_view_count
    ,SUM(CASE WHEN TABLE_TYPE = 'BASE TABLE' THEN 1 ELSE 0 END) as base_table_count
    ,SUM(CASE WHEN TABLE_TYPE = 'EXTERNAL TABLE' THEN 1 ELSE 0 END) as external_table_count
from SNOWFLAKE.ACCOUNT_USAGE.TABLES;
'''

WAREHOUSE_DETAILS = '''
show warehouses;
'''

def WAREHOUSE_UTILIZATION_LAST_N_DAYS(days):
    query = f'''
    WITH availability_time AS 
    (SELECT
    --TO_CHAR(convert_timezone('UTC', start_time::timestamp_ntz), 'MM/DD/YYYY HH24') as hour
    warehouse_name
    ,ROUND(SUM(credits_used_compute),0) AS compute_credits_used
    ,compute_credits_used * 60 * 60 AS compute_availability_sec
    FROM snowflake.account_usage.warehouse_metering_history
    WHERE start_time BETWEEN date_trunc('day', dateadd('day',-{days},convert_timezone('UTC',current_timestamp()))) AND current_timestamp()
    --AND warehouse_name = 'AIRFLOW_WH'--:warehouse_name
    GROUP BY 1
    ),

    query_time AS
    (
    SELECT
    --to_char(convert_timezone('UTC', end_time::timestamp_ntz), 'MM/DD/YYYY HH24') as hour,
        warehouse_name,
    COUNT(*), ROUND(AVG(total_elapsed_time/1000),2) as avg_query_time
    ,ROUND(MEDIAN(total_elapsed_time/1000),2) as "Median Query Time"
    , ROUND(SUM(execution_time/1000),2) as total_exec_time_sec
    , ROUND(MEDIAN(execution_time/1000),2) as "Median Execution Time"
        , MEDIAN(query_load_percent) AS median_query_load_pct
    FROM SNOWFLAKE.account_usage.query_history
    WHERE start_time BETWEEN date_trunc('day', dateadd('day',-{days},convert_timezone('UTC',current_timestamp()))) AND current_timestamp()
    GROUP BY warehouse_name
    )

    --ORDER BY 1;
    SELECT at.warehouse_name--, at.hour
    , at.compute_credits_used, at.compute_availability_sec, total_exec_time_sec,
    ROUND((total_exec_time_sec / nullif(at.compute_availability_sec,0 )) * 100,1) AS pct_utilization,
    median_query_load_pct, median_query_load_pct / 64 as median_query_load_pct_3xl
    FROM availability_time at JOIN query_time qt ON at.warehouse_name = qt.warehouse_name
    --and query_time qt ON at.hour = qt.hour
    ORDER BY pct_utilization DESC
    ;
    '''
    return query

def WH_UTILIZATION_LAST_48_HOURS(wh_name):
    query = f'''
    WITH availability_time AS 
    (SELECT
    TO_CHAR(convert_timezone('UTC', start_time::timestamp_ntz), 'MM/DD/YYYY HH24') as hour
    ,ROUND(SUM(credits_used_compute),2) AS compute_credits_used
    ,compute_credits_used * 60 * 60 AS compute_availability_sec
    FROM snowflake.account_usage.warehouse_metering_history
    WHERE start_time BETWEEN date_trunc('day', dateadd('day',-7,convert_timezone('UTC',current_timestamp()))) AND current_timestamp()
    AND warehouse_name = '{wh_name}'--:warehouse_name
    GROUP BY 1
    ),

    query_time AS
    (
    SELECT
    to_char(convert_timezone('UTC', end_time::timestamp_ntz), 'MM/DD/YYYY HH24') as hour, 
    COUNT(*), ROUND(AVG(total_elapsed_time/1000),2) as avg_query_time
    ,ROUND(MEDIAN(total_elapsed_time/1000),2) as "Median Query Time"
    , ROUND(SUM(execution_time/1000),2) as total_exec_time_sec
    , ROUND(MEDIAN(execution_time/1000),2) as "Median Execution Time"
        , MEDIAN(query_load_percent) AS median_query_load_pct
    FROM SNOWFLAKE.account_usage.query_history
    WHERE start_time >= dateadd(hour, -24, current_date()) AND bytes_scanned > 0
    AND WAREHOUSE_NAME = '{wh_name}' --:warehouse_name
    GROUP BY hour
    )

    --ORDER BY 1;
    SELECT at.hour, at.compute_credits_used, at.compute_availability_sec, total_exec_time_sec
    ,(total_exec_time_sec / at.compute_availability_sec ) * 100 AS pct_utilization
    FROM availability_time at JOIN
    query_time qt ON at.hour = qt.hour
    order by hour;
    '''
    return query



#-------------- WAREHOUSE MONITORING ------------------
WH_CREDIT_BREAKDOWN = '''
select
name as wh_name
,sum(credits_used_compute) as compute_credits
,sum(credits_used_cloud_services) as cloud_services_credits
,sum(credits_used) as total_credits
,(cloud_services_credits/total_credits)*100 as perc_cloud
,(compute_credits/total_credits)*100 as perc_compute
from snowflake.account_usage.metering_history
group by wh_name;
'''

METERING_TOP_10 = '''
select top 10 
name 
,sum(credits_used) AS CREDITS_USED
from metering_history 
group by name
order by CREDITS_USED desc; '''

STREAMLIT_CREDITS_USED = '''
select
sum(credits_used_cloud_services) as CREDITS_USED_STREAMLIT
from query_history
where query_tag = 'StreamlitQuery';'''

METERING_HISTORY = ''' 
select 
name
,credits_used 
from metering_history;'''

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

COMPUTE_CREDITS_PER_DAY = '''
SELECT
DATE_TRUNC('day', convert_timezone('UTC',start_time))::DATE as "Usage Week"
,ROUND(SUM(credits_used_compute),2)::number(38,2) AS "Compute Credits Used"
,ROUND(SUM(credits_used_compute)*4,2) AS "Cost ($)"
FROM snowflake.organization_usage.warehouse_metering_history
WHERE start_time BETWEEN date_trunc('day', dateadd('day',-365,convert_timezone('UTC',current_timestamp()))) AND current_timestamp()
GROUP BY 1 
ORDER BY 1 desc;
'''

COMPUTE_AVAILABILITY_AND_EXECUTION_TIME = '''
WITH availability_time AS 
(SELECT
TO_CHAR(convert_timezone('UTC', start_time::timestamp_ntz), 'MM/DD/YYYY HH24') as hour
,ROUND(SUM(credits_used_compute),2) AS compute_credits_used
,compute_credits_used * 60 * 60 AS compute_availability_sec
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time BETWEEN date_trunc('day', dateadd('day',-7,convert_timezone('UTC',current_timestamp()))) AND current_timestamp()
AND warehouse_name = 'COMPUTE_WH'--:warehouse_name
GROUP BY 1
),

query_time AS
(
SELECT
to_char(convert_timezone('UTC', end_time::timestamp_ntz), 'MM/DD/YYYY HH24') as hour, 
COUNT(*), ROUND(AVG(total_elapsed_time/1000),2) as avg_query_time
,ROUND(MEDIAN(total_elapsed_time/1000),2) as "Median Query Time"
, ROUND(SUM(execution_time/1000),2) as total_exec_time_sec
, ROUND(MEDIAN(execution_time/1000),2) as "Median Execution Time"
    , MEDIAN(query_load_percent) AS median_query_load_pct
FROM SNOWFLAKE.account_usage.query_history
WHERE start_time >= dateadd(hour, -48, current_date()) AND bytes_scanned > 0
AND WAREHOUSE_NAME = 'COMPUTE_WH' --:warehouse_name
GROUP BY hour
)

--ORDER BY 1;
SELECT at.hour, at.compute_credits_used, at.compute_availability_sec, total_exec_time_sec
,(total_exec_time_sec / at.compute_availability_sec ) * 100 AS pct_utilization
FROM availability_time at JOIN
query_time qt ON at.hour = qt.hour;
'''

#-------------- RBAC SUMMARY ------------------
ALL_RBAC_ROLES = '''
select 
CREATED_ON as "DATE CREATED"
,NAME 
,ASSIGNED_TO_USERS as "ASSIGNED TO USERS"
,GRANTED_TO_ROLES as "GRANTED TO ROLES"
,OWNER 
from roles;'''

#-------------- QUERY MONITORING ------------------
USER_LIST = ''' 
SELECT distinct(user_name)
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
;
    '''

USER_QUERY_HISTORY = '''
SELECT user_name as "Username"
    , avg(percentage_scanned_from_cache)*100 as "Avg Scanned from Cache (%)"
    , avg(partitions_scanned)::float as "Avg Partitions Scanned"
    , avg(execution_time)::float as "Avg Execution Time"
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY 
GROUP BY user_name
ORDER BY avg(partitions_total) DESC
;
'''
LONGEST_QUERIES = '''

SELECT QUERY_ID
    , QUERY_TEXT
    ,(EXECUTION_TIME / 60000)
AS EXEC_TIME,WAREHOUSE_NAME,USER_NAME,EXECUTION_STATUS 
from "SNOWFLAKE"."ACCOUNT_USAGE"."QUERY_HISTORY" where EXECUTION_STATUS = 'SUCCESS' order by EXECUTION_TIME desc;
'''

QUERY_COUNT_BY_TYPE = '''
SELECT 
date_trunc('day', convert_timezone('America/Chicago', start_time::timestamp_ntz)) as "Query Date",
query_type AS "Query Type",
SUM(credits_used_cloud_services) AS "Cloud Services Credits",
count(*) AS "Query Count"
FROM snowflake.account_usage.query_history q 
WHERE start_time >  dateadd('day',-14,convert_timezone('America/Chicago', current_timestamp)) 
AND warehouse_name = 'COMPUTE_WH'
GROUP BY 1,2
ORDER BY 1;
'''

QUERY_CATEGORY = '''
select count(q.query_type) as "Number of Queries",avg(q.total_elapsed_time/1000) as "Avg Total Elapsed Time (s)",
    avg(q.PERCENTAGE_SCANNED_FROM_CACHE*100) as "Avg % Scanned From Cache",
    case
        when query_type like '%CREATE%' or 
            query_type like '%ALTER%' or 
            query_type like '%DROP%' or 
            query_type like '%RENAME%' or 
            query_type like '%TRUNCATE%' or 
            query_type like '%SHOW%' or 
            query_type like '%USE%' or
            query_type like '%DESCRIBE%' or 
            query_type like '%COMMENT%' then 'DDL General'
        when query_type like '%GRANT%' or
            query_type like '%REVOKE%' then 'DCL'
        when query_type like '%SET%' then 'DDL Account Session'
        when query_type = 'SELECT' or
            query_type = 'INSERT' or 
            query_type = 'UPDATE' or 
            query_type = 'DELETE' or 
            query_type = 'MERGE' or 
            query_type = 'CALL' then 'DML General'
        when query_type like  '%PUT%' or
            query_type like '%REMOVE%' or
            query_type like '%LIST%' or
            query_type like  '%GET%' then 'DML File Staging' 
        when query_type like  '%COPY%' then 'DML Data Loading'
        when query_type like  '%COMMIT%' or
             query_type like  '%BEGIN%' then 'TCL'
        else 'Unknown'
        end as "Query Category"
    from snowflake.account_usage.query_history as q
    where q.database_name = 'PROD_DB'
    group by "Query Category"
    order by count(q.query_type) desc;

'''

def LOGIN(user):
    query = f'''
        select name,
        default_role, 
        EXT_AUTHN_DUO as "MFA",
        datediff(day,  to_date(LAST_SUCCESS_LOGIN), to_date(current_date())) as last_login
        from users
        where name = '{user}';

            '''
    return query    

def USER_USAGE(user):
    query = f'''
    select 
    case
        when query_type like '%CREATE%' or 
            query_type like '%ALTER%' or 
            query_type like '%DROP%' or 
            query_type like '%RENAME%' or 
            query_type like '%TRUNCATE%' or 
            query_type like '%SHOW%' or 
            query_type like '%USE%' or
            query_type like '%DESCRIBE%' or 
            query_type like '%COMMENT%' then 'DDL General'
        when query_type like '%GRANT%' or
            query_type like '%REVOKE%' then 'DCL'
        when query_type like '%SET%' then 'DDL Account Session'
        when query_type = 'SELECT' or
            query_type = 'INSERT' or 
            query_type = 'UPDATE' or 
            query_type = 'DELETE' or 
            query_type = 'MERGE' or 
            query_type = 'CALL' then 'DML General'
        when query_type like  '%PUT%' or
            query_type like '%REMOVE%' or
            query_type like '%LIST%' or
            query_type like  '%GET%' then 'DML File Staging' 
        when query_type like  '%COPY%' then 'DML Data Loading'
        when query_type like  '%COMMIT%' or
             query_type like  '%BEGIN%' then 'TCL'
        else 'Unknown'
        end as "Query_Category",
     sum(qh.total_elapsed_time/1000) as total_time
    from query_history as qh
    join users as u
    on qh.user_name = u.name
    where u.name = '{user}'
    group by 1
    order by 2 desc
    limit 1000;
    '''    
    return query

def CREDITS_BY_USER_YEAR(user):
    query = f'''
            WITH USER_HOUR_EXECUTION_CTE AS (
                SELECT  USER_NAME
                ,WAREHOUSE_NAME
                ,DATE_TRUNC('hour',START_TIME) as START_TIME_HOUR
                ,SUM(EXECUTION_TIME)  as USER_HOUR_EXECUTION_TIME
                FROM "SNOWFLAKE"."ACCOUNT_USAGE"."QUERY_HISTORY" 
                WHERE WAREHOUSE_NAME IS NOT NULL
                AND EXECUTION_TIME > 0
            
            --Change the below filter if you want to look at a longer range than the last 1 month 
                AND START_TIME > DATEADD(Month,-12,CURRENT_TIMESTAMP())
                group by 1,2,3
                )
            , HOUR_EXECUTION_CTE AS (
                SELECT  START_TIME_HOUR
                ,WAREHOUSE_NAME
                ,SUM(USER_HOUR_EXECUTION_TIME) AS HOUR_EXECUTION_TIME
                FROM USER_HOUR_EXECUTION_CTE
                group by 1,2
            )
            , APPROXIMATE_CREDITS AS (
                SELECT 
                A.USER_NAME
                ,C.WAREHOUSE_NAME
                ,(A.USER_HOUR_EXECUTION_TIME/B.HOUR_EXECUTION_TIME)*C.CREDITS_USED AS APPROXIMATE_CREDITS_USED

                FROM USER_HOUR_EXECUTION_CTE A
                JOIN HOUR_EXECUTION_CTE B  ON A.START_TIME_HOUR = B.START_TIME_HOUR and B.WAREHOUSE_NAME = A.WAREHOUSE_NAME
                JOIN "SNOWFLAKE"."ACCOUNT_USAGE"."WAREHOUSE_METERING_HISTORY" C ON C.WAREHOUSE_NAME = A.WAREHOUSE_NAME AND C.START_TIME = A.START_TIME_HOUR
            )

            SELECT 
            USER_NAME
            ,SUM(APPROXIMATE_CREDITS_USED) AS APPROXIMATE_CREDITS_USED
            FROM APPROXIMATE_CREDITS
            WHERE USER_NAME = '{user}'
            GROUP BY 1
            ORDER BY 2 DESC
            ;

            '''
    return query

def CREDITS_BY_USER_WEEK(user):
    query = f'''
            WITH USER_HOUR_EXECUTION_CTE AS (
                SELECT  USER_NAME
                ,WAREHOUSE_NAME
                ,DATE_TRUNC('hour',START_TIME) as START_TIME_HOUR
                ,SUM(EXECUTION_TIME)  as USER_HOUR_EXECUTION_TIME
                FROM "SNOWFLAKE"."ACCOUNT_USAGE"."QUERY_HISTORY" 
                WHERE WAREHOUSE_NAME IS NOT NULL
                AND EXECUTION_TIME > 0
            
            --Change the below filter if you want to look at a longer range than the last 1 month 
                AND START_TIME > DATEADD(Day,-7,CURRENT_TIMESTAMP())
                group by 1,2,3
                )
            , HOUR_EXECUTION_CTE AS (
                SELECT  START_TIME_HOUR
                ,WAREHOUSE_NAME
                ,SUM(USER_HOUR_EXECUTION_TIME) AS HOUR_EXECUTION_TIME
                FROM USER_HOUR_EXECUTION_CTE
                group by 1,2
            )
            , APPROXIMATE_CREDITS AS (
                SELECT 
                A.USER_NAME
                ,C.WAREHOUSE_NAME
                ,(A.USER_HOUR_EXECUTION_TIME/B.HOUR_EXECUTION_TIME)*C.CREDITS_USED AS APPROXIMATE_CREDITS_USED

                FROM USER_HOUR_EXECUTION_CTE A
                JOIN HOUR_EXECUTION_CTE B  ON A.START_TIME_HOUR = B.START_TIME_HOUR and B.WAREHOUSE_NAME = A.WAREHOUSE_NAME
                JOIN "SNOWFLAKE"."ACCOUNT_USAGE"."WAREHOUSE_METERING_HISTORY" C ON C.WAREHOUSE_NAME = A.WAREHOUSE_NAME AND C.START_TIME = A.START_TIME_HOUR
            )

            SELECT 
            USER_NAME
            ,SUM(APPROXIMATE_CREDITS_USED) AS APPROXIMATE_CREDITS_USED
            FROM APPROXIMATE_CREDITS
            WHERE USER_NAME = '{user}'
            GROUP BY 1
            ORDER BY 2 DESC
            ;

            '''
    return query
    
def USER_ACCESS_HISTORY(user):
    query = f'''
    select query_id, 
    convert_timezone('Europe/London', query_start_time) as "query_start_time", 
    direct_objects_accessed,
    base_objects_accessed,
    objects_modified
    from snowflake.account_usage.access_history
    where user_name = '{user}'
    order by query_start_time desc;
    '''
    return query

#-------------- TASK MONITORING ------------------
SHOW_TASKS = '''
show tasks in database streamlit;
'''

TASK_HISTORY = '''
select NAME
,count(NAME) as runs
,sum(case when STATE = 'SUCCEEDED'  then 1 else 0 end) as count_succeeded
,sum(case when STATE = 'FAILED' then 1 else 0 end) as count_failed
from snowflake.account_usage.task_history
group by NAME
order by runs;
'''

if __name__ == "__main__":
    pass
