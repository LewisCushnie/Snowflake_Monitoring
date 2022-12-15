import streamlit as st
import pandas as pd
from utils import snowflake_connector as sf
from utils import sql

# st.set_page_config(
#     page_title="Usage Insights app - Data Transfer",
#     page_icon="🔹",
#     layout="centered",
# )

def main():
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title('Query Monitoring')

    st.info(
    '''The **Query Monitoring** page highlights frequently called, 
    and most expensive queries. The aim is to allow business domains and users to track query history and 
    optimise caching and warehouse compute.'''
    )

    #------------------------------- SIDEBAR -----------------------------------    
    
    query = sql.SNOWFLAKE_ACCOUNT_PARAMS

    df = sf.sql_to_dataframe(query)
    df = df.transpose()

    current_user = df.loc['CURRENT_USER'].iloc[0]
    st.sidebar.header(f'Hello, {current_user}')

    st.sidebar.subheader('Session Info')

    role = df.loc['CURRENT_ROLE'].iloc[0]
    #st.sidebar.text(f'Current role - {role}')

    wh = df.loc['WAREHOUSE'].iloc[0]
    #st.sidebar.text(f'Warehouse - {wh}')

    st.sidebar.markdown(
    f'''**Current Role** - {role}
     **Current Warehouse** - {wh}'''
    )

    query = sql.STREAMLIT_CREDITS_USED
    STREAMLIT_CREDITS_USED_df = sf.sql_to_dataframe(query)
    metric=round(STREAMLIT_CREDITS_USED_df['CREDITS_USED_STREAMLIT'].iloc[0],5)
    remaining=round(100-metric,3)
    st.sidebar.metric(label='Credits used by Streamlit', value =metric, delta=f'{remaining} remaining')

    #------------------------------- MAIN PAGE ----------------------------------- 
    #==========================#
    # DOMAIN QUERY PERFORMANCE #
    #==========================#
    line = '---'
    st.markdown(line)
    st.header('Compare Domain Query Performance')

    DOMAIN = st.selectbox('Choose business domain', ('FINANCE', 'UNDERWRITING'))

    DOMAIN_QUERY_USAGE = f'''
        select q.schema_name as "Schema"
        , sum(w.credits_used) as "Total Credits Used"
        , sum(w.credits_used_compute) as "Total Compute Credits Used"
        from snowflake.account_usage.query_history as q
        join snowflake.account_usage.warehouse_metering_history as w
        on q.warehouse_id = w.warehouse_id
        where q.database_name like 'PROD_DB' and q.schema_name like '%{DOMAIN}%'
        group by q.database_name, q.schema_name
        order by sum(w.credits_used) desc;
        '''

    if DOMAIN:
        df = sf.sql_to_dataframe(DOMAIN_QUERY_USAGE)
        st.dataframe(df, width=1000)
        st.bar_chart(df, x='Schema', y=['Total Compute Credits Used', 'Total Credits Used'])

    #==========================#
    # QUERY COUNT BY TYPE (ADDITION FROM LEWIS)
    #==========================#
    line = '---'
    st.markdown(line)
    st.header('Query count by type')   
    query = sql.QUERY_COUNT_BY_TYPE
    QUERY_COUNT_BY_TYPE_df = sf.sql_to_dataframe(query)
    st.dataframe(QUERY_COUNT_BY_TYPE_df)
    st.bar_chart(QUERY_COUNT_BY_TYPE_df, x= 'Query Date', y= 'Query Count')

if __name__ == "__main__":
    main()
