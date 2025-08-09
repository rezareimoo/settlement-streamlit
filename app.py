import streamlit as st
from database import fetch_all_data
from cases_tab import render_cases_tab
from demographics_tab import render_demographics_tab
from children_tab import render_children_tab
from case_lookup_tab import render_case_lookup_tab

# Set page config to wide layout to reduce padding
st.set_page_config(layout="wide")

# Custom CSS to further reduce padding
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Settlement App")

# Fetch all data from the database
try:
    df, jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df = fetch_all_data()
    
    if df is not None:
        # Create tabs for different sections
        cases, jamati_demographics, children_data, case_lookup = st.tabs(["Cases", "Jamati Demographics", "Children's Data", "Case Lookup"])

        with cases:
            render_cases_tab(df, jamati_member_df)

        with jamati_demographics:
            render_demographics_tab(jamati_member_df)

        with children_data:
            render_children_tab(df, jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df)

        with case_lookup:
            render_case_lookup_tab(df, jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df)

    else:
        st.error("Failed to fetch data from the database. Please check your connection.")

except Exception as e:
    st.error(f"An error occurred: {e}")
    print(f"Error in main app: {e}")