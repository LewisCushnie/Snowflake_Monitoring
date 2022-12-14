import pandas as pd
import streamlit as st
from utils import snowflake_connector as sf
from utils.df_styler import colour_df
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

    st.title('Resource Monitoring Summary')

    # MAIN PAGE - INTRO
    st.info(
    '''
    The **Resource Monitoring Summary** page provides a breakdown of resource useage within each Snowflake account highlighting
    how and where credits are being consumed. The aim is to allow easy identification of inefficient or missused resources.
    '''
    )

    # MAIN PAGE - METERING SUMMARY
    line = '---'
    st.markdown(line)
    metering_left_column, metering_right_column = st.columns(2)
    query = sql.METERING_HISTORY
    METERING_HISTORY_df = sf.sql_to_dataframe(query)
    with metering_right_column:
        st.header("Metering Summary:")
        st.dataframe(METERING_HISTORY_df)

    # MAIN PAGE - WAREHOUSE USAGE TABLE
    query = sql.METERING_TOP_10
    METERING_TOP_10_df = sf.sql_to_dataframe(query)
    with metering_left_column:
        st.header('Warehouse Usage')
        st.dataframe(METERING_TOP_10_df)

    # SIDEBAR - MOST USED WAREHOUSE
    most_used_loc = METERING_TOP_10_df['CREDITS_USED'].idxmax()
    most_used_wh = METERING_TOP_10_df['NAME'].iloc[most_used_loc]
    amount_used = round(METERING_TOP_10_df['CREDITS_USED'].iloc[most_used_loc], 3)
    st.sidebar.metric(label='Most used warehouse', value= most_used_wh, delta= f'{amount_used} Credits', delta_color= "normal")

    # MAIN PAGE - WAREHOUSE USAGE COMPARISON BAR CHART
    line = '---'
    st.markdown(line)
    st.header('Warehouse usage comparison chart')
    METERING_TOP_10_df = METERING_TOP_10_df.set_index('NAME')
    METERING_TOP_10_df['CREDITS_USED'] = METERING_TOP_10_df['CREDITS_USED'].astype(float)
    # Multiselect list
    wh_selected = st.multiselect("Pick Warehouse:", list(METERING_TOP_10_df.index),['COMPUTE_WH', 'CADENS_WH', 'INTL_WH'])
    # filter using panda's .loc
    wh_to_show_df = METERING_TOP_10_df.loc[wh_selected]
    # Display the filtered df on the page.
    st.bar_chart(wh_to_show_df)
    # Raw data checkbox
    raw_data = st.checkbox('Show raw warehouse data:')
    if raw_data:
        st.dataframe(wh_to_show_df)

    # MAIN PAGE: COMPUTE_CREDITS_PER_DAY BAR CHART
    line = '---'
    st.markdown(line)
    st.header('Total compute credit usage per day')
    st.write('Cost assumes $4/credit')
    query = sql.COMPUTE_CREDITS_PER_DAY
    COMPUTE_CREDITS_PER_DAY_df = sf.sql_to_dataframe(query)

    # Add slider:
    min_date = COMPUTE_CREDITS_PER_DAY_df['Usage Week'].min()
    max_date = COMPUTE_CREDITS_PER_DAY_df['Usage Week'].max()
    auto_date_lower = min_date
    auto_date_higher = max_date
    slider_values = st.slider(
    'Select date range',
    min_date, max_date, (auto_date_lower, auto_date_higher)
    )

    # Select DataFrame rows between two dates
    date_mask = (COMPUTE_CREDITS_PER_DAY_df['Usage Week'] > slider_values[0]) & (COMPUTE_CREDITS_PER_DAY_df['Usage Week'] <= slider_values[1])
    COMPUTE_CREDITS_PER_DAY_FILTERED_df = COMPUTE_CREDITS_PER_DAY_df.loc[date_mask]
    # Create the bar chart with filtered values
    st.bar_chart(COMPUTE_CREDITS_PER_DAY_FILTERED_df, x= 'Usage Week', y= ['Compute Credits Used','Cost ($)'])
    # Raw data checkbox
    raw_data = st.checkbox('Show raw compute data:')
    if raw_data:
        st.write('Red - $10+ per day | Orange - $5-%10 per day | Green - Less than $5 per day')
        COMPUTE_CREDITS_PER_DAY_FILTERED_df = COMPUTE_CREDITS_PER_DAY_FILTERED_df.style.applymap(colour_df,
        subset=pd.IndexSlice[:,['Cost ($)']])
        st.dataframe(COMPUTE_CREDITS_PER_DAY_FILTERED_df, width=1000)

    # COMPUTE AVAILABILITY VS EXECUTION TIME
    line = '---'
    st.markdown(line)
    st.header('Compute availablity v.s execution time')
    query = sql.COMPUTE_AVAILABILITY_AND_EXECUTION_TIME
    COMPUTE_AVAILABILITY_AND_EXECUTION_TIME_df = sf.sql_to_dataframe(query)
    st.bar_chart(COMPUTE_AVAILABILITY_AND_EXECUTION_TIME_df[['HOUR', 'TOTAL_EXEC_TIME_SEC', 'COMPUTE_AVAILABILITY_SEC']], x= 'HOUR')
    # Raw data checkbox
    raw_data = st.checkbox('Show raw availability data:')
    if raw_data:
        st.dataframe(COMPUTE_AVAILABILITY_AND_EXECUTION_TIME_df)

if __name__ == "__main__":
    main()