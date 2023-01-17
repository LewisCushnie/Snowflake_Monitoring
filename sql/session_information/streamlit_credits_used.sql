select
sum(credits_used_cloud_services) as CREDITS_USED_STREAMLIT
from query_history
where query_tag = 'StreamlitQuery';