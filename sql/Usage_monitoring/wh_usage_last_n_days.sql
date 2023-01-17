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