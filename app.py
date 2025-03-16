import streamlit as st
from config import DATABASE_URL
import psycopg2
import pandas as pd
import plotly.express as px
from urllib.request import urlopen
import json

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

# You can now use DATABASE_URL for your database connections

try:
    # Attempt to establish a connection
    conn = psycopg2.connect(DATABASE_URL)
    print("Successfully connected to the database!")

    # Fetch data from the SettlementCase table
    query = "SELECT * FROM SettlementCase"
    df = pd.read_sql(query, conn)
    print("Data fetched successfully!")
    jamati_member_query = "SELECT * FROM JamatiMember"
    jamati_member_df = pd.read_sql(jamati_member_query, conn)
    print("Jamati member data fetched successfully!")
    education_query = "SELECT * FROM Education"
    education_df = pd.read_sql(education_query, conn)
    print("Education data fetched successfully!")
    finance_query = "SELECT * FROM Finance"
    finance_df = pd.read_sql(finance_query, conn)
    print("Finance data fetched successfully!")
    physical_mental_health_query = "SELECT * FROM PhysicalMentalHealth"
    physical_mental_health_df = pd.read_sql(physical_mental_health_query, conn)
    print("Physical and mental health data fetched successfully!")
    social_inclusion_agency_query = "SELECT * FROM SocialInclusionAgency"
    social_inclusion_agency_df = pd.read_sql(social_inclusion_agency_query, conn)
    print("Social inclusion agency data fetched successfully!")
    # Close the connection
    conn.close()

    # Display filters for Region and AssignedTo
    regions = df['region'].unique()
    country_of_origin = jamati_member_df['countryoforigin'].unique()

    cases, jamati_demographics = st.tabs(["Cases", "Jamati Demographics"])

    with cases:
        selected_region = st.selectbox("Select Region", options=["All"] + list(regions))

        # Filter the dataframe based on selections
        if selected_region != "All":
            df = df[df['region'] == selected_region]

        # Calculate total number of cases and open cases
        total_cases = len(df)
        open_cases = df[df['status'].isin(['Open', 'Reopen'])].shape[0]

        # Display headers side by side with custom color for open cases
        col1, col2 = st.columns(2)

        # Custom CSS for button styling
        st.markdown("""
            <style>
            div[data-testid="stHorizontalBlock"] div[data-testid="column"] button[data-testid="baseButton-secondary"]:hover {
                background-color: #1f77b4;
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)

        # Initialize session states
        if 'active_view' not in st.session_state:
            st.session_state.active_view = 'total'
        if 'needs_rerun' not in st.session_state:
            st.session_state.needs_rerun = False

        # Check if we need to rerun
        if st.session_state.needs_rerun:
            st.session_state.needs_rerun = False
            st.rerun()

        with col1:
            if st.button(
                f"Total Cases: {total_cases}",
                type="primary" if st.session_state.active_view == 'total' else "secondary",
                use_container_width=True
            ):
                st.session_state.active_view = 'total'
                st.session_state.needs_rerun = True
                st.rerun()

        with col2:
            if st.button(
                f"Open Cases: {open_cases}",
                type="primary" if st.session_state.active_view == 'open' else "secondary",
                use_container_width=True
            ):
                st.session_state.active_view = 'open'
                st.session_state.needs_rerun = True
                st.rerun()

        # Filter based on active view
        if st.session_state.active_view == 'open':
            df = df[df['status'].isin(['Open', 'Reopen'])]

        # Create two columns for pie chart and map
        pie_col, map_col = st.columns(2)

        with pie_col:
            # Display pie chart
            status_counts = df['status'].value_counts()
            fig = px.pie(status_counts, values=status_counts.values, names=status_counts.index, title='Case Status Distribution')
            st.plotly_chart(fig, use_container_width=True)

        with map_col:
            # Create US map visualization
            state_counts = df['state'].value_counts().reset_index()
            state_counts.columns = ['state', 'count']
            
            # Create the choropleth map
            fig_map = px.choropleth(
                state_counts,
                locations='state',
                locationmode='USA-states',
                color='count',
                scope='usa',
                color_continuous_scale=['white', 'blue'],
                title='Number of Cases by State',
                labels={'count': 'Number of Cases'}
            )
            
            # Update the layout for better visualization and remove background
            fig_map.update_layout(
                geo_scope='usa',
                margin=dict(l=0, r=0, t=30, b=0),
                geo=dict(
                    showlakes=False,
                    showland=False,
                    bgcolor='rgba(0,0,0,0)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            # Display the map
            st.plotly_chart(fig_map, use_container_width=True)

        # Create a line chart based on the CreationDate, grouped by Region
        df['creationdate'] = pd.to_datetime(df['creationdate'])
        
        # Filter cases created after 2020
        df = df[df['creationdate'].dt.year > 2022]

        # Create a month column for monthly aggregation
        df['month_year'] = df['creationdate'].dt.to_period('M')
        
        # Group by Month and Region, then count the number of cases
        df_grouped = df.groupby([df['month_year'].astype(str), 'region']).size().reset_index(name='case_count')

        # Create the line chart
        line_fig = px.line(df_grouped, x='month_year', y='case_count', color='region', 
                           title='New Cases Over Time by Region (Monthly)', 
                           labels={'month_year': 'Month', 'case_count': 'Number of Cases'})
        st.plotly_chart(line_fig)

        # Display the filtered data in a scrollable table
        st.subheader("Filtered Data")
        st.dataframe(df)
        # st.dataframe(jamati_member_df.drop("legalstatus", axis=1))
        # st.dataframe(education_df)
        # st.dataframe(finance_df)
        # st.dataframe(physical_mental_health_df)
        # st.dataframe(social_inclusion_agency_df)

    with jamati_demographics:
        # Create two columns for side-by-side charts
        col1, col2 = st.columns(2)

        with col1:
            origin_counts = jamati_member_df['countryoforigin'].dropna()
            origin_counts = origin_counts[origin_counts != ""].value_counts()

            fig = px.pie(origin_counts, values=origin_counts.values, names=origin_counts.index, title='Country of Origin Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Calculate age from yearofbirth
            if 'yearofbirth' in jamati_member_df.columns:
                # Filter out rows with NaN or empty yearofbirth
                valid_years_df = jamati_member_df.dropna(subset=['yearofbirth'])
                valid_years_df = valid_years_df[valid_years_df['yearofbirth'] != ""]
                
                # Filter out yearofbirth values greater than 2024 or equal to 0
                valid_years_df = valid_years_df[(valid_years_df['yearofbirth'] <= 2024) & (valid_years_df['yearofbirth'] > 1800)]

                current_year = pd.Timestamp.now().year
                valid_years_df['age'] = current_year - valid_years_df['yearofbirth']
                
                # Create a histogram of ages with visual distinction
                age_histogram = px.histogram(valid_years_df, x='age', nbins=20, title='Age Distribution', opacity=0.8)
                # Update layout to add spacing between bars
                age_histogram.update_traces(marker_line_width=1, marker_line_color="white")
                st.plotly_chart(age_histogram, use_container_width=True)
            else:
                st.write("Year of birth data is not available in the dataset.")
        
        # Display the dataframe below the charts
        st.subheader("Jamati Member Data")
        st.dataframe(jamati_member_df.drop("legalstatus", axis=1))

except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")
