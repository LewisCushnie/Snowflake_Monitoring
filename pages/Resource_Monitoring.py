import streamlit as st
from utils import snowflake_connector as sf
from utils import sql

st.set_page_config(
    page_title="Usage Insights app - Data Transfer",
    page_icon="🔹",
    layout="centered",
)

def main():

    # Variables
    default_width = 500

    #------------------------------- SIDEBAR ----------------------------------- 
    st.sidebar.header('Snowflake session')

    # Credits used running queries through streamlit
    query = sql.STREAMLIT_CREDITS_USED
    STREAMLIT_CREDITS_USED_df = sf.sql_to_dataframe(query)
    metric=round(STREAMLIT_CREDITS_USED_df['SUM(CREDITS_USED_CLOUD_SERVICES)'].iloc[0],5)
    remaining=round(100-metric,3)
    st.sidebar.metric(label='Credits used by Streamlit', value =metric, delta=f'{remaining} remaining')
    
    # Account parameters of the account being accessed through streamlit
    query = sql.SNOWFLAKE_ACCOUNT_PARAMS
    SNOWFLAKE_ACCOUNT_PARAMS_df = sf.sql_to_dataframe(query)
    SNOWFLAKE_ACCOUNT_PARAMS_df = SNOWFLAKE_ACCOUNT_PARAMS_df.transpose()
    st.sidebar.dataframe(SNOWFLAKE_ACCOUNT_PARAMS_df)

    #------------------------------- SIDEBAR ----------------------------------- 

    # Apply formatting from the style.css file to the page
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title('Resource Monitoring Summary')

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

    query = sql.METERING_HISTORY
    METERING_HISTORY_df = sf.sql_to_dataframe(query)
    with right_column:
        st.header("Metering Summary:")
        st.dataframe(METERING_HISTORY_df)

    query = sql.METERING_TOP_10
    METERING_TOP_10_df = sf.sql_to_dataframe(query)
    with left_column:
        st.header('Warehouse Usage')
        st.dataframe(METERING_TOP_10_df)

    st.header('Warehouse usage comparison chart')
    METERING_TOP_10_df = METERING_TOP_10_df.set_index('NAME')
    METERING_TOP_10_df['SUM(CREDITS_USED)'] = METERING_TOP_10_df['SUM(CREDITS_USED)'].astype(float)
    # Multiselect list
    wh_selected = st.multiselect("Pick Warehouse:", list(METERING_TOP_10_df.index),['COMPUTE_WH', 'CADENS_WH', 'INTL_WH'])
    # filter using panda's .loc
    wh_to_show_df = METERING_TOP_10_df.loc[wh_selected]
    # Display the filtered df on the page.
    st.bar_chart(wh_to_show_df)

    st.header('Total warehouse usage over last 7 days')
    query = sql.WH_USAGE_LAST_7_DAYS
    WH_USAGE_LAST_7_DAYS_df = sf.sql_to_dataframe(query)    
    st.dataframe(WH_USAGE_LAST_7_DAYS_df)
    


if __name__ == "__main__":
    main()