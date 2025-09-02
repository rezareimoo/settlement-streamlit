import streamlit as st
import pandas as pd
import plotly.express as px

def render_demographics_tab(jamati_member_df):
    """Render the Jamati Demographics tab with demographics visualizations"""
    
    # Create two columns for side-by-side charts
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("🌍 Country of Origin Distribution", expanded=False):
            origin_counts = jamati_member_df['countryoforigin'].dropna()
            origin_counts = origin_counts[origin_counts != ""].value_counts()

            fig = px.pie(origin_counts, values=origin_counts.values, names=origin_counts.index, title='Country of Origin Distribution')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        with st.expander("📊 Age Distribution", expanded=False):
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

    # Add education level visualization
    with st.expander("🎓 Education Level Distribution", expanded=False):
        if 'educationlevel' in jamati_member_df.columns:
            # Filter out null values and empty strings, then get value counts
            education_counts = jamati_member_df['educationlevel'].dropna()
            education_counts = education_counts[education_counts != ""].value_counts()
            
            if not education_counts.empty:  # Only create visualization if we have data
                # Create a bar chart for education levels
                education_fig = px.bar(
                    x=education_counts.index,
                    y=education_counts.values,
                    title='Education Level Distribution',
                    labels={'x': 'Education Level', 'y': 'Number of Members'},
                    color=education_counts.values,
                    color_continuous_scale='Viridis'
                )
                
                # Update layout for better visualization
                education_fig.update_layout(
                    showlegend=False,
                    xaxis_tickangle=45,
                    margin=dict(b=100),  # Add bottom margin for rotated labels
                    coloraxis_showscale=False  # Hide the color scale
                )
                
                # Display the chart
                st.plotly_chart(education_fig, use_container_width=True)
            else:
                st.write("No valid education level data available.")
        else:
            st.write("Education level data is not available in the dataset.")
    
    # Display the dataframe below the charts
    st.subheader("Jamati Member Data")
    st.dataframe(jamati_member_df.drop("legalstatus", axis=1))