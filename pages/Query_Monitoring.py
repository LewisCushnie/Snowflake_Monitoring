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
    # USER QUERY PERFORMANCE #
    #==========================#
    line = '---'
    st.markdown(line)
    st.header('Compare User Query Performance')

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

        st.dataframe(df, width=1000)
        st.bar_chart(data = df, y=['Avg Partitions Scanned','Avg Execution Time'])

        st.download_button('Download Results', download_data, 
                            help='Click to download user query history as a csv')

    #==========================#
    # USER IN DETAIL #
    #==========================#
    line = '---'
    st.markdown(line)
    st.header('Get Detailed Performance Info by User')

    with st.form('user_form'):
        user = st.selectbox('Select a user', clean_users)
        submitted = st.form_submit_button('Submit')

        if submitted:

            try:
            
                LOGIN = f'''
                select last_success_login
                from users
                where name = '{user}';
                '''

                CREDITS_BY_USER = f'''
                WITH USER_HOUR_EXECUTION_CTE AS (
                    SELECT  USER_NAME
                    ,WAREHOUSE_NAME
                    ,DATE_TRUNC('hour',START_TIME) as START_TIME_HOUR
                    ,SUM(EXECUTION_TIME)  as USER_HOUR_EXECUTION_TIME
                    FROM "SNOWFLAKE"."ACCOUNT_USAGE"."QUERY_HISTORY" 
                    WHERE WAREHOUSE_NAME IS NOT NULL
                    AND EXECUTION_TIME > 0
                
                --Change the below filter if you want to look at a longer range than the last 1 month 
                    AND START_TIME > DATEADD(Month,-1,CURRENT_TIMESTAMP())
                    group by 1,2,3
                    )
                , HOUR_EXECUTION_CTE AS (
                    SELECT  START_TIME_HOUR
                    ,WAREHOUSE_NAME
                    ,SUM(USER_HOUR_EXECUTION_TIME) AS HOUR_EXECUTION_TIME
                    FROM USER_HOUR_EXECUTION_CTE
                    group by 1,2
                )
                , APPROXIMATE_CREDITS AS (
                    SELECT 
                    A.USER_NAME
                    ,C.WAREHOUSE_NAME
                    ,(A.USER_HOUR_EXECUTION_TIME/B.HOUR_EXECUTION_TIME)*C.CREDITS_USED AS APPROXIMATE_CREDITS_USED

                    FROM USER_HOUR_EXECUTION_CTE A
                    JOIN HOUR_EXECUTION_CTE B  ON A.START_TIME_HOUR = B.START_TIME_HOUR and B.WAREHOUSE_NAME = A.WAREHOUSE_NAME
                    JOIN "SNOWFLAKE"."ACCOUNT_USAGE"."WAREHOUSE_METERING_HISTORY" C ON C.WAREHOUSE_NAME = A.WAREHOUSE_NAME AND C.START_TIME = A.START_TIME_HOUR
                )

                SELECT 
                USER_NAME
                ,SUM(APPROXIMATE_CREDITS_USED) AS APPROXIMATE_CREDITS_USED
                FROM APPROXIMATE_CREDITS
                WHERE USER_NAME = '{user}'
                GROUP BY 1
                ORDER BY 2 DESC
                ;

                '''

                df = sf.sql_to_dataframe(LOGIN)
                st.write(f"Last login by user, {user}: {df['LAST_SUCCESS_LOGIN'][0]}")

                df = sf.sql_to_dataframe(CREDITS_BY_USER)
                credits = df['APPROXIMATE_CREDITS_USED'][0]
                st.metric('Credits Used',round(credits,2))

            except:
                st.write('Selected user has not logged')


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
