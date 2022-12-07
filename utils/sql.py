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

if __name__ == "__main__":
    pass