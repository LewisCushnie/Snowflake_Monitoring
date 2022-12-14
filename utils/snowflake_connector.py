import pandas as pd
import streamlit as st
from utils import sql
import snowflake.connector

TIME_TO_LIVE = 600 #10 mins

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    snowflake_connector = snowflake.connector.connect(
        **st.secrets["snowflake"], client_session_keep_alive=True
    )

    snowflake_connector.cursor().execute("ALTER SESSION SET QUERY_TAG = 'StreamlitQuery'")

    if 'snowflake_connector' not in st.session_state:
        st.session_state['snowflake_connector'] = snowflake_connector

    return snowflake_connector

snowflake_connector = init_connection()

# Run SQL query and return Pandas DF
@st.experimental_memo(ttl=TIME_TO_LIVE)
def sql_to_dataframe(sql_query: str, show_spinner=False) -> pd.DataFrame:
    data = pd.read_sql(
        sql_query,
        snowflake_connector,
    )
    return data

# Run SQL query and return results in default formate.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=TIME_TO_LIVE)
def run_query(query, show_spinner=False):
    with snowflake_connector.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

if __name__ == "__main__":
    pass

