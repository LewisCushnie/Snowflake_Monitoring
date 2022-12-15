import streamlit as st

st.set_page_config(
    page_title="Usage Insights App"
    ,page_icon="🌀"
    ,layout="centered")

def main():
    # Make sure session state is preserved
    for key in st.session_state:
        st.session_state[key] = st.session_state[key]

    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
    st.title("Welcome to the Usage Insights app!")
    # st.sidebar.text(f"Account: {st.secrets.sf_usage_app.account}")
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
    1) Choose the right size of your warehouses
    2) Suspend warehouses that are sitting idle
    3) Update the query timeout default value
    4) Use resource monitors to track credit usage
    5) Split large files to minimize processing overhead
    6) Create alerts for reader accounts
    7) Identify inefficient queries: By looking for spilling in the query profile, if so,\ 
    consider changing to a bigger warehouses
    8) Identify cases of query queueing: If so, either increase the size or have more clusters(preferred).
    9) Take advantage of caching
    10) Have dedicated separate warehouses for ETLs and querying operations: To optimize performance for each
    11) Setting Appropriate non-default value for query timeout: The default value is 2 days\
    this is unlikely to be necessary for most cases
    12) Running short-duration queries in a shared warehouse: To increase warehouse utilization.
    13) Deprecate unused tables/objects: Unload to an external location and delete table in snowflake to\
    save unnecessary storage costs.
    \n
    **Optimising scripts** to increase query efficiency
    1) Delete all temporary and transient tables when done\
    Otherwise this runs up storage costs for data that was meant to be 'temporary'
    2) Use CREATE or REPLACE not CREATE TABLE AS: ??
    3) Apply COPY INTO, not INSERT INTO: because it utilizes the more efficient bulk loading processes.
    4) Leverage staging tables to transform imported data
    5) Remember those ANSI Joins are more efficient
    6) Remember to sort rather than ORDER BY where possible
    7) Don't tolerate redundancy; use DISTINCT or GROUP BY
    8) Take advantage of partition pruning: Avoid select *, and Order By, Union. Use ANSI joins, Date/timestamp\
    type rather than varchar
    9) Avoid row-by-row processing
    10) Take advantage of High-Performance Functions
    11) Ensure tasks are not left running by mistake
    '''
    )

    st.header("Reducing Storage Costs")
    st.info('''
    1) Use zero-copy cloning
    2) Use S3 buckets in the same region as your data warehouse
    3) Match your bucket specifications with your data transfer expectations, e.g., are they organized\
     by date or by application?
    4) Leverage parallel loading by restricting file size to 60–100 MB 
    5) Avoid using materialized views unless required (e.g., pre-aggregating)
    6) Make sure to have the data compressed before storage as much as possible. There are instances, \
    such as storing database tables, where Snowflake automatically does a data compression, however, \
    this is not always the case, so this is something to be mindful of and to be monitored regularly.
    7) Snowflake works better with the date or timestamp columns stored as such rather than them being \
    stored as type varchar.
    8) Try to make more use of transient tables as they are not maintained in the history tables which in \
    turn reduces the data storage costs for history tables.
    '''
    )

    st.header("Reducing Data Transfer Costs")
    st.info('''
    This section will list all of the costs associated with each activity in snowflake
    '''
    )

    st.header("References")
    st.info('''
    https://www.finout.io/blog/snowflake-cost-reduction \
    https://hevodata.com/learn/snowflake-pricing/ \
    https://www.analytics.today/blog/top-14-snowflake-data-engineering-best-practices \
    https://docs.snowflake.com/en/user-guide/cost-controlling.html \
    https://blog.devgenius.io/snowflake-cost-saving-9e6b05aee0bd \
    '''
    )

if __name__ == "__main__":
    main()  
