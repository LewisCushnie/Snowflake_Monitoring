import streamlit as st

st.set_page_config(page_title="Usage Insights app", page_icon="🌀", layout="centered")

# Make sure session state is preserved
for key in st.session_state:
    st.session_state[key] = st.session_state[key]

st.title("Welcome to the Usage Insights app!")
# st.sidebar.text(f"Account: {st.secrets.sf_usage_app.account}")
st.sidebar.info("Choose a page!")
st.markdown(
    """
This app provides insights on a demo Snowflake account usage.
### Get started!
👈 Select a page in the sidebar!
    """
)

theme = st.get_option("theme")
st.write(theme)
