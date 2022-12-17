import streamlit as st
from utils import sql
from utils import snowflake_connector as sf

def list_to_OR_string(input_list):
    i = 1
    n = len(input_list)
    if n == 0:
        # String to return if nothing is selected
        OR_string = 'XXXXXXX'
    else:
        OR_string = ''
        for word in input_list:
            if i == n:
                OR_string = OR_string + word

            elif i == 1:
                OR_string = word + '|'
                i += 1

            else:
                OR_string = OR_string + word + '|'
                i += 1

    return OR_string

def filter_df_by_business_domain(df):

    # check that the input df contains a 'TABLE SCHEMA' column
    if 'TABLE_SCHEMA' in df:
        st.write('YAY')
    else:
        raise Exception('''The 'TABLE_SCHEMA' column does not exist in this dataframe, 
        cannot use the filter_df_by_business_domain function''')

    # get the business domains from the ADMIN_DB
    query = sql.BUSINESS_DOMAINS
    BUSINESS_DOMAINS_df = sf.sql_to_dataframe(query)

    select_all = st.checkbox('Select all business domains:')

    if select_all:
        selections = list_to_OR_string(BUSINESS_DOMAINS_df['DOMAIN_NAME'])

    else:
        # Multiselect list
        multi_selections = st.multiselect("Select domain(s) to filter by:",\
        list(BUSINESS_DOMAINS_df['DOMAIN_NAME']), list(BUSINESS_DOMAINS_df['DOMAIN_NAME']))
        selections = list_to_OR_string(multi_selections)

    selection_rows = df['TABLE_SCHEMA'].str.contains(selections)
    filtered_df = df.loc[selection_rows]

    return filtered_df

if __name__ == "__main__":
    pass