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
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title('Query Monitoring')

    st.markdown(
    '''The **Query Monitoring** page aims to show a breakdown and analysis of frequently called 
    and most expensive queries. The aim is to allow business domains and users to track query history and 
    optimise caching and warehouse compute'''
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
    # USER QUERY PERFORMANCE #
    #==========================#

    st.header('User Query Performance')

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

    df['Avg Scanned from Cache (%)'] = df['Avg Scanned from Cache (%)'].astype(float)              
    df['Avg Partitions Scanned'] = df['Avg Partitions Scanned'].astype(float)     
    df['Avg Partitions Used'] = df['Avg Partitions Used'].astype(float)     
    
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
        st.dataframe(df, width=500)
        st.bar_chart(df, x='Schema', y=['Total Compute Credits Used', 'Total Credits Used'])


if __name__ == "__main__":
    main()
