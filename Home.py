# Imports 
import streamlit as st
from utils import snowflake_connector as sf
from utils import sql

# Page config settings
st.set_page_config(
    page_title="Usage Insights App"
    ,page_icon="🌀"
    ,layout="centered")

def main():

    # Make sure session state is preserved
    for key in st.session_state:
        st.session_state[key] = st.session_state[key]

    # Apply formatting to page
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    #======================================================#
    # SIDEBAR - SNOWFLAKE ACCOUNT PARAMETERS
    #======================================================#

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

    st.title("Welcome to the Usage Insights app!")

    st.sidebar.info("Choose a page above!")

    st.success(
    """
    This app provides insights on a demo Snowflake account usage.
    ### Get started!
    👈 Select a page in the sidebar!
    """
    )
    st.header("Understanding Snowflake's Cost Model")
    st.info('''
    At the highest level, snowflake charges you for three things: 
    \n
    1. **Compute costs:** are likely to constitute the largest portion of your bill and are based on\
    how long your warehouses are running and how much compute power they're using. Warehouses come\
    in a range of sizes, from x-small to 6X-large, with the price doubling between each tier.
    2. **Storage costs:** are typically lower than compute costs and are based on how much data you're\
    storing across tables, clones, and regions.
    3. **Data transfer costs:** are incurred when you transfer data between Snowflake regions, or to\
    another cloud provider. 
    \n
    Analysis in the Usage Insights App will attempt to minimise incurred costs in each of these areas\
    by highlighting key performance metrics and usage data across the snowflake account's objects and\
    users. All of the data and figures in this app have been generated using the metadata stored in the\
    snowflake account's metadata database (SNOWFLAKE). It is the intention that this app be used to actively\
    monitor key metrics in order to make changes that maximise resource usage efficiency and minimise\
    incurred costs.
    '''
    )

    st.header("Understanding the charging rates")

    st.info('''
    This section will list all of the costs associated with each activity in snowflake
    '''
    )

    st.header("Reducing Compute Costs")

    st.info('''
    1) **Choose the right size of warehouse:** For optimal query performance and cost\
    per credit
    2) **Suspend warehouses that are sitting idle:** To maximise warehouse utilisation
    3) **Update the query timeout default value:** The default value is 2 days\
    this is unlikely to be necessary for most cases
    4) **Use resource monitors:** to track credit usage and set up alerts
    5) **Split large files before ingestion:** to minimize processing overhead
    6) **Create alerts for reader accounts:** To ensure the costs don't run away
    7) **Identify inefficient queries:** By looking for spilling in the query profile, if so,\
    consider changing to a bigger warehouses
    8) **Identify cases of query queueing:** If so, either increase the size or have more clusters(preferred).
    9) **Take advantage of caching:** Especially in test environments
    10) **Have dedicated separate warehouses for ETLs and querying operations:** To optimize performance for each
    11) **Running short-duration queries in a shared warehouse:** To increase warehouse utilization.
    12) **Deprecate unused tables/objects:** Unload to an external location and delete table in snowflake to\
    save unnecessary storage costs.
    \n
    **Optimising scripts** to increase query efficiency
    1) **Delete all temporary and transient tables when done:**\
    Otherwise runs up storage costs for data that was meant to be 'temporary'
    2) **Use CREATE or REPLACE not CREATE TABLE AS:** ??
    3) **Apply COPY INTO, not INSERT INTO:** as it utilizes the more efficient bulk loading processes.
    4) **Leverage staging tables to transform imported data:** ??
    5) **Sort in the cloud service rather than ORDER BY:** ??
    6) **Use DISTINCT or GROUP BY:** To minimise redundancy
    7) **Take advantage of partition pruning:** Avoid select *, and Order By, Union. Use ANSI joins, Date/timestamp\
    type rather than varchar
    8) **Take advantage of High-Performance Functions**: Specifically for large datasets where drawing exact answers\
    is not completely necessary e.g data science tasks.
    9) **Ensure tasks are not left running by mistake:** As these will continue to execute queries
    '''
    )

    st.header("Reducing Storage Costs")

    st.info('''
    1) **Use zero-copy cloning**
    2) **Match bucket specifications with data transfer expectations:** e.g., are they organized\
    by date or by application?
    3) **Leverage parallel loading:** by restricting file size to 60-100 MB 
    4) **Avoid materialized views unless required:** e.g., pre-aggregating
    5) **Compress data before storage as much as possible:** Snowflake does not compress automatically in\
    all instances
    6) **Use transient tables as often as possible:** As they are not maintained in the history\
    tables therefore reduces costs for maintaining history tables.
    '''
    )

    st.header("Reducing Data Transfer Costs")
    
    st.info('''
    This section will list all of the costs associated with each activity in snowflake
    1) **Use S3 buckets in the same region as your data warehouse**
    '''
    )

    st.header("References")
    st.info('''
    https://www.finout.io/blog/snowflake-cost-reduction \
    https://hevodata.com/learn/snowflake-pricing/ \
    https://www.analytics.today/blog/top-14-snowflake-data-engineering-best-practices \
    https://docs.snowflake.com/en/user-guide/cost-controlling.html \
    https://blog.devgenius.io/snowflake-cost-saving-9e6b05aee0bd \
    https://www.snowflake.com/blog/10-best-practices-every-snowflake-admin-can-do-to-optimize-resources/ \
    '''
    )

if __name__ == "__main__":
    main()  
