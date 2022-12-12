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

    selection = st.selectbox('Choose business domain', ('FINANCE', 'UNDERWRITING'))

    RBAC = f'''
        select 
        CREATED_ON as "DATE CREATED"
        ,NAME 
        --,ASSIGNED_TO_USERS as "ASSIGNED TO USERS"
        ,GRANTED_TO_ROLES as "GRANTED TO ROLES"
        ,OWNER 
        from roles
        where name like '%{selection}%';'''

    if selection:
        df = sf.sql_to_dataframe(RBAC)
        st.dataframe(df, width=1000)

if __name__ == "__main__":
    main()            
