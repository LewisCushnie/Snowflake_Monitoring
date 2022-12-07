import streamlit as st
from utils import snowflake_connector as sf
from utils import sql

st.set_page_config(
    page_title="Usage Insights app - Data Transfer",
    page_icon="🔹",
    layout="centered",
)

def main():
    query = sql.TEST_QUERY
    test_df = sf.sql_to_dataframe(query)
    return st.write('Hello'), st.dataframe(test_df)


if __name__ == "__main__":
    main()