import streamlit as st
import pandas as pd
from utils import snowflake_connector as sf
from utils import sql

def main():

    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title('RBAC Summary')

    st.markdown(
    '''The **RBAC Summary** page aims allows users to easily track ROLES and USERS assigned to these roles'''
    )

    #------------------------------- MAIN PAGE ----------------------------------- #
    #==========================#
    # USER QUERY PERFORMANCE #
    #==========================#

    st.header('Roles by Domain and Environment')

    selection = st.selectbox('Filter by', ('Business Domain', 'Environment'))

    RBAC = '''
        show roles;
            '''

    if selection:

        if selection=='Business Domain':

            domain = st.radio(label='Choose Business Domain', options=('FINANCE', 'UNDERWRITING'))

            df = sf.sql_to_dataframe(RBAC)
            df = df[['name', 'assigned_to_users', 'granted_to_roles', 'granted_roles']]
            df= df[df['name'].str.contains(domain)]
            st.dataframe.write(df)

        if selection =='Environment':

            environment = st.radio(label='Choose Environment',options=('DEV', 'TEST', 'PROD'))

            df = sf.sql_to_dataframe(RBAC)
            df = df[['name', 'assigned_to_users', 'granted_to_roles', 'granted_roles']]
            df= df[df['name'].str.contains(environment)]
            st.dataframe(df)

if __name__ == "__main__":
    main()            
