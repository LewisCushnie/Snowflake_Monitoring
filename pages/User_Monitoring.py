import streamlit as st
import pandas as pd
from utils import snowflake_connector as sf
from utils.functions import add_logo
from utils import sql

def main():

    # Apply formatting from the style.css file to the page
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    #===================#
    # MAIN PAGE - INTRO #
    #===================#

    st.title('User Monitoring')
    st.success(
    '''The **User Monitoring** page allows you to track and compare account usage and query performance between users.
    Full access history, including direct and base object access, is available to download for each user
    '''
    )

    add_logo()

    # Get clean list of USERS from ACCOUNT_USAGE
    query = sql.USER_LIST 
    users = sf.run_query(query)
    
    clean_users = []

    for i in users:
            clean_users.append(i[0])

    #================#
    # USER IN DETAIL #
    #================#
    
    line = '---'
    st.markdown(line)
    st.header('Get Detailed Performance Info by User')

    with st.form('user_form'):
        user = st.selectbox('Select a user', clean_users)
        submitted = st.form_submit_button('Submit')

        if submitted:
        
            LOGIN = sql.LOGIN(user)
            LOGIN_df = sf.sql_to_dataframe(LOGIN)

            CREDITS_BY_USER_YEAR = sql.CREDITS_BY_USER_YEAR(user)
            CREDITS_BY_USER_YEAR_df = sf.sql_to_dataframe(CREDITS_BY_USER_YEAR)

            CREDITS_BY_USER_WEEK = sql.CREDITS_BY_USER_WEEK(user)
            CREDITS_BY_USER_WEEK_df = sf.sql_to_dataframe(CREDITS_BY_USER_WEEK)

            USER_USAGE = sql.USER_USAGE(user)
            USER_USAGE_df = sf.sql_to_dataframe(USER_USAGE)

            try:
                last_login = LOGIN_df['LAST_LOGIN'][0]
                role = LOGIN_df['DEFAULT_ROLE'][0]
                name = LOGIN_df['NAME'][0]
                if len(role) > 0:
                    st.write(f'{user} ({role})')
                else:
                    st.write(f'{user} (no default role)')
                st.info(body=f"Last active: {last_login} day(s) ago", icon='ℹ️')

        
            except Exception as e:
                st.write('User not logged in')
            
            credits_year = CREDITS_BY_USER_YEAR_df['APPROXIMATE_CREDITS_USED'][0]
            st.dataframe(CREDITS_BY_USER_YEAR_df)
            credits_week = CREDITS_BY_USER_WEEK_df['APPROXIMATE_CREDITS_USED'][0]
            st.dataframe(CREDITS_BY_USER_WEEK_df)
            # average_week = credits_year/52.1429
            # st.write(average_week)
            # st.metric('Credits Used Last 7 days', value=round(credits_week,2), delta=round(average_week,2))
            # except:
            #     st.write('No credit usage by user')

    USER_ACCESS_HISTORY = sql.USER_ACCESS_HISTORY(user)
    df = sf.sql_to_dataframe(USER_ACCESS_HISTORY)
    download = df.to_csv().encode('utf-8')

    st.download_button(
        label= f"Download access history for {user}",
        data=download,
        file_name=f'{user}_access_hisotry.csv'
    )

    #===============#
    # COMPARE USERS #
    #===============#

    line = '---'
    st.markdown(line)
    st.header('Compare User Query Performance')

    # Get DF of useful query stats for each user
    # Display only selected names

    query = sql.USER_QUERY_HISTORY
    df = sf.sql_to_dataframe(query)
    df = df.set_index('Username')
    
    selected_username = st.multiselect('Select a user', clean_users)
    df = df.loc[selected_username]      
    download_data = df.to_csv()              

    if selected_username:

        st.dataframe(df, width=1000)
        st.bar_chart(data = df, y=['Avg Partitions Scanned','Avg Execution Time'])

        st.download_button('Download Results', download_data, 
                            help='Click to download user query history as a csv')            

if __name__ == "__main__":
    main()