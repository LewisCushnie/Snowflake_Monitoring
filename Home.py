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
    \n
    Listed below are a number of ways to reduce the costs associated with each of areas listed above:
    \n
    ### Reducing Compute Costs
    \n
    ### Reducing Storage Costs
    \n
    ### Reducing Data Transfer Costs
    '''
    )

    st.header("Understanding the charging rates")
    st.info('''
    This section will list all of the costs associated with each activity in snowflake
    '''
    )

    st.header("Reducing Compute Costs")
    st.info('''
    This section will list all of the costs associated with each activity in snowflake
    '''
    )

    st.header("Reducing Storage Costs")
    st.info('''
    This section will list all of the costs associated with each activity in snowflake
    '''
    )

    st.header("Reducing Data Transfer Costs")
    st.info('''
    This section will list all of the costs associated with each activity in snowflake
    '''
    )

    st.header("References")
    st.info('''
    https://www.finout.io/blog/snowflake-cost-reduction
    '''
    )

if __name__ == "__main__":
    main()  
