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
    streamlit_credits = STREAMLIT_CREDITS_USED_df.iloc[0]['SUM(CREDITS_USED_CLOUD_SERVICES)']
    streamlit_credits = round(streamlit_credits, 5)
    st.sidebar.metric("Credits used from streamlit queries", streamlit_credits)
    
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

    st.header("Metering Summary:")
    query = sql.METERING_HISTORY
    METERING_HISTORY_df = sf.sql_to_dataframe(query)
    st.dataframe(METERING_HISTORY_df)

    st.header('Warehouse credit usage')
    query = sql.METERING_TOP_10
    METERING_TOP_10_df = sf.sql_to_dataframe(query)
    st.dataframe(METERING_TOP_10_df)

    METERING_TOP_10_df = METERING_TOP_10_df.set_index('NAME')
    METERING_TOP_10_df['SUM(CREDITS_USED)'] = METERING_TOP_10_df['SUM(CREDITS_USED)'].astype(float)

    # # Multiselect list
    wh_selected = st.multiselect("Pick Warehouse:", list(METERING_TOP_10_df.index),['COMPUTE_WH', 'CADENS_WH', 'INTL_WH'])
    # filter using panda's .loc
    wh_to_show_df = METERING_TOP_10_df.loc[wh_selected]

    # Display the filtered df on the page.
    st.bar_chart(wh_to_show_df)

    # st.text('On/Off grid')
    # col1, col2, col3 = st.columns(3)
    # col1.metric("COMPUTE_WH", metering_top_10_df.loc['COMPUTE_WH', 'Credits Used'], 10)
    # col2.metric("Wind", "9 mph", "-8%")
    # col3.metric("Humidity", "86%", "4%")

    click = st.button('Snow baby!')

    if click:
        st.snow()
        click = False


if __name__ == "__main__":
    main()