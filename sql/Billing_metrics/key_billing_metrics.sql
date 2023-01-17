-- Description:
-- Identify key metrics as it pertains to total compute costs from warehouses, serverless features, and total storage costs.

-- How to Interpret Results:
-- Where are we seeing most of our costs coming from (compute, serverless, storage)? Are seeing excessive costs in any of those categories that are above expectations?

-- Primary Schema:
-- Account_Usage

/* These queries can be used to measure where costs have been incurred by 
   the different cost vectors within a Snowflake account including:
   1) Warehouse Costs
   2) Serverless Costs
   3) Storage Costs
   
   To accurately report the dollar amounts, make changes to the variables
   defined on lines 17 to 20 to properly reflect your credit price, the initial
   capacity purchased, when your contract started and the term (default 12 months)

   If unsure, ask your Sales Engineer or Account Executive
*/

USE DATABASE SNOWFLAKE;
USE SCHEMA ACCOUNT_USAGE;

SET CREDIT_PRICE = 4.00; --edit this number to reflect credit price
SET TERM_LENGTH = 12; --integer value in months
SET TERM_START_DATE = '2019-01-01';
SET TERM_AMOUNT = 100000.00; --number(10,2) value in dollars


WITH CONTRACT_VALUES AS (

      SELECT
               $CREDIT_PRICE::decimal(10,2) as CREDIT_PRICE
              ,$TERM_AMOUNT::decimal(38,0) as TOTAL_CONTRACT_VALUE
              ,$TERM_START_DATE::timestamp as CONTRACT_START_DATE
              ,DATEADD(month,$TERM_LENGTH,$TERM_START_DATE)::timestamp as CONTRACT_END_DATE

),
PROJECTED_USAGE AS (

      SELECT
                 CREDIT_PRICE
                ,TOTAL_CONTRACT_VALUE
                ,CONTRACT_START_DATE
                ,CONTRACT_END_DATE
                ,(TOTAL_CONTRACT_VALUE)
                    /
                    DATEDIFF(day,CONTRACT_START_DATE,CONTRACT_END_DATE)  AS DOLLARS_PER_DAY
                , (TOTAL_CONTRACT_VALUE/CREDIT_PRICE)
                    /
                DATEDIFF(day,CONTRACT_START_DATE,CONTRACT_END_DATE) AS CREDITS_PER_DAY
      FROM      CONTRACT_VALUES

)

--COMPUTE FROM WAREHOUSES
SELECT
         'WH Compute' as WAREHOUSE_GROUP_NAME
        ,WMH.WAREHOUSE_NAME
        ,NULL AS GROUP_CONTACT
        ,NULL AS GROUP_COST_CENTER
        ,NULL AS GROUP_COMMENT
        ,WMH.START_TIME
        ,WMH.END_TIME
        ,WMH.CREDITS_USED
        ,$CREDIT_PRICE
        ,($CREDIT_PRICE*WMH.CREDITS_USED) AS DOLLARS_USED
        ,'ACTUAL COMPUTE' AS MEASURE_TYPE                   
from    SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY WMH

UNION ALL

--COMPUTE FROM SNOWPIPE
SELECT
         'Snowpipe' AS WAREHOUSE_GROUP_NAME
        ,PUH.PIPE_NAME AS WAREHOUSE_NAME
        ,NULL AS GROUP_CONTACT
        ,NULL AS GROUP_COST_CENTER
        ,NULL AS GROUP_COMMENT
        ,PUH.START_TIME
        ,PUH.END_TIME
        ,PUH.CREDITS_USED
        ,$CREDIT_PRICE
        ,($CREDIT_PRICE*PUH.CREDITS_USED) AS DOLLARS_USED
        ,'ACTUAL COMPUTE' AS MEASURE_TYPE
from    SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY PUH

UNION ALL

--COMPUTE FROM CLUSTERING
SELECT
         'Auto Clustering' AS WAREHOUSE_GROUP_NAME
        ,DATABASE_NAME || '.' || SCHEMA_NAME || '.' || TABLE_NAME AS WAREHOUSE_NAME
        ,NULL AS GROUP_CONTACT
        ,NULL AS GROUP_COST_CENTER
        ,NULL AS GROUP_COMMENT
        ,ACH.START_TIME
        ,ACH.END_TIME
        ,ACH.CREDITS_USED
        ,$CREDIT_PRICE
        ,($CREDIT_PRICE*ACH.CREDITS_USED) AS DOLLARS_USED
        ,'ACTUAL COMPUTE' AS MEASURE_TYPE
from    SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY ACH

UNION ALL

--COMPUTE FROM MATERIALIZED VIEWS
SELECT
         'Materialized Views' AS WAREHOUSE_GROUP_NAME
        ,DATABASE_NAME || '.' || SCHEMA_NAME || '.' || TABLE_NAME AS WAREHOUSE_NAME
        ,NULL AS GROUP_CONTACT
        ,NULL AS GROUP_COST_CENTER
        ,NULL AS GROUP_COMMENT
        ,MVH.START_TIME
        ,MVH.END_TIME
        ,MVH.CREDITS_USED
        ,$CREDIT_PRICE
        ,($CREDIT_PRICE*MVH.CREDITS_USED) AS DOLLARS_USED
        ,'ACTUAL COMPUTE' AS MEASURE_TYPE
from    SNOWFLAKE.ACCOUNT_USAGE.MATERIALIZED_VIEW_REFRESH_HISTORY MVH

UNION ALL

--COMPUTE FROM SEARCH OPTIMIZATION
SELECT
         'Search Optimization' AS WAREHOUSE_GROUP_NAME
        ,DATABASE_NAME || '.' || SCHEMA_NAME || '.' || TABLE_NAME AS WAREHOUSE_NAME
        ,NULL AS GROUP_CONTACT
        ,NULL AS GROUP_COST_CENTER
        ,NULL AS GROUP_COMMENT
        ,SOH.START_TIME
        ,SOH.END_TIME
        ,SOH.CREDITS_USED
        ,$CREDIT_PRICE
        ,($CREDIT_PRICE*SOH.CREDITS_USED) AS DOLLARS_USED
        ,'ACTUAL COMPUTE' AS MEASURE_TYPE
from    SNOWFLAKE.ACCOUNT_USAGE.SEARCH_OPTIMIZATION_HISTORY SOH

UNION ALL

--COMPUTE FROM REPLICATION
SELECT
         'Replication' AS WAREHOUSE_GROUP_NAME
        ,DATABASE_NAME AS WAREHOUSE_NAME
        ,NULL AS GROUP_CONTACT
        ,NULL AS GROUP_COST_CENTER
        ,NULL AS GROUP_COMMENT
        ,RUH.START_TIME
        ,RUH.END_TIME
        ,RUH.CREDITS_USED
        ,$CREDIT_PRICE
        ,($CREDIT_PRICE*RUH.CREDITS_USED) AS DOLLARS_USED
        ,'ACTUAL COMPUTE' AS MEASURE_TYPE
from    SNOWFLAKE.ACCOUNT_USAGE.REPLICATION_USAGE_HISTORY RUH

UNION ALL

--STORAGE COSTS
SELECT
         'Storage' AS WAREHOUSE_GROUP_NAME
        ,'Storage' AS WAREHOUSE_NAME
        ,NULL AS GROUP_CONTACT
        ,NULL AS GROUP_COST_CENTER
        ,NULL AS GROUP_COMMENT
        ,SU.USAGE_DATE
        ,SU.USAGE_DATE
        ,NULL AS CREDITS_USED
        ,$CREDIT_PRICE
        ,((STORAGE_BYTES + STAGE_BYTES + FAILSAFE_BYTES)/(1024*1024*1024*1024)*23)/DA.DAYS_IN_MONTH AS DOLLARS_USED
        ,'ACTUAL COMPUTE' AS MEASURE_TYPE
from    SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE SU
JOIN    (SELECT COUNT(*) AS DAYS_IN_MONTH,TO_DATE(DATE_PART('year',D_DATE)||'-'||DATE_PART('month',D_DATE)||'-01') as DATE_MONTH FROM SNOWFLAKE_SAMPLE_DATA.TPCDS_SF10TCL.DATE_DIM GROUP BY TO_DATE(DATE_PART('year',D_DATE)||'-'||DATE_PART('month',D_DATE)||'-01')) DA ON DA.DATE_MONTH = TO_DATE(DATE_PART('year',USAGE_DATE)||'-'||DATE_PART('month',USAGE_DATE)||'-01')

UNION ALL


SELECT
         NULL as WAREHOUSE_GROUP_NAME
        ,NULL as WAREHOUSE_NAME
        ,NULL as GROUP_CONTACT
        ,NULL as GROUP_COST_CENTER
        ,NULL as GROUP_COMMENT
        ,DA.D_DATE::timestamp as START_TIME
        ,DA.D_DATE::timestamp as END_TIME
        ,PU.CREDITS_PER_DAY AS CREDITS_USED
        ,PU.CREDIT_PRICE
        ,PU.DOLLARS_PER_DAY AS DOLLARS_USED
        ,'PROJECTED COMPUTE' AS MEASURE_TYPE
FROM    PROJECTED_USAGE PU
JOIN    SNOWFLAKE_SAMPLE_DATA.TPCDS_SF10TCL.DATE_DIM DA ON DA.D_DATE BETWEEN PU.CONTRACT_START_DATE AND PU.CONTRACT_END_DATE

UNION ALL


SELECT
         NULL as WAREHOUSE_GROUP_NAME
        ,NULL as WAREHOUSE_NAME
        ,NULL as GROUP_CONTACT
        ,NULL as GROUP_COST_CENTER
        ,NULL as GROUP_COMMENT
        ,NULL as START_TIME
        ,NULL as END_TIME
        ,NULL AS CREDITS_USED
        ,PU.CREDIT_PRICE
        ,PU.TOTAL_CONTRACT_VALUE AS DOLLARS_USED
        ,'CONTRACT VALUES' AS MEASURE_TYPE
FROM    PROJECTED_USAGE PU
;