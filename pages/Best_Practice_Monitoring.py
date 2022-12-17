import pandas as pd
import streamlit as st
from utils import snowflake_connector as sf
import utils.df_styler as sty
from utils import sql
import datetime

def main():

    # Apply formatting from the style.css file to the page
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # GLOBAL VARAIBLES
    default_width = 500

    #======================================================#
    # MAIN PAGE - INTRO
    #======================================================#
    
    st.title('Best Practice Monitoring')
    st.success(
    '''
    The **Best Practice Monitoring** page provides a number of figures to monitor Snowflake best practices\
    it is the intention that the analysis on this page be used as a method for identiying areas of a (functional team's)\
    snowflake workflow that could be optimised to further cut costs
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

    # EMPTY TABLES IN ACCOUNT
    st.header('Empty tables in account')
    query = sql.EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT
    EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df = sf.sql_to_dataframe(query)

    selection_rows = EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df['TABLE_SCHEMA'].str.contains('FINANCE')
    st.write(selection_rows)
    st.write(EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df['TABLE_SCHEMA'].isin(selection_rows))
    filtered_df = EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df.loc[EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df['TABLE_SCHEMA'].isin(selection_rows)]
    st.write(filtered_df)

    # st.write(EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df.loc(EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df['TABLE_SCHEMA'].str.contains('FINANCE')))
    # filtered_df = WH_CREDIT_BREAKDOWN_df.loc[WH_CREDIT_BREAKDOWN_df['WH_NAME'].isin(wh_selected)]

    # Colour formatting
    EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df = EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df.style.applymap(sty.make_red,
    subset=pd.IndexSlice[:,['EMPTY']])
    st.dataframe(EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df)

    with st.expander("What's this for?"):
        st.info('The dataframe above shows tables/views in the account that do not contain any data. This allows\
        unused/accidentally created tables to be identified and removed from the account'
        )

   # UNUSED TABLES IN ACCOUNT
    st.header('Unused tables in account')
    days = st.number_input('Number of days table/view has not been used:', value= 30)
    query = sql.UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT(days)
    UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT_df = sf.sql_to_dataframe(query)

    # Colour formatting
    UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT_df = UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT_df.style.applymap(sty.make_red,
    subset=pd.IndexSlice[:,['DAYS_UNUSED']])
    st.dataframe(UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT_df)

    with st.expander("What's this for?"):
        st.info('The dataframe above shows tables/views containing data that has not been used within the specified time period. It is\
        the intention that unused data be reviewed, to check for any tables/views that could be removed from the\
        account to reduce storage costs'
        )

   # TABLE AND VIEW TYPE SUMMARY
    st.header('Table and view type summary')

    with st.expander("What's this for?"):
        st.info('The dataframe above shows tables/views containing data that has not been used within the specified time period. It is\
        the intention that unused data be reviewed, to check for any tables/views that could be removed from the\
        account to reduce storage costs'
        )

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

    #======================================================#
    # MAIN PAGE: WAREHOUSES THAT DO NOT HAVE A RESOURCE MONITOR   
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Warehouses that do not have a resource monitor')
    st.write('Identify big aggregate functions that could be taking advantage of High performing functions')


if __name__ == "__main__":
    main()