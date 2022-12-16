import pandas as pd
import streamlit as st
import altair as alt
from utils import snowflake_connector as sf
from utils.df_styler import colour_df
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

    st.sidebar.header('Warehouse usage summary stats')
    query = sql.WH_USAGE_LAST_7_DAYS
    WH_USAGE_LAST_7_DAYS_df = sf.sql_to_dataframe(query)
    metric=round(WH_USAGE_LAST_7_DAYS_df['CREDITS_USED_LAST_PERIOD'].iloc[0],5)
    pct_change=round(WH_USAGE_LAST_7_DAYS_df['PCT_CHANGE'].iloc[0],3)
    st.sidebar.metric(label='Credit usage over last 7 day period', value= metric, delta= f'{pct_change}%', delta_color= "inverse")

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
    # SIDEBAR - MOST USED WAREHOUSE
    #======================================================#

    query = sql.METERING_TOP_10
    METERING_TOP_10_df = sf.sql_to_dataframe(query)

    # Most used warehouse
    most_used_loc = METERING_TOP_10_df['CREDITS_USED'].idxmax()
    most_used_wh = METERING_TOP_10_df['NAME'].iloc[most_used_loc]

    # Top 5 most used warehouses
    five_most_used_df = METERING_TOP_10_df['CREDITS_USED'].nlargest(5)
    five_most_used_wh_list = METERING_TOP_10_df['NAME'].iloc[five_most_used_df.index].tolist()

    amount_used = round(METERING_TOP_10_df['CREDITS_USED'].iloc[most_used_loc], 3)
    st.sidebar.metric(label='Most used warehouse', value= most_used_wh, delta= f'{amount_used} Credits', delta_color= "normal")

    #======================================================#
    # MAIN PAGE - WAREHOUSE USAGE COMPARISON BAR CHART
    #======================================================#
    
    line = '---'
    st.markdown(line)
    st.header('Warehouse usage comparison chart')

    METERING_TOP_10_df = METERING_TOP_10_df.set_index('NAME')
    METERING_TOP_10_df['CREDITS_USED'] = METERING_TOP_10_df['CREDITS_USED'].astype(float)

    # Multiselect list
    wh_selected = st.multiselect("Pick Warehouse (5 most used warehouses selected by default):",\
     list(METERING_TOP_10_df.index), five_most_used_wh_list)
    wh_to_show_df = METERING_TOP_10_df.loc[wh_selected]

    # Create altair chart
    chart = alt.Chart(wh_to_show_df.reset_index()).mark_bar().encode(
    x= alt.X('NAME:N', sort= '-y'),
    y= alt.Y('CREDITS_USED:Q')
    )

    st.altair_chart(chart, use_container_width= True, theme= 'streamlit')

    # Raw data checkbox
    raw_data = st.checkbox('Show raw warehouse data:')
    if raw_data:
        st.dataframe(wh_to_show_df)

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
    date_mask = (COMPUTE_CREDITS_PER_DAY_df['Usage Week'] > slider_values[0]) & (COMPUTE_CREDITS_PER_DAY_df['Usage Week'] <= slider_values[1])
    filtered_df = COMPUTE_CREDITS_PER_DAY_df.loc[date_mask]

    # Create bar chart with filtered values
    st.bar_chart(filtered_df, x= 'Usage Week', y= ['Compute Credits Used','Cost ($)'])

    # chart = alt.Chart(filtered_df).transform_fold(
    # ['Compute Credits Used', 'Cost ($)'],
    # as_=['QUANTITY', 'COUNT']
    # ).mark_bar().encode(
    # x= alt.X('QUANTITY:O', axis=alt.Axis(title=None)),
    # y= 'COUNT:Q',
    # color= 'QUANTITY:N',
    # column= alt.Column('Usage Week:N')
    # )

    # st.altair_chart(chart, use_container_width= False, theme= 'streamlit')

    # Raw data checkbox
    raw_data = st.checkbox('Show raw compute data:')
    if raw_data:
        st.text('Red - $10+ per day | Orange - $5-$10 per day | Green - Less than $5 per day')
        filtered_df = filtered_df.style.applymap(colour_df,
        subset=pd.IndexSlice[:,['Cost ($)']])
        st.dataframe(filtered_df, width=1000)

    #======================================================#
    # MAIN PAGE: WAREHOUSE CREDIT USAGE BREAKDOWN
    #======================================================#

    line = '---'
    st.markdown(line)
    st.header('Warehouse credit usage breakdown')

    query = sql.WH_CREDIT_BREAKDOWN
    WH_CREDIT_BREAKDOWN_df = sf.sql_to_dataframe(query)

    # Top n highest total credit usage warehouses
    n_largest = st.number_input('Select n highest credit usage warehouses:', step= 1, value= 5)
    WH_CREDIT_BREAKDOWN_TOP_N = WH_CREDIT_BREAKDOWN_df['TOTAL'].nlargest(n_largest)
    WH_CREDIT_BREAKDOWN_df = WH_CREDIT_BREAKDOWN_df.iloc[WH_CREDIT_BREAKDOWN_TOP_N.index]

    percentage = st.checkbox('Show as percentages:')
    if percentage:
        WH_CREDIT_df = WH_CREDIT_BREAKDOWN_df[['WH_NAME','PERC_COMPUTE', 'PERC_CLOUD']]
        st.bar_chart(WH_CREDIT_df, x= 'WH_NAME')
    else:
        WH_CREDIT_df = WH_CREDIT_BREAKDOWN_df[['WH_NAME','COMPUTE', 'CLOUD_SERVICES']]
        st.bar_chart(WH_CREDIT_df, x= 'WH_NAME')

        # Create altair chart
        chart = alt.Chart(WH_CREDIT_df.reset_index()).transform_fold(
        ['PERC_COMPUTE', 'PERC_CLOUD'],
        as_=['CATEGORY', 'PERCENTAGE']
        ).mark_bar().encode(
        x= alt.X('WH_NAME', sort= '-y'),
        y= alt.Y('PERCENTAGE'),
        color= 'CATEGORY:N'
        )

        st.altair_chart(chart, use_container_width= False, theme= 'streamlit')

    # chart = alt.Chart(SHOW_TASKS_df).transform_fold(
    # ['COUNT_SUCCEEDED', 'COUNT_FAILED'],
    # as_=['STATUS', 'COUNT']
    # ).mark_bar().encode(
    # x= alt.X('NAME', sort= '-y'),
    # y= alt.Y('COUNT:Q'),
    # color= 'STATUS:N'
    # )

    # Raw data checkbox
    raw_data = st.checkbox('Show raw warehouse usage data')
    if raw_data:
        st.dataframe(WH_CREDIT_df)

    # line = '---'
    # st.markdown(line)
    # st.header('Warehouse credit usage breakdown')

    # query = sql.WH_CREDIT_BREAKDOWN
    # WH_CREDIT_BREAKDOWN_df = sf.sql_to_dataframe(query)

    # # Top n highest total credit usage warehouses
    # n_largest = st.number_input('Select n highest credit usage warehouses:', step= 1, value= 5)
    # WH_CREDIT_BREAKDOWN_TOP_N = WH_CREDIT_BREAKDOWN_df['TOTAL'].nlargest(n_largest)
    # WH_CREDIT_BREAKDOWN_df = WH_CREDIT_BREAKDOWN_df.iloc[WH_CREDIT_BREAKDOWN_TOP_N.index]

    # percentage = st.checkbox('Show as percentages:')
    # if percentage:
    #     WH_CREDIT_df = WH_CREDIT_BREAKDOWN_df[['WH_NAME','PERC_COMPUTE', 'PERC_CLOUD']]
    #     st.bar_chart(WH_CREDIT_df, x= 'WH_NAME')
    # else:
    #     WH_CREDIT_df = WH_CREDIT_BREAKDOWN_df[['WH_NAME','COMPUTE', 'CLOUD_SERVICES']]
    #     st.bar_chart(WH_CREDIT_df, x= 'WH_NAME')

    # # Raw data checkbox
    # raw_data = st.checkbox('Show raw warehouse usage data')
    # if raw_data:
    #     st.dataframe(WH_CREDIT_df)

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
        sub_df = COMPUTE_AVAILABILITY_AND_EXECUTION_TIME_df[['HOUR', 'PCT_UTILIZATION']]
        st.bar_chart(sub_df, x= 'HOUR')
    else:
        sub_df = COMPUTE_AVAILABILITY_AND_EXECUTION_TIME_df[['HOUR', 'TOTAL_EXEC_TIME_SEC', 'COMPUTE_AVAILABILITY_SEC']]
        st.bar_chart(sub_df, x= 'HOUR')

    # Raw data checkbox
    raw_data = st.checkbox('Show raw availability data:')
    if raw_data:
        st.dataframe(sub_df)

if __name__ == "__main__":
    main()