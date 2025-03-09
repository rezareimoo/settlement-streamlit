import streamlit as st
from config import DATABASE_URL
import psycopg2
import pandas as pd
import plotly.express as px

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

        # Create a pie chart of the statuses
        status_counts = df['status'].value_counts()
        fig = px.pie(status_counts, values=status_counts.values, names=status_counts.index, title='Case Status Distribution')
        st.plotly_chart(fig)

        # Create a line chart based on the CreationDate, grouped by Region
        df['lastlogdate'] = pd.to_datetime(df['lastlogdate'])
        
        # Filter cases created after 2020
        df = df[df['lastlogdate'].dt.year > 2022]

        # Group by CreationDate and Region, then count the number of cases
        df_grouped = df.groupby(['lastlogdate', 'region']).size().reset_index(name='case_count')

        # Create the line chart
        line_fig = px.line(df_grouped, x='lastlogdate', y='case_count', color='region', 
                           title='Cases Over Time by Region', 
                           labels={'lastlogdate': 'Last Log Date', 'case_count': 'Number of Cases'})
        st.plotly_chart(line_fig)

        # Display the filtered data in a scrollable table
        st.subheader("Filtered Data")
        st.dataframe(df)
        st.dataframe(jamati_member_df)
        st.dataframe(education_df)
        st.dataframe(finance_df)
        st.dataframe(physical_mental_health_df)
        st.dataframe(social_inclusion_agency_df)

    with jamati_demographics:

        origin_counts = jamati_member_df['countryoforigin'].dropna()
        origin_counts = origin_counts[origin_counts != ""].value_counts()

        fig = px.pie(origin_counts, values=origin_counts.values, names=origin_counts.index, title='Country of Origin Distribution')
        st.plotly_chart(fig)
        
        # Calculate age from yearofbirth
        if 'yearofbirth' in jamati_member_df.columns:
            # Filter out rows with NaN or empty yearofbirth
            valid_years_df = jamati_member_df.dropna(subset=['yearofbirth'])
            valid_years_df = valid_years_df[valid_years_df['yearofbirth'] != ""]

            current_year = pd.Timestamp.now().year
            valid_years_df['age'] = current_year - valid_years_df['yearofbirth']
            
            # Create a histogram of ages
            age_histogram = px.histogram(valid_years_df, x='age', nbins=20, title='Age Distribution')
            st.plotly_chart(age_histogram)
            st.dataframe(valid_years_df)
        else:
            st.write("Year of birth data is not available in the dataset.")

except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")


