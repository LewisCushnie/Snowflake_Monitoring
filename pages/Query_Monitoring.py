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
    st.sidebar.dataframe(STREAMLIT_CREDITS_USED_df)
    metric=STREAMLIT_CREDITS_USED_df['SUM(CREDITS_USED_CLOUD_SERVICES)'].iloc[0]
    st.sidebar.write(metric)
    
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
    df = df.set_index('USER_NAME')

    df.rename(columns = {'AVG(PERCENTAGE_SCANNED_FROM_CACHE)':'Scanned From Cache (%)',
                        'AVG(PARTITIONS_SCANNED)':'Avg Partitions Scanned',
                        'AVG(PARTITIONS_TOTAL)':'Avg Total Partitions',
                        'AVG(EXECUTION_TIME)':'Avg Execution Time',
                        'AVG(QUERY_LOAD_PERCENT)':'Avg Query Load (%)'}, inplace = True)


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

        # if button:
        #     button=False
        
if __name__ == "__main__":
    main()