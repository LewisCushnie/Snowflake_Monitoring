import pandas as pd
import streamlit as st
from utils import snowflake_connector as sf
from utils import sql
import datetime

st.set_page_config(
    page_title="Usage Insights app - Data Transfer",
    page_icon="🔹",
    layout="centered",
)

def main():

    # VARAIBLES
    default_width = 500

    # SIDEBAR - SNOWFLAKE ACCOUNT PARAMETERS
    query = sql.SNOWFLAKE_ACCOUNT_PARAMS
    df = sf.sql_to_dataframe(query)
    df = df.transpose()

    current_user = df.loc['CURRENT_USER'].iloc[0]
    st.sidebar.header(f'Hello, {current_user} ❄️')

    role = df.loc['CURRENT_ROLE'].iloc[0]
    #st.sidebar.text(f'Current role - {role}')

    wh = df.loc['WAREHOUSE'].iloc[0]
    #st.sidebar.text(f'Warehouse - {wh}')

    st.sidebar.markdown(
    f'''**Current Role** - {role}
     **Current Warehouse** - {wh}'''
    )

    # SIDEBAR - CREDITS USED THROUGH STREAMLIT
    # Credits used running queries through streamlit
    query = sql.STREAMLIT_CREDITS_USED
    STREAMLIT_CREDITS_USED_df = sf.sql_to_dataframe(query)
    metric=round(STREAMLIT_CREDITS_USED_df['CREDITS_USED_STREAMLIT'].iloc[0],5)
    remaining=round(100-metric,3)
    st.sidebar.metric(label='**Credits used by Streamlit:**', value =metric, delta=f'{remaining} remaining')

    line = '---'
    st.sidebar.markdown(line)
    
    # # SIDEBAR - ACCOUNT PARAMETERS OF LINKED ACCOUNT
    # query = sql.SNOWFLAKE_ACCOUNT_PARAMS
    # SNOWFLAKE_ACCOUNT_PARAMS_df = sf.sql_to_dataframe(query)
    # SNOWFLAKE_ACCOUNT_PARAMS_df = SNOWFLAKE_ACCOUNT_PARAMS_df.transpose()
    # st.sidebar.dataframe(SNOWFLAKE_ACCOUNT_PARAMS_df)

    # SIDEBAR - WAREHOUSE USAGE SUMMARY STATS
    st.sidebar.header('Warehouse usage summary stats')
    query = sql.WH_USAGE_LAST_7_DAYS
    WH_USAGE_LAST_7_DAYS_df = sf.sql_to_dataframe(query)
    metric=round(WH_USAGE_LAST_7_DAYS_df['CREDITS_USED_LAST_PERIOD'].iloc[0],5)
    pct_change=round(WH_USAGE_LAST_7_DAYS_df['PCT_CHANGE'].iloc[0],3)
    st.sidebar.metric(label='Credit usage over last 7 day period', value= metric, delta= f'{pct_change}%', delta_color= "inverse")

    # Apply formatting from the style.css file to the page
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title('Task Monitoring Summary')

    # MAIN PAGE - INTRO
    st.info(
    '''
    The **Task Monitoring Summary** page provides a breakdown of task useage within each Snowflake account highlighting
    task credit usage and those which are/aren't currently running. The aim is to allow tasks to be easily tracked and ensure
    they are not left running by mistake.
    '''
    )

    # MAIN PAGE - WAREHOUSE USAGE COMPARISON BAR CHART
    line = '---'
    st.markdown(line)
    st.header('Account task run tracker')
    query = sql.TASK_HISTORY
    SHOW_TASKS_df = sf.sql_to_dataframe(query)

    st.bar_chart(SHOW_TASKS_df, x= 'NAME', y= ['RUNS', 'COUNT_SUCCEEDED', 'COUNT_FAILED'])
    
    raw_data = st.checkbox('Show raw task history data:')
    if raw_data:
        st.dataframe(SHOW_TASKS_df)

    # MAIN PAGE - STATUS SUMMARY
    line = '---'
    st.markdown(line)
    st.header('Account task status summary')
    query = sql.SHOW_TASKS
    SHOW_TASKS_df = sf.sql_to_dataframe(query)
    SHOW_TASKS_df = SHOW_TASKS_df[['name', 'warehouse', 'schedule', 'state']]
    
    def highlighter(cell_value):
        if cell_value == 'started':
            return 'background-color: green'
    
    print("Highlighted DataFrame :")
    SHOW_TASKS_df.style.apply(highlighter, axis = None)
    st.dataframe(SHOW_TASKS_df)

    raw_data = st.checkbox('Show raw task activity data:')
    if raw_data:
        st.dataframe(SHOW_TASKS_df)


if __name__ == "__main__":
    main()