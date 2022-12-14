import streamlit as st

st.set_page_config(
    page_title="Usage Insights App"
    ,page_icon="🌀"
    ,layout="centered")

def main():
    # Make sure session state is preserved
    for key in st.session_state:
        st.session_state[key] = st.session_state[key]

    with open("utils/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
    st.title("Welcome to the Usage Insights app!")
    # st.sidebar.text(f"Account: {st.secrets.sf_usage_app.account}")
    st.sidebar.info("Choose a page above!")
    st.success(
    """
    This app provides insights on a demo Snowflake account usage.
    ### Get started!
    👈 Select a page in the sidebar!
    """
    )
    st.header("Understanding Snowflake's Cost Model")
    st.info('''
    This will lay out how to understand the model
    \
    ref: https://www.finout.io/blog/snowflake-cost-reduction
    ''')

if __name__ == "__main__":
    main()  
