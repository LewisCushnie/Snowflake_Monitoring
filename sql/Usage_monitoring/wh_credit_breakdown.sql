select
name as wh_name
,sum(credits_used_compute) as compute_credits
,sum(credits_used_cloud_services) as cloud_services_credits
,sum(credits_used) as total_credits
,(cloud_services_credits/total_credits)*100 as perc_cloud
,(compute_credits/total_credits)*100 as perc_compute
from snowflake.account_usage.metering_history
group by wh_name;