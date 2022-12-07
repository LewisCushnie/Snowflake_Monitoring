import streamlit as st
import pandas as pd
from utils import snowflake_connector as sf
from utils import sql

st.set_page_config(
    page_title="Usage Insights app - Data Transfer",
    page_icon="🔹",
    layout="centered",
)

def main():

    #------------------------------- SIDEBAR ----------------------------------- 
    st.sidebar.header('Snowflake session')

    query = sql.STREAMLIT_CREDITS_USED
    STREAMLIT_CREDITS_USED_df = sf.sql_to_dataframe(query)
    metric=round(STREAMLIT_CREDITS_USED_df['SUM(CREDITS_USED_CLOUD_SERVICES)'].iloc[0],5)
    remaining=round(100-metric,3)
    st.sidebar.metric(label='Credits used by Streamlit', value =metric, delta=f'{remaining} remaining')
    
    query = sql.SNOWFLAKE_ACCOUNT_PARAMS
    SNOWFLAKE_ACCOUNT_PARAMS_df = sf.sql_to_dataframe(query)
    SNOWFLAKE_ACCOUNT_PARAMS_df = SNOWFLAKE_ACCOUNT_PARAMS_df.transpose()
    st.sidebar.dataframe(SNOWFLAKE_ACCOUNT_PARAMS_df)

    # credits = SNOWFLAKE_ACCOUNT_PARAMS_df.iloc[0]['Streamlit_Credits_Used']
    # rounded_credits = round(credits, 5)
    # st.sidebar.metric("Credits used from streamlit queries", rounded_credits)

    #------------------------------- SIDEBAR ----------------------------------- 

    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title('Query Monitoring')

    st.markdown(
    '''The **Query Monitoring** page aims to show a breakdown and analysis of frequently called 
    and most expensive queries. The aim is to allow business domains and users to track query history and 
    optimise caching and warehouse compute'''
    )

    # Get clean list of USERS from ACCOUNT_USAGE


    query = sql.USER_LIST 
    users = sf.run_query(query)
    
    clean_users = []

    for i in users:
            clean_users.append(i[0])

    # Get DF of useful query stats for each user
    # Display only selected names

    query = sql.USER_QUERY_HISTORY
    df = sf.sql_to_dataframe(query)
    df = df.set_index('Username')

    df['Scanned From Cache (%)'] = df['Scanned From Cache (%)'].astype(float)              
    df['Avg Partitions Scanned'] = df['Avg Partitions Scanned'].astype(float)     
    df['Avg Total Partitions'] = df['Avg Total Partitions'].astype(float)     
    df['Avg Query Load (%)'] = df['Avg Query Load (%)'].astype(float) 

    selected_username = st.multiselect('Select a user', clean_users)
    df = df.loc[selected_username]      
    download_data = df.to_csv()              

    if selected_username:

        st.dataframe(df)
        st.bar_chart(data = df, y=['Avg Partitions Scanned','Avg Execution Time'])

        st.download_button('Download Results', download_data, 
                            help='Click to download user query history as a csv')

#==========================#
# DOMAIN QUERY PERFORMANCE #
#==========================#

    st.header('Domain Query Performance')

    DOMAIN = st.selectbox('Choose business domain', ('FINANCE', 'UNDERWRITING'))

    DOMAIN_QUERY_USAGE = f'''
        select q.schema_name, sum(w.credits_used), sum(w.credits_used_compute) 
        from snowflake.account_usage.query_history as q
        join snowflake.account_usage.warehouse_metering_history as w
        on q.warehouse_id = w.warehouse_id
        where q.database_name like 'PROD_DB' and q.schema_name like '%{DOMAIN}%'
        group by q.database_name, q.schema_name
        order by sum(w.credits_used) desc;
        '''

    if DOMAIN:
        df = sf.sql_to_dataframe(DOMAIN_QUERY_USAGE)
        st.dataframe(df)


if __name__ == "__main__":
    main()