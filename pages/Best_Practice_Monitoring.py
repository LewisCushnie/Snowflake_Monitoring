# Imports
import pandas as pd
import streamlit as st
import altair as alt
from utils import snowflake_connector as sf
import utils.df_styler as sty
from utils import sql
from utils import functions as fun
from utils.functions import add_logo

import datetime

def main():

    # Apply formatting from the style.css file to the page
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Define global variables
    default_width = 500

    #======================================================#
    # SIDEBAR - SNOWFLAKE ACCOUNT PARAMETERS
    #======================================================#

    # Sidebar logo
    add_logo()

    # Import query from the sql.py file then convert to dataframe
    query = sql.SNOWFLAKE_ACCOUNT_PARAMS
    df = sf.sql_to_dataframe(query)
    
    # Get current user
    df = df.transpose()
    current_user = df.loc['CURRENT_USER'].iloc[0]

    # Get current role
    role = df.loc['CURRENT_ROLE'].iloc[0]
    #st.sidebar.text(f'Current role - {role}')

    # Get current warehouse
    wh = df.loc['WAREHOUSE'].iloc[0]
    #st.sidebar.text(f'Warehouse - {wh}')

    # Display in sidebar
    st.sidebar.header(f'Hello, {current_user} ❄️')
    st.sidebar.markdown(
    f'''**Current Role** - {role}
     **Current Warehouse** - {wh}'''
    )

    #======================================================#
    # SIDEBAR - CREDITS USED THROUGH STREAMLIT
    #======================================================#

    # Import query from the sql.py file then convert to dataframe
    query = sql.STREAMLIT_CREDITS_USED
    STREAMLIT_CREDITS_USED_df = sf.sql_to_dataframe(query)

    # Get credits used, and credits remaining
    metric = round(STREAMLIT_CREDITS_USED_df['CREDITS_USED_STREAMLIT'].iloc[0], 5)
    remaining = round(100-metric, 3)

    # Display in sidebar
    st.sidebar.metric(label='**Credits used by Streamlit:**', value =metric, delta=f'{remaining} remaining')

    #======================================================#
    # MAIN PAGE - INTRO
    #======================================================#
    
    st.title('Snowflake Best Practice Monitoring')

    st.success(
    '''
    The **Best Practice Monitoring** page provides a number of figures to monitor Snowflake best practices.\
    It is the intention that the analysis on this page be used as a method for identiying areas of a (functional team's)\
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
    \n
    What are the costs in Snoflake?: https://docs.snowflake.com/en/user-guide/cost-understanding.html
    '''
    )

    #======================================================#
    # MAIN PAGE: TOTAL COMPUTE CREDITS PER DAY
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Total compute credit usage per day')

    st.info(
    '''
    💡 This section provides a summary of snowflake spending for the given selection
    \n
    **Note:** Cost assumes $4/credit
    '''
    )

    # Import query from the sql.py file then convert to dataframe
    query = sql.COMPUTE_CREDITS_PER_DAY
    COMPUTE_CREDITS_PER_DAY_df = sf.sql_to_dataframe(query)

    # Get min and max values from query date range
    min_date = COMPUTE_CREDITS_PER_DAY_df['Usage Week'].min()
    max_date = COMPUTE_CREDITS_PER_DAY_df['Usage Week'].max()
    auto_date_lower = min_date
    auto_date_higher = max_date

    # Create slider with min and max date values
    slider_values = st.slider(
    'Select date range',
    min_date, max_date, (auto_date_lower, auto_date_higher)
    )

    # Select DataFrame rows between the dates outputted from the slider
    date_mask = (COMPUTE_CREDITS_PER_DAY_df['Usage Week'] > slider_values[0]) &\
     (COMPUTE_CREDITS_PER_DAY_df['Usage Week'] <= slider_values[1])
    filtered_df = COMPUTE_CREDITS_PER_DAY_df.loc[date_mask]

    # Create selectbox for currency selection
    selection = st.selectbox(
    'Select currency:', 
    ('Cost ($)', 'Credits used'))

    if selection == 'Credits used':
        # Credits bar chart
        st.bar_chart(filtered_df, x= 'Usage Week', y= 'Compute Credits Used')

    elif selection == 'Cost ($)':
        # Cost bar chart
        st.bar_chart(filtered_df, x= 'Usage Week', y= 'Cost ($)')
        
    else:
        pass

    # Create checkbox for raw data display 
    raw_data = st.checkbox('Show raw data:', key= 'Total compute credit usage per day')

    if raw_data:
        # Apply color formatting to dataframe
        st.text('Red - $10+ per day | Orange - $5-$10 per day | Green - Less than $5 per day')
        filtered_df = filtered_df.style.applymap(colour_df,
        subset=pd.IndexSlice[:,['Cost ($)']])

        # Display dataframe
        st.dataframe(filtered_df, width=1000)
    
    with st.expander("What's this for?"):
        st.info('''
        💡 This figure allows you to investigate trends in credit spending on the snowflake account.
        This should act as a starting point to understand what the current spending habits and projections are,
        and therefore informs which of the following figures are likely to be of benefit. 
        \n
        **Benefit:** Provides a high-level overview of spending.
        '''
        )

    #======================================================#
    # MAIN PAGE - TABLE AND VIEW MONITORING
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Table and View monitoring')

    st.info('💡 This section provides analysis on the account\'s tables and views \n \
    \n What are the different table types? https://docs.snowflake.com/en/user-guide/tables-temp-transient.html\
    \n What are the different view types? https://docs.snowflake.com/en/user-guide/views-introduction.html')

    # ------------- EMPTY TABLES IN ACCOUNT -----------------
    st.subheader('Empty tables and views in account')

    # Import query from the sql.py file then convert to dataframe
    query = sql.EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT
    EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df = sf.sql_to_dataframe(query)
    
    # Generate the business domain filter options
    filtered_df = fun.filter_df_by_business_domain(EMPTY_TABLES_AND_VIEWS_IN_ACCOUNT_df,\
     'TABLE_SCHEMA', unique_key= 'Empty tables in account')

    if len(filtered_df) != 0:

        # Colour formatting
        filtered_df = filtered_df.style.applymap(sty.make_red,
        subset=pd.IndexSlice[:,['EMPTY']])

        # Display dataframe
        st.dataframe(filtered_df, use_container_width= True)

    else:
        # Message to show if no matches from the filter
        st.success('There are no empty tables or views in the selection 😀')

    with st.expander("What's this for?"):
        st.info('''
        💡 The dataframe above shows tables/views in the account that do not contain any data. This allows
        unused/accidentally created tables to be identified and removed from the account.
        \n
        **Benefit:** Reduced storage costs, and clutter on the account.
        '''
        )

   # ---------------- UNUSED TABLES IN ACCOUNT ------------------------
    st.subheader('Unused tables and views in account')

    # User input for number of days to look back
    days = st.number_input('Number of days table/view has not been used:', value= 30)

    # Import query from the sql.py file then convert to dataframe
    query = sql.UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT(days)
    UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT_df = sf.sql_to_dataframe(query)

    # Generate the business domain filter options
    filtered_df = fun.filter_df_by_business_domain(UNUSED_TABLES_AND_VIEWS_IN_ACCOUNT_df\
    ,'TABLE_SCHEMA' ,unique_key= 'Unused tables in account')

    if len(filtered_df) != 0:

        # Colour formatting
        filtered_df = filtered_df.style.applymap(sty.make_red,
        subset=pd.IndexSlice[:,['DAYS_UNUSED']])

        # Display dataframe
        st.dataframe(filtered_df)

    else:
        # Message to show if no matches from the filter
        st.success('There are no unused tables in the selection 😀')

    with st.expander("What's this for?"):
        st.info('''
        💡 The dataframe above shows tables/views containing data that has not been used within the specified time period. It is
        the intention that unused data be reviewed, to check for any tables/views that could be removed from the
        account to reduce storage costs.
        \n
        **Benefit:** Dropping debricated tables (after moving to another location) reduces storage costs.
        '''
        )

   # ----------------- TABLE AND VIEW TYPE SUMMARY ----------------------
    st.subheader('Table and view type summary')

    # Import query from the sql.py file then convert to dataframe
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

    # Dipslay altair chart
    st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

    # Raw data checkbox
    raw_data = st.checkbox('Show raw data', key= 'Table and view type summary')
    if raw_data:

        # Display dataframe
        st.dataframe(TABLE_AND_VIEW_BREAKDOWN_df)

    with st.expander("What's this for?"):
        st.info('''
        💡 The bar chart above shows a breakdown of each table and view type in the selected location. This can be used to
        monitor the usage of each type, and better understand which data has time-travel enabled and which does not.
        Consider noting any table types which are not used much, or used a lot. Remember, transient and temporary tables/views
        help save on storage costs, whereas permenant tables/views offer time-travel and fail-safe protection. Be sure to check
        that the benefits of each are being used appropriately.
        \n
        **Benefit:** Monitoring table/view usage helps ensure storage costs are minimised, and the correct data is backed up.\n
        **Snowflake docs:** 
        \n
        https://docs.snowflake.com/en/user-guide/tables-temp-transient.html \n
        https://docs.snowflake.com/en/user-guide/views-introduction.html
        '''
        )

    #======================================================#
    # MAIN PAGE: WAREHOUSE MONITORING
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Warehouse monitoring')  

    st.info('💡 This section provides analysis on the account\'s warehouses \n \
    \n What is a warehouse?: https://docs.snowflake.com/en/user-guide/warehouses-overview.html')  

   # ----------------- WAREHOUSES WITHOUT MONITOR ----------------------
    st.subheader('Warehouses that do not have a resource monitor')

    # Import query from the sql.py file then convert to dataframe
    query = sql.WAREHOUSE_DETAILS
    WAREHOUSE_DETAILS_df = sf.sql_to_dataframe(query)

    # Select rows where there is no resource monitor
    WAREHOUSE_DETAILS_df = WAREHOUSE_DETAILS_df[['name', 'resource_monitor','owner', 'updated_on']]
    WAREHOUSE_DETAILS_df = WAREHOUSE_DETAILS_df[WAREHOUSE_DETAILS_df['resource_monitor'] == 'null']

    # Generate the business domain filter options
    filtered_df = fun.filter_df_by_business_domain(WAREHOUSE_DETAILS_df\
    ,'name' ,unique_key= 'Warehouses that do not have a resource monitor')

    if len(filtered_df) != 0:

        # Colour formatting
        filtered_df = filtered_df.style.applymap(sty.make_red,
        subset=pd.IndexSlice[:,['resource_monitor']])

        # Display dataframe
        st.dataframe(filtered_df)

    else:
        st.success('There are no warehouses without a resource monitor in the selection 😀')
    
    with st.expander("What's this for?"):
        st.info('''
        💡 It is good practice to ensure that all warehouses have a resource monitor attached to them to
        prevent excessive credit spending from going un-noticed.
        \n
        **Benefit:** Save compute costs by preventing warehouses from using large amounts of credits due
        to mistakes, ineffecient queries, etc.
        '''
        )

   # ----------------- WAREHOUSE UTILIZATION SUMMARY ----------------------
    st.subheader('Warehouse utilisation summary over previous n days')

    # User input for number of days selection
    days = st.number_input('Previous n days:', value= 30, key= 'Warehouse utilisation - Summary')

    # Import query from the sql.py file then convert to dataframe
    query = sql.WAREHOUSE_UTILIZATION_LAST_N_DAYS(days)
    WAREHOUSE_UTILIZATION_LAST_N_DAYS_df = sf.sql_to_dataframe(query)

    # Select necessary rows
    WAREHOUSE_UTILIZATION_LAST_N_DAYS_df = \
    WAREHOUSE_UTILIZATION_LAST_N_DAYS_df[['WAREHOUSE_NAME', 
                                        'COMPUTE_AVAILABILITY_SEC', 
                                        'TOTAL_EXEC_TIME_SEC', 
                                        'PCT_UTILIZATION']]

    # Generate business domain filter options using the filter_df_by_business_domain function
    WAREHOUSE_UTILIZATION_LAST_N_DAYS_df = fun.filter_df_by_business_domain(WAREHOUSE_UTILIZATION_LAST_N_DAYS_df\
    ,'WAREHOUSE_NAME' ,unique_key= '(2.0) Warehouse utilisation - Summary')

    utilisation = st.checkbox('Show warehouse utlisation:', key= '(2.0) Warehouse utilisation - Summary')
    if utilisation:
        # Select necessary columns and divide by 100 to get correct percentage
        filtered_df = WAREHOUSE_UTILIZATION_LAST_N_DAYS_df[['WAREHOUSE_NAME', 
                                                            'PCT_UTILIZATION']]
        filtered_df['PCT_UTILIZATION'] = filtered_df['PCT_UTILIZATION'].div(100)

        # Create altair chart
        chart = alt.Chart(filtered_df.reset_index()).mark_bar().encode(
        x= alt.X('WAREHOUSE_NAME'),
        y= alt.Y('PCT_UTILIZATION:Q', axis= alt.Axis(title= 'Percentage Warehouse Utilisation', format= '%')),
        )

        # Display altair chart
        st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

    else:
        # Select necessary columns
        filtered_df = WAREHOUSE_UTILIZATION_LAST_N_DAYS_df[['WAREHOUSE_NAME', 
                                                        'TOTAL_EXEC_TIME_SEC', 
                                                        'COMPUTE_AVAILABILITY_SEC']]

        # Create altair chart
        chart = alt.Chart(filtered_df.reset_index()).transform_fold(
        ['TOTAL_EXEC_TIME_SEC', 'COMPUTE_AVAILABILITY_SEC'],
        as_=['CATEGORY', 'TIME']
        ).mark_bar().encode(
        x= alt.X('WAREHOUSE_NAME'),
        y= alt.Y('TIME:Q'),
        color= 'CATEGORY:N'
        )

        # Display altair chart
        st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

    with st.expander("What's this for?"):
        st.info('''
        💡 It is good practice to ensure that all warehouses have a resource monitor attached to them to
        prevent excessive credit spending from going un-noticed.
        \n
        **Benefit:** Save compute costs by preventing warehouses from using large amounts of credits due
        to mistakes, ineffecient queries, etc.
        '''
        )

    # Raw data checkbox
    raw_data = st.checkbox('Show raw data:', key= 'Warehouse utilisation - Summary raw data')
    if raw_data:
        st.dataframe(filtered_df)

   # ----------------- WAREHOUSE UTILIZATION BY HOUR ----------------------
    st.subheader('Warehouse utilisation by hour over previous 48 hours')

    # Import query from the sql.py file then convert to dataframe
    query = sql.WAREHOUSE_DETAILS
    WAREHOUSE_DETAILS_df = sf.sql_to_dataframe(query)

    # Convert warehouse names to list
    WAREHOUSE_NAMES_LIST = WAREHOUSE_DETAILS_df['name'].tolist()

    # Create warehouse name selectbox
    wh_name = st.selectbox(
    'Select a warehouse to see hourly data for:',
    WAREHOUSE_NAMES_LIST)

    # Import query from the sql.py file then convert to dataframe
    query = sql.WH_UTILIZATION_LAST_48_HOURS(wh_name)
    WH_UTILIZATION_LAST_48_HOURS_df = sf.sql_to_dataframe(query)

    utilisation = st.checkbox('Show warehouse utlisation:', key= '(2.1) Warehouse utilisation - Utilisation by hour')
    if utilisation:
        # Select necessary rows and divide by 100 to get correct percentage
        filtered_df = WH_UTILIZATION_LAST_48_HOURS_df[['HOUR', 
                                                        'PCT_UTILIZATION']]
        filtered_df['PCT_UTILIZATION'] = filtered_df['PCT_UTILIZATION'].div(100)

        # Create altair chart
        chart = alt.Chart(filtered_df.reset_index()).mark_bar().encode(
        x= alt.X('HOUR'),
        y= alt.Y('PCT_UTILIZATION:Q', axis= alt.Axis(title= 'Percentage Warehouse Utilisation', format= '%')),
        )

        # Display altair chart
        st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

    else:
        # Select necessary rows
        filtered_df = WH_UTILIZATION_LAST_48_HOURS_df[['HOUR', 
                                                        'TOTAL_EXEC_TIME_SEC', 
                                                        'COMPUTE_AVAILABILITY_SEC']]

        # Create altair chart
        chart = alt.Chart(filtered_df.reset_index()).transform_fold(
        ['TOTAL_EXEC_TIME_SEC', 'COMPUTE_AVAILABILITY_SEC'],
        as_=['CATEGORY', 'TIME']
        ).mark_bar().encode(
        x= alt.X('HOUR'),
        y= alt.Y('TIME:Q'),
        color= 'CATEGORY:N'
        )

        # Display altair chart
        st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

    # Raw data checkbox
    raw_data = st.checkbox('Show raw data:', key= 'Compute availablity v.s execution time by hour')
    if raw_data:
        st.dataframe(filtered_df)

    with st.expander("What's this for?"):
        st.info('''
        💡 Definition of Warehouse Utilization:

        Warehouse utilization here is calculated with a simple formula, namely #seconds execution time
         / # seconds of compute availability.  The numerator is the # seconds of execution time for all 
         queries running during the period.  The denominator is # seconds of compute availability during 
         the period.  This availability piggybacks on the easily available credits used during the period 
         being measured, since that is already accurately captured for all warehouse sizes, and even 
         accounts for warehouse resizing during the period.  

        Availability in seconds = credits_used * 60 *60.  For example, an extra small WH costs 1 credit 
        per hour, meaning 1 credit = 1 hour of compute availability.  Therefore, a single credit hour equals
         3,600 seconds of credit availability.  Although it could be argued that there are 8 threads per XS 
         Warehouse, and it could be fully loaded with queries, in testing it let to embarrassingly low 
         utilization rates for most warehouses.  On a data warehouse, multiple threads are usually used to 
         process single queries in parallel.  Not accounting for the threads works well for comparison purposes.

        '''
        )

    # ===========================================#
    # MAIN PAGE - ACCOUNT TASK RUN TRACKER
    # ===========================================#

    line = '---'
    st.markdown(line)
    st.header('Task Monitoring Summary')

    st.info('''
    💡 This section provides analysis on tasks in the account.
    \n
    What is a task?: https://docs.snowflake.com/en/user-guide/tasks-intro.html
    ''')

   # ----------------- TASK STATUS SUMMARY ----------------------
    st.subheader('Task status summary')

    # Import query from the sql.py file then convert to dataframe
    query = sql.SHOW_TASKS
    SHOW_TASKS_df = sf.sql_to_dataframe(query)

    # Select necessary rows
    SHOW_TASKS_df = SHOW_TASKS_df[['name', 'warehouse', 'schedule', 'state']]

    # Colour formatting
    SHOW_TASKS_df = SHOW_TASKS_df.style.applymap(sty.make_red,
    subset=pd.IndexSlice[:,['state']])

    # Display dataframe
    st.dataframe(SHOW_TASKS_df)

    with st.expander("What's this for?"):
        st.info('''
        💡 The dataframe above shows the state of tasks in the selection (suspended/running). 
        \n
        **Benefit:** At a glance, you can see all tasks in the account, and whether they are
        running or not.
        '''
        )

   # ----------------- TASK HISTORY TRACKER ----------------------
    st.subheader('Task success history')

    # Import query from the sql.py file then convert to dataframe
    query = sql.TASK_HISTORY
    SHOW_TASKS_df = sf.sql_to_dataframe(query)

    # Create altair chart
    chart = alt.Chart(SHOW_TASKS_df).transform_fold(
    ['COUNT_SUCCEEDED', 'COUNT_FAILED'],
    as_=['STATUS', 'COUNT']
    ).mark_bar().encode(
    x= alt.X('NAME', sort= '-y'),
    y= alt.Y('COUNT:Q'),
    color= 'STATUS:N'
    )
    
    # Display altair chart
    st.altair_chart(chart, use_container_width= True, theme= 'streamlit')
    
    raw_data = st.checkbox('Show raw task history data:')
    if raw_data:
        st.dataframe(SHOW_TASKS_df)

    with st.expander("What's this for?"):
        st.info('''
        💡 The figure above shows the success and failure count for each task in the selection.
        High rates of failure might indicate a task that needs re-working.
        \n
        **Benefit:** This figure can alert you to any problematic tasks that fail regularly.
        Remember, you are still charged for task runtime even when they fail.
        '''
        )

    #======================================================#
    # MAIN PAGE: COPY INTO V.S INSERT INTO
    #======================================================#

    line = '---'
    st.markdown(line)
    st.subheader('Copy Into v.s Insert Into')
    st.write('Check why this matters')

    #======================================================#
    # MAIN PAGE: SORT V.S ORDER BY
    #======================================================#

    line = '---'
    st.markdown(line)
    st.subheader('Queries that contain an Order By')
    st.write('Check why this matters')

    #======================================================#
    # MAIN PAGE: HIGH PERFORMING FUNCTIONS
    #======================================================#

    line = '---'
    st.markdown(line)
    st.subheader('High Performing function usage')
    st.write('Identify big aggregate functions that could be taking advantage of High performing functions')

    #======================================================#
    # MAIN PAGE: ZERO COPY CLONING    
    #======================================================#

    line = '---'
    st.markdown(line)
    st.subheader('Zero Copy Cloning Usage')
    st.write('Identify big aggregate functions that could be taking advantage of High performing functions')

    #======================================================#
    # MAIN PAGE: WAREHOUSES THAT DONT HAVE A TAG    
    #======================================================#

    line = '---'
    st.markdown(line)
    st.subheader('Warehouse without a tag')
    st.write('Identify big aggregate functions that could be taking advantage of High performing functions')

    #======================================================#
    # MAIN PAGE: QUERIES THAT SPILL TO DISC
    #======================================================#

    line = '---'
    st.markdown(line)
    st.subheader('Queries that spill to disc')
    st.write('Identify big aggregate functions that could be taking advantage of High performing functions')

    #======================================================#
    # MAIN PAGE: PARTITION PRUNING
    #======================================================#

    line = '---'
    st.markdown(line)
    st.subheader('Taking advantage of partition pruning')
    st.write('''
    SELECT * usage
    ORDER BY usage
    WHERE usage
    ''')


if __name__ == "__main__":
    main()