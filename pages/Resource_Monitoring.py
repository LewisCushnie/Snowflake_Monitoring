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

    # SIDEBAR - CREDITS USED THROUGH STREAMLIT
    st.sidebar.header('Snowflake session')
    # Credits used running queries through streamlit
    query = sql.STREAMLIT_CREDITS_USED
    STREAMLIT_CREDITS_USED_df = sf.sql_to_dataframe(query)
    metric=round(STREAMLIT_CREDITS_USED_df['CREDITS_USED_STREAMLIT'].iloc[0],5)
    remaining=round(100-metric,3)
    st.sidebar.metric(label='Credits used by Streamlit', value =metric, delta=f'{remaining} remaining')
    
    # SIDEBAR - ACCOUNT PARAMETERS OF LINKED ACCOUNT
    query = sql.SNOWFLAKE_ACCOUNT_PARAMS
    SNOWFLAKE_ACCOUNT_PARAMS_df = sf.sql_to_dataframe(query)
    SNOWFLAKE_ACCOUNT_PARAMS_df = SNOWFLAKE_ACCOUNT_PARAMS_df.transpose()
    st.sidebar.dataframe(SNOWFLAKE_ACCOUNT_PARAMS_df)

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
    st.text(
    '''
    This page provides a breakdown of the resource useage within the Snowflake account to better understand
    where and how credits are being consumed on the account. This will include a number of interactive charts,
    as well as recomendaions for parameter changes within snowflake that aim to maximise resourcse consumption
    efficiency.

    This page will look at:

    - Warehouse monitoring
    - Task monitoring
    - Snowpipe monitoring
    '''
    )

    left_column, right_column = st.columns(2)

    # MAIN PAGE - METERING SUMMARY
    query = sql.METERING_HISTORY
    METERING_HISTORY_df = sf.sql_to_dataframe(query)
    with right_column:
        st.header("Metering Summary:")
        st.dataframe(METERING_HISTORY_df)

    # MAIN PAGE - WAREHOUSE USAGE TABLE
    query = sql.METERING_TOP_10
    METERING_TOP_10_df = sf.sql_to_dataframe(query)
    with left_column:
        st.header('Warehouse Usage')
        st.dataframe(METERING_TOP_10_df)

    # SIDEBAR - MOST USED WAREHOUSE
    most_used_loc = METERING_TOP_10_df['CREDITS_USED'].idxmax()
    most_used_wh = METERING_TOP_10_df['NAME'].iloc[most_used_loc]
    amount_used = round(METERING_TOP_10_df['CREDITS_USED'].iloc[most_used_loc], 3)
    st.sidebar.metric(label='Most used warehouse', value= most_used_wh, delta= f'{amount_used} Credits', delta_color= "normal")

    # MAIN PAGE - WAREHOUSE USAGE COMPARISON BAR CHART
    st.header('Warehouse usage comparison chart')
    METERING_TOP_10_df = METERING_TOP_10_df.set_index('NAME')
    METERING_TOP_10_df['CREDITS_USED'] = METERING_TOP_10_df['CREDITS_USED'].astype(float)
    # Multiselect list
    wh_selected = st.multiselect("Pick Warehouse:", list(METERING_TOP_10_df.index),['COMPUTE_WH', 'CADENS_WH', 'INTL_WH'])
    # filter using panda's .loc
    wh_to_show_df = METERING_TOP_10_df.loc[wh_selected]
    # Display the filtered df on the page.
    st.bar_chart(wh_to_show_df)

    query = sql.COMPUTE_CREDITS_PER_DAY
    COMPUTE_CREDITS_PER_DAY_df = sf.sql_to_dataframe(query)
    st.dataframe(COMPUTE_CREDITS_PER_DAY_df)
    st.bar_chart(COMPUTE_CREDITS_PER_DAY_df, x= 'Usage Week', y= 'Compute Credits Used')

    # Add a slider to the sidebar:
    min_date = COMPUTE_CREDITS_PER_DAY_df['Usage Week'].min()
    max_date = COMPUTE_CREDITS_PER_DAY_df['Usage Week'].max()
    auto_date_lower = min_date
    auto_date_higher = max_date

    with left_column:
        lower_date_input = st.date_input(
        "Enter date range start:",
        datetime.date(2019, 7, 6))

    with right_column:
        higher_date_input = st.date_input(
        "Enter date range end:",
        datetime.date(2019, 7, 6))

    slider = st.slider(
    'Select date range',
    min_date, max_date, (auto_date_lower, auto_date_higher)
    )
    #, (25.0, 75.0)

    st.stop()

    # Multiselect list
    wh_selected = st.multiselect("Pick Warehouse:", list(METERING_TOP_10_df.index),['COMPUTE_WH', 'CADENS_WH', 'INTL_WH'])
    # filter using panda's .loc
    wh_to_show_df = METERING_TOP_10_df.loc[wh_selected]
    # Display the filtered df on the page.
    st.bar_chart(wh_to_show_df)
    
    

if __name__ == "__main__":
    main()