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

    #======================================================#
    # MAIN PAGE - TRANSIENT, TEMPORARY, AND MATERIALIZED VIEWS/TABLES
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Transient, Temporary, and Materialised Views/Tables')
    st.info('Transient and temporary are meant to be short-lived tables, check they are not persisting for\
     too long > suggest changing to permenant. Also, avoid using materialised view unless necessary.\
     Try to make more use of transient tables as they truncate history tables and save on storage costs')

    st.header('Empty tables in account')
    st.info('The table below shows tables/views containing data that has not been used within the specified time period. It is\
    the intention that unused data be reviewed, to check for any tables/views that could be removed from the\
    account to reduce storage costs')
    query = sql.EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT
    EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df = sf.sql_to_dataframe(query)
    st.dataframe(EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df)

    st.header('Unused tables in account')
    days = st.number_input('Number of days table/view has not been used:', value= 30)
    query = sql.UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT(days)
    UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT_df = sf.sql_to_dataframe(query)
    st.dataframe(UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT_df)

    #======================================================#
    # MAIN PAGE: COPY INTO V.S INSERT INTO
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Copy Into v.s Insert Into')
    st.write('Check why this matters')

    #======================================================#
    # MAIN PAGE: SORT V.S ORDER BY
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Sort v.s Order By')
    st.write('Check why this matters')

    #======================================================#
    # MAIN PAGE: HIGH PERFORMING FUNCTIONS
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('High Performing function usage')
    st.write('Identify big aggregate functions that could be taking advantage of High performing functions')

    #======================================================#
    # MAIN PAGE: ZERO COPY CLONING    
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Zero Copy Cloning Usage')
    st.write('Identify big aggregate functions that could be taking advantage of High performing functions')


if __name__ == "__main__":
    main()