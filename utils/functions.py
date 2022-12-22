import streamlit as st
from utils import sql
from utils import snowflake_connector as sf

def filter_df_by_business_domain(df, domain_name_column_str, unique_key):

    '''
    - df: The dataframe that you want to filter by domain
    - domain_name_column_str: The column that contains the domain name info (can contain domain names,
    or objects that have the domain name in them e.g a warehouse called PROD_FINANCE_WH)
    - unique_key: This keep streamlit happy (otherwise you get duplicate keys generated for the buttons).
    simply name this after the graph title e.g 'warehouse monitoring'
    '''

    # check that the input df contains a 'TABLE SCHEMA' column
    if domain_name_column_str in df:
        pass
    else:
        raise Exception(f'''The {domain_name_column_str} column does not exist in this dataframe, 
        cannot use the filter_df_by_business_domain function''')

    # get the business domains from the ADMIN_DB
    query = sql.BUSINESS_DOMAINS
    BUSINESS_DOMAINS_df = sf.sql_to_dataframe(query)

    apply_filter = st.checkbox('Business domain filter:', key= unique_key+'check1')

    if apply_filter:
        # Multiselect list
        multi_selections = st.multiselect("Select domain(s) to filter by:",\
        list(BUSINESS_DOMAINS_df['DOMAIN_NAME']), list(BUSINESS_DOMAINS_df['DOMAIN_NAME']), key= unique_key+'multi1')

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

        selections = list_to_OR_string(multi_selections)
        selection_rows = df[domain_name_column_str].str.contains(selections)
        filtered_df = df.loc[selection_rows]

    else:
        filtered_df = df

    return filtered_df

def colour_df(value):
  
  if value >= 10:
    colour = 'red'
  if value <10 and value >=5:
    colour = 'orange'
  if value <5:
    colour = 'green'

  return 'color: %s' % colour

def make_red(value):
  colour = 'red'
  return 'color: %s' % colour

def add_logo():

    return st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://www.beazley.com/themes/custom/beazley_default/logo.svg);
                background-repeat: no-repeat;
                padding-top: 20px;
                background-position: 20px 20px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    pass

if __name__ == "__main__":
    pass