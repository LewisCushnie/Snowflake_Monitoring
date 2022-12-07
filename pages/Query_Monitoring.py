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
    
    query = sql.SNOWFLAKE_ACCOUNT_PARAMS
    SNOWFLAKE_ACCOUNT_PARAMS_df = sf.sql_to_dataframe(query)
    SNOWFLAKE_ACCOUNT_PARAMS_df = SNOWFLAKE_ACCOUNT_PARAMS_df.transpose()
    st.sidebar.dataframe(SNOWFLAKE_ACCOUNT_PARAMS_df)

    # streamlit_credits_used_df = pd.DataFrame(streamlit_credits_used, columns=['Streamlit_Credits_Used'])
    # credits = streamlit_credits_used_df.iloc[0]['Streamlit_Credits_Used']
    # rounded_credits = round(credits, 5)
    # st.sidebar.metric("Credits used from streamlit queries", rounded_credits)

    # snowflake_session_variables_df = pd.DataFrame(snowflake_session_variables, 
    # columns=['Database', 'Schema', 'Current role', 'Session ID', 'Current user', 'Warehouse', 'Region', 'Region time'])
    # transposed_session_variables_df = snowflake_session_variables_df.transpose().reset_index()
    # transposed_session_variables_df = transposed_session_variables_df.rename(columns={"index": "Session Parameter", 0: "Value"})
    # st.sidebar.dataframe(transposed_session_variables_df)
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
    users = pd.read_sql(query,sf)

    clean_users = []

    for i in users:
            clean_users.append(i[0])

    # Get DF of useful query stats for each user
    # Display only selected names

    query = sql.USER_QUERY_HISTORY
    df = sf.sql_to_dataframe(query)

    selected_username = st.multiselect('Select a user', clean_users)
    df = df.loc[selected_username]                    

    if selected_username:
        st.dataframe(df)
        # st.bar_chart(data = df, y=['Avg Partitions Scanned', 'Percent from cache'])
        # st.bar_chart(data = df, y=['Execution time'])


if __name__ == "__main__":
    main()