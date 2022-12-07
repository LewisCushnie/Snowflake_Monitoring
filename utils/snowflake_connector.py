import datetime
from typing import Any, Dict
import pandas as pd
import streamlit as st
# from snowflake.connector import connect
#from snowflake.connector.connection import SnowflakeConnection
from utils import sql

#=============

import snowflake.connector

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

# Funtion to perform queries from the database.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with st.session_state['snowflake_connector'].cursor() as cur:
        cur.execute(query)
        return cur.fetchall()



# TIME_TO_LIVE = 60 * 60 * 6  # 6 hours caching


# # Share the connector across all users connected to the app
# @st.experimental_singleton()
# def get_connector(
#     secrets_key: str = "snowflake",
#     input_params: Dict[str, Any] = None,
#     use_browser=True,
# ) -> SnowflakeConnection:
#     """Get a connector to Snowflake. By default, the connector will look
#     for credentials found under st.secrets["snowflake"].
#     Args:
#         secrets_key (str, optional): Streamlit secrets key for the credentials.
#         Defaults to 'snowflake'
#         params (dict, optional): Connector parameters.
#         Overrides Streamlit secrets. Defaults to None.
#         local_development (bool, optional): If True, this will open a
#         tab in your browser to collect requirements. Defaults to True.
#     Returns:
#         SnowflakeConnection: Snowflake connector object.
#     """

#     # Default params
#     params: Dict[str, Any] = {
#         **st.secrets[secrets_key],
#         "client_session_keep_alive": True,
#         "client_store_temporary_credential": True,
#     }

#     # Override default params with input params
#     if input_params:
#         for key in input_params.keys():
#             params[key] = input_params[key]

#     # This will open a tab in your browser and sign you in
#     if use_browser:
#         params["authenticator"] = "externalbrowser"

#     connector = connect(**params)
#     return connector


# snowflake_connector = get_connector(
#     secrets_key="sf_usage_app",
#     use_browser=False,
# )

# cur = snowflake_connector.cursor()
# cur.execute(f"use warehouse {st.secrets.sf_usage_app.warehouse};")


@st.experimental_memo(ttl=TIME_TO_LIVE)
def sql_to_dataframe(sql_query: str) -> pd.DataFrame:
    data = pd.read_sql(
        sql_query,
        snowflake_connector,
    )
    return data


# @st.experimental_memo(ttl=TIME_TO_LIVE)
# def get_queries_data(
#     date_from: datetime.date,
#     date_to: datetime.date,
# ):
#     queries_data = sql_to_dataframe(
#         sql.QUERIES_QUERY.format(
#             date_from=date_from,
#             date_to=date_to,
#         )
#     )
#     queries_data["DURATION_SECS"] = round(
#         (queries_data.TOTAL_ELAPSED_TIME) / 1000
#     )
#     queries_data["DURATION_SECS_PP"] = queries_data.DURATION_SECS.apply(
#         gui.pretty_print_seconds
#     )
#     queries_data["QUERY_TEXT_PP"] = queries_data.QUERY_TEXT.apply(
#         gui.pretty_print_sql_query
#     )
#     return queries_data


if __name__ == "__main__":
    pass
