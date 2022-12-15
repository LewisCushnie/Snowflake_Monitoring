import streamlit as st
import pandas as pd
from utils import snowflake_connector as sf
from utils import sql

def main():

    # Apply formatting from the style.css file to the page
    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    #==========================#
    # MAIN PAGE - INTRO #
    #==========================#

    st.title('RBAC Summary')
    st.success(
    '''
    The **RBAC Summary** page aims allows users to easily track ROLES and USERS assigned to these roles, the aim
    is to allow users to rapidly undertsand where grants have been assigned in a team.
    '''
    )

    #==========================#
    # USER QUERY PERFORMANCE #
    #==========================#

    st.header('Roles by Environment & Domain')

    selection = st.selectbox('Filter by Environment', ('PROD', 'TEST', 'DEV'))

    RBAC = '''
        show roles;
            '''

    if selection:

        df = sf.sql_to_dataframe(RBAC)
        df = df[['name', 'assigned_to_users', 'granted_to_roles', 'granted_roles']]


        if selection=='PROD':

            domain = st.radio(label='Choose Business Domain', options=('ALL','FINANCE', 'UNDERWRITING'))

            if domain == 'ALL':
                df= df[df['name'].str.contains(selection)]
                st.dataframe(df)

            else:
                df= df[df['name'].str.contains(domain)]
                df= df[df['name'].str.contains(selection)]
                st.dataframe(df)

        if selection=='TEST':

            domain = st.radio(label='Choose Business Domain', options=('ALL','FINANCE', 'UNDERWRITING'))

            if domain == 'ALL':
                df= df[df['name'].str.contains(selection)]
                st.dataframe(df)

            else:
                df= df[df['name'].str.contains(domain)]
                df= df[df['name'].str.contains(selection)]
                st.dataframe(df)

        if selection=='DEV':
            
            domain = st.radio(label='Choose Business Domain', options=('ALL','FINANCE', 'UNDERWRITING'))

            if domain == 'ALL':
                df= df[df['name'].str.contains(selection)]
                st.dataframe(df)

            else:
                df= df[df['name'].str.contains(domain)]
                df= df[df['name'].str.contains(selection)]
                st.dataframe(df)

if __name__ == "__main__":
    main()            
