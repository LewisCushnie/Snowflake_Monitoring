select 
current_database() as DATABASE
,current_schema() as SHEMA
,current_role() as CURRENT_ROLE
,current_session() as SESSION_ID
,current_user() as CURRENT_USER
,current_warehouse() as WAREHOUSE
,current_region() as ACCOUNT_REGION
,current_time() as REGION_TIME
;