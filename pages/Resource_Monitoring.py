import streamlit as st
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

    query = sql.TEST_QUERY
    TEST_QUERY_df = sf.sql_to_dataframe(query)
    st.dataframe(TEST_QUERY_df)

    query = sql.STREAMLIT_CREDITS_USED
    STREAMLIT_CREDITS_USED_df = sf.sql_to_dataframe(query)
    st.dataframe(STREAMLIT_CREDITS_USED_df)

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

    # # Convert to pandas dataframe
    # metering_top_10_df = pd.DataFrame(metering_top_10, columns=['WH_Name', 'Credits Used'])
    # metering_top_10_df = metering_top_10_df.set_index('WH_Name')
    # metering_top_10_df['Credits Used'] = metering_top_10_df['Credits Used'].astype(float)

    # # Multiselect list
    # wh_selected = st.multiselect("Pick Warehouse:", list(metering_top_10_df.index),['COMPUTE_WH', 'CADENS_WH', 'INTL_WH'])
    # # filter using panda's .loc
    # WH_to_show_df = metering_top_10_df.loc[wh_selected]

    # # Display the filtered df on the page.
    # st.bar_chart(WH_to_show_df, height= 500)

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