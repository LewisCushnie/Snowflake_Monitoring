import streamlit as st
import pandas as pd
from utils import snowflake_connector as sf
from utils import sql

def main():

    # Apply formatting from the style.css file to the page
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
    #==========================#
    # MAIN PAGE - INTRO #
    #==========================#

    st.title('Query Monitoring')
    st.success(
    '''The **Query Monitoring** page highlights frequently called, 
    and most expensive queries. The aim is to allow business domains and users to track query history and 
    optimise caching and warehouse compute.'''
    )

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

    query = sql.QUERY_CATEGORY
    df = sf.sql_to_dataframe(query)
    st.bar_chart(df, x='Query Category', y='Number of Queries')

    st.markdown(line)

    query = sql.QUERY_COUNT_BY_TYPE
    QUERY_COUNT_BY_TYPE_df = sf.sql_to_dataframe(query)
    st.dataframe(QUERY_COUNT_BY_TYPE_df)
    st.bar_chart(QUERY_COUNT_BY_TYPE_df, x= 'Query Date', y= 'Query Count')

if __name__ == "__main__":
    main()
