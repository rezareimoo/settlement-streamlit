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

    # Close the connection
    conn.close()

    # Display filters for Region and AssignedTo
    regions = df['region'].unique()
    assigned_to = df['assignedto'].unique()

    selected_region = st.selectbox("Select Region", options=["All"] + list(regions))
    selected_assigned_to = st.selectbox("Select Assigned To", options=["All"] + list(assigned_to))

    # Filter the dataframe based on selections
    if selected_region != "All":
        df = df[df['region'] == selected_region]
    if selected_assigned_to != "All":
        df = df[df['assignedto'] == selected_assigned_to]

    # Create a pie chart of the statuses
    status_counts = df['status'].value_counts()
    fig = px.pie(status_counts, values=status_counts.values, names=status_counts.index, title='Case Status Distribution')
    st.plotly_chart(fig)

    # Display the filtered data in a scrollable table
    st.subheader("Filtered Data")
    st.dataframe(df)

except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")


