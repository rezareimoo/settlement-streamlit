import streamlit as st
import psycopg2
import pandas as pd
from config import DATABASE_URL
from database import fetch_all_data
from cases_tab import render_cases_tab
from demographics_tab import render_demographics_tab
from children_tab import render_children_tab
from case_lookup_tab import render_case_lookup_tab
from jamati_member_lookup_tab import render_jamati_member_lookup_tab

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

def load_fdp_data():
    """Load and process FDP data"""
    try:
        conn_fdp = psycopg2.connect(DATABASE_URL)
        fdp_query = "SELECT * FROM fdp_cases"
        fdp_raw = pd.read_sql(fdp_query, conn_fdp)
        conn_fdp.close()
        
        # Map FDP fields to CMS structure
        fdp_df = fdp_raw.copy()
        fdp_df = fdp_df.rename(columns={
            'access_case': 'caseid',
            'settlement_case_status': 'status',
            'family_last_name': 'lastname',
            'head_of_family_first_name': 'firstname',
            'state_code_2_digits': 'state',
            'access_case_creation_date': 'creationdate',
            'settlement_cm': 'assignedto',
            'phone': 'phonenumber',
            'current_location': 'city',
            'zip_code': 'zip'
        })
        
        # Convert creation date to datetime
        fdp_df['creationdate'] = pd.to_datetime(fdp_df['creationdate'], errors='coerce')
        
        # Map status values to CMS equivalents
        status_mapping = {
            'Active': 'Open',
            'Closed': 'Closed',
            'On Hold': 'Open',
            'Completed': 'Closed'
        }
        fdp_df['status'] = fdp_df['status'].map(status_mapping).fillna(fdp_df['status'])
        
        # Ensure required columns exist
        required_cols = ['caseid', 'region', 'status', 'creationdate', 'firstname', 'lastname', 'state']
        for col in required_cols:
            if col not in fdp_df.columns:
                fdp_df[col] = 'N/A'
        
        # Handle missing or null regions
        fdp_df['region'] = fdp_df['region'].fillna('Unknown')
        
        # Filter out any completely invalid rows
        fdp_df = fdp_df.dropna(subset=['caseid'])
        
        return fdp_df
        
    except Exception as e:
        st.error(f"Error loading FDP data: {e}")
        return None

# Fetch all data from the database
try:
    df, jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df = fetch_all_data()
    
    if df is not None:
        # Create tabs for different sections with updated titles
        cases, case_lookup, jamati_demographics, children_data, jamati_member_lookup = st.tabs([
            "Cases (CMS + FDP + Compare)", 
            "Case Lookup (CMS Only)",
            "Jamati Demographics (CMS Only)", 
            "Children's Data (CMS Only)", 
            "Jamati Member Lookup (CMS Only)"
        ])

        with cases:
            # Data source selection
            st.markdown("### 📊 Data Source Selection")
            data_source = st.radio(
                "Select data source:",
                options=["CMS Data", "FDP Data", "Compare Both"],
                horizontal=True,
                key="data_source_selector"
            )
            st.markdown("---")
            
            # Load FDP data if needed
            fdp_df = None
            if data_source in ["FDP Data", "Compare Both"]:
                fdp_df = load_fdp_data()
                if fdp_df is None:
                    data_source = "CMS Data"  # Fallback to CMS
            
            # Select which dataset to use
            if data_source == "CMS Data":
                working_df = df.copy()
                working_jamati_df = jamati_member_df.copy()
            elif data_source == "FDP Data" and fdp_df is not None:
                working_df = fdp_df.copy()
                working_jamati_df = pd.DataFrame()  # FDP doesn't have jamati member details
            else:  # Compare Both
                working_df = df.copy()
                working_jamati_df = jamati_member_df.copy()
            
            # Render the cases tab with the selected data
            render_cases_tab(working_df, working_jamati_df, data_source, fdp_df if data_source == "Compare Both" else None)

        with case_lookup:
            render_case_lookup_tab(df, jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df)

        with jamati_demographics:
            render_demographics_tab(jamati_member_df)

        with children_data:
            render_children_tab(df, jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df)

        with jamati_member_lookup:
            render_jamati_member_lookup_tab(jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df)

    else:
        st.error("Failed to fetch data from the database. Please check your connection.")

except Exception as e:
    st.error(f"An error occurred: {e}")
    print(f"Error in main app: {e}")
