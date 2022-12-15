import pandas as pd
import streamlit as st
from utils import snowflake_connector as sf
from utils import sql
import datetime

def main():

    # Apply formatting from the style.css file to the page
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # GLOBAL VARAIBLES
    default_width = 500

    # ===========================================#
    # MAIN PAGE - INTRO
    # ===========================================#

    st.title('Task Monitoring Summary')
    st.success(
    '''
    The **Task Monitoring Summary** page provides a breakdown of task useage within each Snowflake account highlighting
    task credit usage and those which are/aren't currently running. The aim is to allow tasks to be easily tracked and ensure
    they are not left running by mistake.
    '''
    )

    # ===========================================#
    # MAIN PAGE - WAREHOUSE USAGE COMPARISON BAR CHART
    # ===========================================#

    line = '---'
    st.markdown(line)
    st.header('Account task run tracker')
    query = sql.TASK_HISTORY
    SHOW_TASKS_df = sf.sql_to_dataframe(query)

    st.bar_chart(SHOW_TASKS_df, x= 'NAME', y= ['RUNS', 'COUNT_SUCCEEDED', 'COUNT_FAILED'])
    
    raw_data = st.checkbox('Show raw task history data:')
    if raw_data:
        st.dataframe(SHOW_TASKS_df)

    # ===========================================#
    # MAIN PAGE - STATUS SUMMARY
    # ===========================================#

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