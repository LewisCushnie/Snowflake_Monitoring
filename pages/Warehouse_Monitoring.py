import pandas as pd
import streamlit as st
import altair as alt
from utils import snowflake_connector as sf
from utils.df_styler import colour_df
from utils.functions import add_logo
from utils import sql
import datetime

def main():

    # Apply formatting from the style.css file to the page
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # GLOBAL VARAIBLES
    default_width = 500

    #======================================================#
    # SIDEBAR - WAREHOUSE USAGE SUMMARY STATS
    #======================================================#

    # Add logo
    add_logo()

    st.sidebar.header('Warehouse usage summary stats')
    query = sql.WH_USAGE_LAST_7_DAYS
    WH_USAGE_LAST_7_DAYS_df = sf.sql_to_dataframe(query)
    metric=round(WH_USAGE_LAST_7_DAYS_df['CREDITS_USED_LAST_PERIOD'].iloc[0],5)
    pct_change=round(WH_USAGE_LAST_7_DAYS_df['PCT_CHANGE'].iloc[0],3)
    st.sidebar.metric(label='Credit usage over last 7 day period', value= metric, delta= f'{pct_change}%', delta_color= "inverse")

    #======================================================#
    # SIDEBAR - MOST USED WAREHOUSE
    #======================================================#

    query = sql.WH_CREDIT_BREAKDOWN
    WH_CREDIT_BREAKDOWN_df = sf.sql_to_dataframe(query)

    # Most used warehouse
    most_used_loc = WH_CREDIT_BREAKDOWN_df['TOTAL_CREDITS'].idxmax()
    most_used_wh = WH_CREDIT_BREAKDOWN_df['WH_NAME'].iloc[most_used_loc]

    amount_used = round(WH_CREDIT_BREAKDOWN_df['TOTAL_CREDITS'].iloc[most_used_loc], 3)
    st.sidebar.metric(label='Most used warehouse', value= most_used_wh, delta= f'{amount_used} Credits', delta_color= "normal")

    #======================================================#
    # MAIN PAGE - INTRO
    #======================================================#

    st.title('Resource Monitoring Summary')
    st.success(
    '''
    The **Resource Monitoring Summary** page provides a breakdown of resource useage within each Snowflake account highlighting
    how and where credits are being consumed. The aim is to allow easy identification of inefficient or missused resources.
    '''
    )

    #======================================================#
    # MAIN PAGE: WAREHOUSE CREDIT USAGE BREAKDOWN
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Warehouse credit usage breakdown')

    query = sql.WH_CREDIT_BREAKDOWN
    WH_CREDIT_BREAKDOWN_df = sf.sql_to_dataframe(query)
    WH_CREDIT_BREAKDOWN_df['TOTAL_CREDITS'] = WH_CREDIT_BREAKDOWN_df['TOTAL_CREDITS'].astype(float)

    selection = st.selectbox(
    'Select warehouse analysis type:', 
    ('Warehouse comparison', 'n most used warehouses'))
    
    if selection == 'Warehouse comparison':

        # Top 5 most used warehouses
        five_most_used_df = WH_CREDIT_BREAKDOWN_df['TOTAL_CREDITS'].nlargest(5)
        five_most_used_wh_list = WH_CREDIT_BREAKDOWN_df['WH_NAME'].iloc[five_most_used_df.index].tolist()

        # Multiselect list
        wh_selected = st.multiselect("Pick Warehouse (5 most used warehouses selected by default):",\
        list(WH_CREDIT_BREAKDOWN_df['WH_NAME']), five_most_used_wh_list)
        filtered_df = WH_CREDIT_BREAKDOWN_df.loc[WH_CREDIT_BREAKDOWN_df['WH_NAME'].isin(wh_selected)]

        # st.altair_chart(chart, use_container_width= True, theme= 'streamlit')
        percentage = st.checkbox('Show as percentages:')
        if percentage:
            WH_CREDIT_df = filtered_df[['WH_NAME','PERC_COMPUTE', 'PERC_CLOUD']]

            # Create altair chart
            chart = alt.Chart(WH_CREDIT_df.reset_index()).transform_fold(
            ['PERC_COMPUTE', 'PERC_CLOUD'],
            as_=['CATEGORY', 'PERCENTAGE']
            ).mark_bar().encode(
            x= alt.X('WH_NAME', sort= '-y'),
            y= alt.Y('PERCENTAGE:Q'),
            color= 'CATEGORY:N'
            )
            st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

        else:
            WH_CREDIT_df = filtered_df[['WH_NAME','COMPUTE_CREDITS', 'CLOUD_SERVICES_CREDITS']]

            # Create altair chart
            chart = alt.Chart(filtered_df.reset_index()).transform_fold(
            ['COMPUTE_CREDITS', 'CLOUD_SERVICES_CREDITS'],
            as_=['CATEGORY', 'CREDITS']
            ).mark_bar().encode(
            x= alt.X('WH_NAME', sort= '-y'),
            y= alt.Y('CREDITS:Q'),
            color= 'CATEGORY:N'
            )
            st.altair_chart(chart, use_container_width= True, theme= 'streamlit')
        
    
    elif selection == 'n most used warehouses':

        # Top n highest total credit usage warehouses
        n_largest = st.number_input('Select n highest credit usage warehouses:', step= 1, value= 5)
        WH_CREDIT_BREAKDOWN_TOP_N = WH_CREDIT_BREAKDOWN_df['TOTAL_CREDITS'].nlargest(n_largest)
        filtered_df = WH_CREDIT_BREAKDOWN_df.iloc[WH_CREDIT_BREAKDOWN_TOP_N.index]

        percentage = st.checkbox('Show as percentages:')
        if percentage:
            WH_CREDIT_df = filtered_df[['WH_NAME','PERC_COMPUTE', 'PERC_CLOUD']]

            # Create altair chart
            chart = alt.Chart(WH_CREDIT_df.reset_index()).transform_fold(
            ['PERC_COMPUTE', 'PERC_CLOUD'],
            as_=['CATEGORY', 'PERCENTAGE']
            ).mark_bar().encode(
            x= alt.X('WH_NAME', sort= '-y'),
            y= alt.Y('PERCENTAGE:Q'),
            color= 'CATEGORY:N'
            )
            st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

        else:
            WH_CREDIT_df = filtered_df[['WH_NAME','COMPUTE_CREDITS', 'CLOUD_SERVICES_CREDITS']]

            # Create altair chart
            chart = alt.Chart(filtered_df.reset_index()).transform_fold(
            ['COMPUTE_CREDITS', 'CLOUD_SERVICES_CREDITS'],
            as_=['CATEGORY', 'CREDITS']
            ).mark_bar().encode(
            x= alt.X('WH_NAME', sort= '-y'),
            y= alt.Y('CREDITS:Q'),
            color= 'CATEGORY:N'
            )
            st.altair_chart(chart, use_container_width= True, theme= 'streamlit')
    
    else:
        pass

    # Raw data checkbox
    raw_data = st.checkbox('Show raw data', key= 'Warehouse credit usage breakdown')
    if raw_data:
        st.dataframe(WH_CREDIT_df)

    #======================================================#
    # MAIN PAGE: COMPUTE CREDITS PER DAY
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Total compute credit usage per day')

    st.write('Cost assumes $4/credit')
    query = sql.COMPUTE_CREDITS_PER_DAY
    COMPUTE_CREDITS_PER_DAY_df = sf.sql_to_dataframe(query)

    # Add slider:
    min_date = COMPUTE_CREDITS_PER_DAY_df['Usage Week'].min()
    max_date = COMPUTE_CREDITS_PER_DAY_df['Usage Week'].max()
    auto_date_lower = min_date
    auto_date_higher = max_date
    slider_values = st.slider(
    'Select date range',
    min_date, max_date, (auto_date_lower, auto_date_higher)
    )

    # Select DataFrame rows between two dates
    date_mask = (COMPUTE_CREDITS_PER_DAY_df['Usage Week'] > slider_values[0]) &\
     (COMPUTE_CREDITS_PER_DAY_df['Usage Week'] <= slider_values[1])
    filtered_df = COMPUTE_CREDITS_PER_DAY_df.loc[date_mask]

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

    # Raw data checkbox
    raw_data = st.checkbox('Show raw data:', key= 'Total compute credit usage per day')
    if raw_data:
        st.text('Red - $10+ per day | Orange - $5-$10 per day | Green - Less than $5 per day')
        filtered_df = filtered_df.style.applymap(colour_df,
        subset=pd.IndexSlice[:,['Cost ($)']])
        st.dataframe(filtered_df, width=1000)

    #======================================================#
    # MAIN PAGE: COMPUTE AVAILABILITY VS EXECUTION TIME
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Compute availablity v.s execution time by hour')

    query = sql.COMPUTE_AVAILABILITY_AND_EXECUTION_TIME
    COMPUTE_AVAILABILITY_AND_EXECUTION_TIME_df = sf.sql_to_dataframe(query)

    utilisation = st.checkbox('Show warehouse utlisation:')
    if utilisation:
        filtered_df = COMPUTE_AVAILABILITY_AND_EXECUTION_TIME_df[['HOUR', 'PCT_UTILIZATION']]
        filtered_df['PCT_UTILIZATION'] = filtered_df['PCT_UTILIZATION'].div(100)

        # Create altair chart
        chart = alt.Chart(filtered_df.reset_index()).mark_bar().encode(
        x= alt.X('HOUR'),
        y= alt.Y('PCT_UTILIZATION:Q', axis= alt.Axis(title= 'Percentage Warehouse Utilisation', format= '%')),
        )
        st.altair_chart(chart, use_container_width= True, theme= 'streamlit')
    else:
        filtered_df = COMPUTE_AVAILABILITY_AND_EXECUTION_TIME_df[['HOUR', 'TOTAL_EXEC_TIME_SEC', 'COMPUTE_AVAILABILITY_SEC']]

        # Create altair chart
        chart = alt.Chart(filtered_df.reset_index()).transform_fold(
        ['TOTAL_EXEC_TIME_SEC', 'COMPUTE_AVAILABILITY_SEC'],
        as_=['CATEGORY', 'TIME']
        ).mark_bar().encode(
        x= alt.X('HOUR'),
        y= alt.Y('TIME:Q'),
        color= 'CATEGORY:N'
        )
        st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

    # Raw data checkbox
    raw_data = st.checkbox('Show raw data:', key= 'Compute availablity v.s execution time by hour')
    if raw_data:
        st.dataframe(filtered_df)

if __name__ == "__main__":
    main()