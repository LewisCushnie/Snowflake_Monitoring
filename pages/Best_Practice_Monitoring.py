import pandas as pd
import streamlit as st
import altair as alt
from utils import snowflake_connector as sf
import utils.df_styler as sty
from utils import sql
from utils import functions as fun
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
    snowflake workflow that could be optimised to further cut costs. 
    \n
    Remeber, at the highest level, snowflake charges you for three things: 
    \n
    1. **Compute costs:** are likely to constitute the largest portion of your bill and are based on\
    how long your warehouses are running and how much compute power they're using. Warehouses come\
    in a range of sizes, from x-small to 6X-large, with the price doubling between each tier.
    2. **Storage costs:** are typically lower than compute costs and are based on how much data you're\
    storing across tables, clones, and regions.
    3. **Data transfer costs:** are incurred when you transfer data between Snowflake regions, or to\
    another cloud provider. 
    \n
    The analysis in this app has been included to help ensure Snowflake best practices are being maintained to reduce costs
    in the three areas listed above.
    '''
    )

    #======================================================#
    # MAIN PAGE - TRANSIENT, TEMPORARY, AND MATERIALIZED VIEWS/TABLES
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Table and View monitoring')
    st.info('This section provides analysis on the account\'s tables and views')

    # EMPTY TABLES IN ACCOUNT
    st.header('(1) Empty tables and views in account')
    query = sql.EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT
    EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df = sf.sql_to_dataframe(query)
    
    # Generate the business domain filter options
    filtered_df = fun.filter_df_by_business_domain(EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df, unique_key= 'Empty tables in account')

    # Colour formatting
    filtered_df = filtered_df.style.applymap(sty.make_red,
    subset=pd.IndexSlice[:,['EMPTY']])
    st.dataframe(filtered_df, use_container_width= True)

    with st.expander("What's this for?"):
        st.info('''
        The dataframe above shows tables/views in the account that do not contain any data. This allows
        unused/accidentally created tables to be identified and removed from the account.
        **Benefit:** Reduced storage costs, and clutter on the account.
        '''
        )

   # UNUSED TABLES IN ACCOUNT
    st.header('(2) Unused tables and views in account')
    days = st.number_input('Number of days table/view has not been used:', value= 30)

    query = sql.UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT(days)
    UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT_df = sf.sql_to_dataframe(query)

    # Generate the business domain filter options
    filtered_df = fun.filter_df_by_business_domain(UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT_df, unique_key= 'Unused tables in account')

    # Colour formatting
    filtered_df = filtered_df.style.applymap(sty.make_red,
    subset=pd.IndexSlice[:,['DAYS_UNUSED']])
    st.dataframe(filtered_df)

    with st.expander("What's this for?"):
        st.info('''
        The dataframe above shows tables/views containing data that has not been used within the specified time period. It is
        the intention that unused data be reviewed, to check for any tables/views that could be removed from the
        account to reduce storage costs.
        **Benefit:** Dropping debricated tables (after moving to another location) reduces storage costs.
        '''
        )

   # TABLE AND VIEW TYPE SUMMARY
    st.header('(3) Table and view type summary')

    query = sql.TABLE_AND_VIEW_BREAKDOWN
    TABLE_AND_VIEW_BREAKDOWN_df = sf.sql_to_dataframe(query)

    # Create altair chart
    chart = alt.Chart(TABLE_AND_VIEW_BREAKDOWN_df.reset_index()).transform_fold(
    ['VIEW_COUNT', 'MATERIALIZED_VIEW_COUNT', 'BASE_TABLE_COUNT', 'EXTERNAL_TABLE_COUNT'],
    as_=['TYPE', 'COUNT']
    ).mark_bar().encode(
    x= alt.X('TYPE:N', sort= '-y', axis=alt.Axis(labels=False)),
    y= alt.Y('COUNT:Q'),
    color= 'TYPE:N'
    )
    st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

    # Raw data checkbox
    raw_data = st.checkbox('Show raw data', key= 'Table and view type summary')
    if raw_data:
        st.dataframe(TABLE_AND_VIEW_BREAKDOWN_df)

    with st.expander("What's this for?"):
        st.info('''
        The bar chart above shows a breakdown of each table and view type in the selected location. This can be used to
        monitor the usage of each type, and better understand which data has time-travel enabled and which does not.
        Consider noting any table types which are not used much, or used a lot. Remember, transient and temporary tables/views
        help save on storage costs, whereas permenant tables/views offer time-travel and fail-safe protection. Be sure to check
        that the benefits of each are being used appropriately.\n
        **Benefit:** Monitoring table/view usage helps ensure storage costs are minimised, and the correct data is backed up.\n
        **Snowflake docs:** \n
        https://docs.snowflake.com/en/user-guide/tables-temp-transient.html \n
        https://docs.snowflake.com/en/user-guide/views-introduction.html
        '''
        )

    #======================================================#
    # MAIN PAGE: WAREHOUSES THAT DO NOT HAVE A RESOURCE MONITOR   
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Warehouses that do not have a resource monitor')
    st.write('Identify big aggregate functions that could be taking advantage of High performing functions')

    query = sql.WAREHOUSE_DETAILS
    WAREHOUSE_DETAILS_df = sf.sql_to_dataframe(query)
    WAREHOUSE_DETAILS_df = WAREHOUSE_DETAILS_df[['name', 'resource_monitor','owner', 'updated_on']]

    # Colour formatting
    WAREHOUSE_DETAILS_df = WAREHOUSE_DETAILS_df.style.applymap(sty.make_red,
    subset=pd.IndexSlice[:,['resource_monitor']])

    st.dataframe(WAREHOUSE_DETAILS_df)

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
    st.header('Queries that contain an Order By')
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