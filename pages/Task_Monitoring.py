import pandas as pd
import streamlit as st
import altair as alt
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
    # MAIN PAGE - ACCOUNT TASK RUN TRACKER
    # ===========================================#

    line = '---'
    st.markdown(line)
    st.header('Account task run tracker')
    query = sql.TASK_HISTORY
    SHOW_TASKS_df = sf.sql_to_dataframe(query)

    # st.display(SHOW_TASKS_df)
    # st.display(SHOW_TASKS_df.melt())

    st.bar_chart(SHOW_TASKS_df, x= 'NAME', y= ['COUNT_SUCCEEDED', 'COUNT_FAILED'])

    # chart = alt.Chart(SHOW_TASKS_df).mark_bar().encode(
    # x='sum(yield):Q',
    # y=alt.Y('site:N', sort='-x')
    # )

    # .transform_fold(
    # ['AAPL', 'AMZN', 'GOOG'],
    # as_=['company', 'price']

    chart = alt.Chart(SHOW_TASKS_df).transform_fold(
    ['COUNT_SUCCEEDED', 'COUNT_FAILED'],
    as_=['STATUS', 'COUNT']
    ).mark_bar().encode(
    x= alt.X('NAME', sort= '-y'),
    y= alt.Y('COUNT:Q'),
    color= 'STATUS:N'
    )

    st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

    # a = alt.Chart(SHOW_TASKS_df).mark_bar().encode(
    # x='NAME', y='COUNT_SUCCEEDED')

    # b = alt.Chart(SHOW_TASKS_df).mark_bar().encode(
    # x='NAME', y='COUNT_FAILED')

    # c = alt.layer(a, b)
    # st.altair_chart(c, use_container_width=True, theme= 'streamlit')
    
    raw_data = st.checkbox('Show raw task history data:')
    if raw_data:
        st.dataframe(SHOW_TASKS_df)

    # ===========================================#
    # MAIN PAGE - ACCOUNT TASK STATUS SUMMARY
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