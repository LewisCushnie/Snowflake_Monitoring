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

    st.bar_chart(SHOW_TASKS_df, x= 'NAME', y= ['RUNS', 'COUNT_SUCCEEDED', 'COUNT_FAILED'])

    demo = alt.Chart(SHOW_TASKS_df).mark_bar().encode(
        x='NAME',
        y='RUNS',
        color='COUNT_SUCCEEDED',
        column='COUNT_FAILED'
    )

    st.altair_chart(demo)

    chart = alt.Chart(SHOW_TASKS_df).mark_bar().encode(
    x=alt.X('NAME'),
    y=alt.Y('RUNS')
    )

    st.altair_chart(chart, theme= 'streamlit')

    df = pd.DataFrame({
        'name': ['brian', 'dominik', 'patricia'],
        'age': [20, 30, 40],
        'salary': [100, 200, 300]
    })

    a = alt.Chart(df).mark_area(opacity=1).encode(
        x='name', y='age')

    b = alt.Chart(df).mark_area(opacity=0.6).encode(
        x='name', y='salary')

    c = alt.layer(a, b)

    st.altair_chart(c, use_container_width=True)

    df = pd.DataFrame([['Action', 5, 'F'], 
                    ['Crime', 10, 'F'], 
                    ['Action', 3, 'M'], 
                    ['Crime', 9, 'M']], 
                    columns=['Genre', 'Rating', 'Gender'])

    chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Genre', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('Rating', axis=alt.Axis(grid=False)),
    color='Gender'
    ).configure_view(
        stroke=None,
    )

    st.altair_chart(chart)
    
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