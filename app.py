import streamlit as st
from config import DATABASE_URL
import psycopg2
import pandas as pd
import plotly.express as px
from urllib.request import urlopen
import json
from datetime import datetime

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

    cases, jamati_demographics, children_data, case_lookup = st.tabs(["Cases", "Jamati Demographics", "Children's Data", "Case Lookup"])

    with cases:
        # --- Summary Table at the Top ---
        # 1. Aggregate number of cases per region
        case_counts = df.groupby('region')['caseid'].nunique().reset_index(name='Number of Cases')

        # 2. For each region, count the number of individuals in jamati_member_df
        def count_individuals(region):
            case_ids = df[df['region'] == region]['caseid'].unique()
            return jamati_member_df[jamati_member_df['caseid'].isin(case_ids)].shape[0]

        case_counts['Number of Individuals'] = case_counts['region'].apply(count_individuals)

        # 3. Calculate number of open cases per region
        open_cases_df = df[df['status'].isin(['Open', 'Reopen'])]
        open_case_counts = open_cases_df.groupby('region')['caseid'].nunique().reset_index(name='Open Cases')

        # 4. Merge open case counts into the summary table
        case_counts = case_counts.merge(open_case_counts, on='region', how='left').fillna(0)

        # 5. Format numbers with commas
        case_counts['Number of Cases'] = case_counts['Number of Cases'].map('{:,}'.format)
        case_counts['Number of Individuals'] = case_counts['Number of Individuals'].map('{:,}'.format)
        case_counts['Open Cases'] = case_counts['Open Cases'].astype(int).map('{:,}'.format)

        # 6. Set region as index for a cleaner look
        case_counts = case_counts.set_index('region')

        # 7. Display with a nice header and description
        st.markdown("## 🗺️ Regional Summary")
        st.markdown(
            "This table summarizes the number of settlement cases, open cases, and the aggregate number of individuals per region."
        )
        st.dataframe(
            case_counts.style
                
                .set_properties(**{'font-size': '16px'})
        )
        st.markdown("---")  # Horizontal line for separation

        selected_region = st.selectbox("Select Region", options=["All"] + list(regions))

        # Filter the dataframe based on selections
        if selected_region != "All":
            df = df[df['region'] == selected_region]

        # Calculate total number of cases and open cases
        total_cases = len(df)
        open_cases = df[df['status'].isin(['Open', 'Reopen'])]

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
                f"Open Cases: {len(open_cases)}",
                type="primary" if st.session_state.active_view == 'open' else "secondary",
                use_container_width=True
            ):
                st.session_state.active_view = 'open'
                st.session_state.needs_rerun = True
                st.rerun()

        # Filter based on active view
        if st.session_state.active_view == 'open':
            df = df[df['status'].isin(['Open', 'Reopen'])]
        
        st.subheader("Settlement Cases")
        st.dataframe(df)

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

        # Add education level visualization
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
        
    with children_data:
        st.subheader("Children's Data (18 and Under)")
        
        # Filter children based on birth year (2025 - age <= 18, so yearofbirth >= 2007)
        current_year = 2025
        children_df = jamati_member_df[
            (jamati_member_df['yearofbirth'].notna()) & 
            (jamati_member_df['yearofbirth'] >= current_year - 18) &
            (jamati_member_df['yearofbirth'] <= current_year)
        ].copy()
        
        # Calculate age for children
        children_df['age'] = current_year - children_df['yearofbirth']
        
        if not children_df.empty:
            # Summary table showing children linked to active cases per region
            st.markdown("## 📊 Children Summary by Region")
            
            # Get active case IDs
            active_cases = df[df['status'].isin(['Open', 'Reopen'])]['caseid'].unique()
            
            # Filter children linked to active cases
            children_active_cases = children_df[children_df['caseid'].isin(active_cases)]
            
            # Group by region and count children
            children_summary = []
            for region in regions:
                region_cases = df[df['region'] == region]['caseid'].unique()
                region_children = children_df[children_df['caseid'].isin(region_cases)]
                region_active_children = children_active_cases[children_active_cases['caseid'].isin(region_cases)]
                
                children_summary.append({
                    'Region': region,
                    'Total Children': len(region_children),
                    'Children in Active Cases': len(region_active_children)
                })
            
            summary_df = pd.DataFrame(children_summary)
            
            # Format numbers with commas
            summary_df['Total Children'] = summary_df['Total Children'].map('{:,}'.format)
            summary_df['Children in Active Cases'] = summary_df['Children in Active Cases'].map('{:,}'.format)
            
            # Set region as index
            summary_df = summary_df.set_index('Region')
            
            st.dataframe(
                summary_df.style.set_properties(**{'font-size': '16px'})
            )
            st.markdown("---")
            
            # Age distribution chart
            col1, col2 = st.columns(2)
            
            with col1:
                age_counts = children_df['age'].value_counts().sort_index()
                age_fig = px.bar(
                    x=age_counts.index,
                    y=age_counts.values,
                    title='Children Age Distribution',
                    labels={'x': 'Age', 'y': 'Number of Children'},
                    color=age_counts.values,
                    color_continuous_scale='Blues'
                )
                age_fig.update_layout(showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(age_fig, use_container_width=True)
            
            with col2:
                # Country of origin for children
                children_origin_counts = children_df['countryoforigin'].dropna()
                children_origin_counts = children_origin_counts[children_origin_counts != ""].value_counts()
                
                if not children_origin_counts.empty:
                    origin_fig = px.pie(
                        children_origin_counts, 
                        values=children_origin_counts.values, 
                        names=children_origin_counts.index, 
                        title='Children Country of Origin Distribution'
                    )
                    st.plotly_chart(origin_fig, use_container_width=True)
                else:
                    st.write("No country of origin data available for children.")
            
            # Education data for children
            st.markdown("## 📚 Children's Education Status")
            
            # Get education data for children
            # Check if column names are lowercase or mixed case
            person_id_col = 'personid' if 'personid' in education_df.columns else 'PersonID'
            children_education = education_df[education_df[person_id_col].isin(children_df[person_id_col])]
            
            if not children_education.empty:
                # Merge children data with education data
                children_edu_merged = children_df.merge(
                    children_education, 
                    on=person_id_col, 
                    how='inner'
                )
                
                # Create education summary table
                # Handle column name variations (lowercase vs PascalCase)
                def get_col_name(preferred, alternative):
                    return preferred if preferred in children_edu_merged.columns else alternative
                
                education_summary = {}
                
                attending_school_col = get_col_name('isattendingschool', 'IsAttendingSchool')
                if attending_school_col in children_edu_merged.columns:
                    education_summary['Attending School'] = children_edu_merged[attending_school_col].sum()
                
                attending_ecdc_col = get_col_name('isattendingecdc', 'IsAttendingECDC')
                if attending_ecdc_col in children_edu_merged.columns:
                    education_summary['Attending ECDC'] = children_edu_merged[attending_ecdc_col].sum()
                
                attending_rec_col = get_col_name('isattendingrec', 'IsAttendingREC')
                if attending_rec_col in children_edu_merged.columns:
                    education_summary['Attending REC'] = children_edu_merged[attending_rec_col].sum()
                
                academic_issues_col = get_col_name('hasacademicissues', 'HasAcademicIssues')
                if academic_issues_col in children_edu_merged.columns:
                    education_summary['Has Academic Issues'] = children_edu_merged[academic_issues_col].sum()
                
                extra_curriculars_col = get_col_name('hasextracurriculars', 'HasExtraCurriculars')
                if extra_curriculars_col in children_edu_merged.columns:
                    education_summary['Has Extra Curriculars'] = children_edu_merged[extra_curriculars_col].sum()
                
                bullied_col = get_col_name('isbullied', 'IsBullied')
                if bullied_col in children_edu_merged.columns:
                    education_summary['Is Bullied'] = children_edu_merged[bullied_col].sum()
                
                behavior_challenges_col = get_col_name('hasbehaviorchallenges', 'HasBehaviorChallenges')
                if behavior_challenges_col in children_edu_merged.columns:
                    education_summary['Has Behavior Challenges'] = children_edu_merged[behavior_challenges_col].sum()
                
                disability_col = get_col_name('hasdisability', 'HasDisability')
                if disability_col in children_edu_merged.columns:
                    education_summary['Has Disability'] = children_edu_merged[disability_col].sum()
                
                learning_plans_col = get_col_name('hasspecializedlearningplans', 'HasSpecializedLearningPlans')
                if learning_plans_col in children_edu_merged.columns:
                    education_summary['Has Specialized Learning Plans'] = children_edu_merged[learning_plans_col].sum()
                
                edu_summary_df = pd.DataFrame(list(education_summary.items()), columns=['Category', 'Count'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Education Statistics")
                    st.dataframe(edu_summary_df, hide_index=True)
                
                with col2:
                    # Academic performance distribution
                    academic_perf_col = get_col_name('academicperformance', 'AcademicPerformance')
                    if academic_perf_col in children_edu_merged.columns:
                        perf_counts = children_edu_merged[academic_perf_col].dropna().value_counts()
                        if not perf_counts.empty:
                            perf_fig = px.bar(
                                x=perf_counts.index,
                                y=perf_counts.values,
                                title='Academic Performance Distribution',
                                labels={'x': 'Performance Level', 'y': 'Number of Children'},
                                color=perf_counts.values,
                                color_continuous_scale='Viridis'
                            )
                            perf_fig.update_layout(showlegend=False, coloraxis_showscale=False)
                            st.plotly_chart(perf_fig, use_container_width=True)
                
                # Detailed children education table
                st.markdown("### Detailed Children Education Data")
                
                # Select relevant columns for display with flexible column naming
                display_column_mapping = {
                    'firstname': ['firstname', 'FirstName'],
                    'lastname': ['lastname', 'LastName'], 
                    'age': ['age'],
                    'region': ['region', 'Region'],
                    'educationlevel': ['educationlevel', 'EducationLevel'],
                    'isattendingschool': ['isattendingschool', 'IsAttendingSchool'],
                    'schoolname': ['schoolname', 'SchoolName'],
                    'schoolgrade': ['schoolgrade', 'SchoolGrade'],
                    'academicperformance': ['academicperformance', 'AcademicPerformance'],
                    'hasacademicissues': ['hasacademicissues', 'HasAcademicIssues'],
                    'hasextracurriculars': ['hasextracurriculars', 'HasExtraCurriculars'],
                    'isbullied': ['isbullied', 'IsBullied'],
                    'hasbehaviorchallenges': ['hasbehaviorchallenges', 'HasBehaviorChallenges'],
                    'hasdisability': ['hasdisability', 'HasDisability']
                }
                
                # Find available columns
                available_columns = []
                column_display_names = []
                for display_name, possible_names in display_column_mapping.items():
                    for col_name in possible_names:
                        if col_name in children_edu_merged.columns:
                            available_columns.append(col_name)
                            column_display_names.append(display_name.replace('_', ' ').title())
                            break
                
                if available_columns:
                    children_display = children_edu_merged[available_columns].copy()
                    
                    # Replace boolean values with Yes/No for better readability
                    bool_columns = children_display.select_dtypes(include=['bool']).columns
                    for col in bool_columns:
                        children_display[col] = children_display[col].replace({True: 'Yes', False: 'No'})
                    
                    st.dataframe(children_display, hide_index=True)
                else:
                    st.info("No education data columns available for display.")
            else:
                st.info("No education data available for children in the system.")
            
            # Overall children data table with selection functionality
            st.markdown("### All Children Data")
            
            # Handle column name variations for children data
            children_column_mapping = {
                'personid': ['personid', 'PersonID'],
                'caseid': ['caseid', 'CaseID'],
                'firstname': ['firstname', 'FirstName'],
                'lastname': ['lastname', 'LastName'],
                'age': ['age'],
                'yearofbirth': ['yearofbirth', 'YearOfBirth'],
                'relationtohead': ['relationtohead', 'RelationToHead'],
                'countryoforigin': ['countryoforigin', 'CountryOfOrigin'],
                'educationlevel': ['educationlevel', 'EducationLevel'],
                'englishfluency': ['englishfluency', 'EnglishFluency'],
                'legalstatus': ['legalstatus', 'LegalStatus'],
                'usarrivalyear': ['usarrivalyear', 'USArrivalYear'],
                'borninusa': ['borninusa', 'BornInUSA']
            }
            
            available_child_cols = []
            for display_name, possible_names in children_column_mapping.items():
                for col_name in possible_names:
                    if col_name in children_df.columns:
                        available_child_cols.append(col_name)
                        break
            
            if available_child_cols:
                # Create a display dataframe with better formatting
                children_display_df = children_df[available_child_cols].copy()
                
                # Format boolean columns
                bool_columns = children_display_df.select_dtypes(include=['bool']).columns
                for col in bool_columns:
                    children_display_df[col] = children_display_df[col].replace({True: 'Yes', False: 'No'})
                
                # Display the dataframe
                st.dataframe(children_display_df, hide_index=True, use_container_width=True)
                
                # Child Selection for Detailed View
                st.markdown("### 🔍 Child Detailed Lookup")
                st.markdown("Select a child to view their complete information including education, health, social inclusion, and finance data.")
                
                # Get person and case ID columns
                person_id_col = 'personid' if 'personid' in children_df.columns else 'PersonID'
                case_id_col = 'caseid' if 'caseid' in children_df.columns else 'CaseID'
                firstname_col = 'firstname' if 'firstname' in children_df.columns else 'FirstName'
                lastname_col = 'lastname' if 'lastname' in children_df.columns else 'LastName'
                
                # Create options for the selectbox
                child_options = []
                for idx, child in children_df.iterrows():
                    child_name = f"{child[firstname_col]} {child[lastname_col]}"
                    child_id = child[person_id_col]
                    case_id = child[case_id_col]
                    age = child['age']
                    child_options.append(f"{child_name} (Age: {age}, Person ID: {child_id}, Case ID: {case_id})")
                
                selected_child_option = st.selectbox(
                    "Select a child to view detailed information:",
                    options=["Select a child..."] + child_options,
                    key="child_selector"
                )
                
                if selected_child_option != "Select a child...":
                    # Extract person ID from the selected option
                    import re
                    person_id_match = re.search(r'Person ID: (\d+)', selected_child_option)
                    if person_id_match:
                        selected_person_id = int(person_id_match.group(1))
                        selected_child = children_df[children_df[person_id_col] == selected_person_id].iloc[0]
                        
                        # Display detailed child information
                        st.markdown("---")
                        st.markdown(f"## 👶 Detailed Information for {selected_child[firstname_col]} {selected_child[lastname_col]}")
                        
                        # Create tabs for different data categories
                        child_tabs = st.tabs(["Personal Info", "Education", "Social Inclusion", "Finance", "Health", "Social Camp Eligibility"])
                        
                        with child_tabs[0]:  # Personal Info
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("### Basic Information")
                                st.markdown(f"**Full Name:** {selected_child[firstname_col]} {selected_child[lastname_col]}")
                                st.markdown(f"**Person ID:** {selected_child[person_id_col]}")
                                st.markdown(f"**Case ID:** {selected_child[case_id_col]}")
                                st.markdown(f"**Age:** {selected_child['age']}")
                                
                                year_col = 'yearofbirth' if 'yearofbirth' in selected_child.index else 'YearOfBirth'
                                if year_col in selected_child.index:
                                    st.markdown(f"**Year of Birth:** {int(selected_child[year_col]) if pd.notna(selected_child[year_col]) else 'N/A'}")
                                
                                relation_col = 'relationtohead' if 'relationtohead' in selected_child.index else 'RelationToHead'
                                if relation_col in selected_child.index:
                                    st.markdown(f"**Relation to Head:** {selected_child[relation_col]}")
                            
                            with col2:
                                st.markdown("### Background Information")
                                
                                country_col = 'countryoforigin' if 'countryoforigin' in selected_child.index else 'CountryOfOrigin'
                                if country_col in selected_child.index:
                                    st.markdown(f"**Country of Origin:** {selected_child[country_col]}")
                                
                                legal_col = 'legalstatus' if 'legalstatus' in selected_child.index else 'LegalStatus'
                                if legal_col in selected_child.index:
                                    st.markdown(f"**Legal Status:** {selected_child[legal_col]}")
                                
                                arrival_col = 'usarrivalyear' if 'usarrivalyear' in selected_child.index else 'USArrivalYear'
                                if arrival_col in selected_child.index:
                                    st.markdown(f"**USA Arrival Year:** {int(selected_child[arrival_col]) if pd.notna(selected_child[arrival_col]) else 'N/A'}")
                                
                                born_col = 'borninusa' if 'borninusa' in selected_child.index else 'BornInUSA'
                                if born_col in selected_child.index:
                                    born_status = 'Yes' if selected_child[born_col] else 'No'
                                    st.markdown(f"**Born in USA:** {born_status}")
                                
                                english_col = 'englishfluency' if 'englishfluency' in selected_child.index else 'EnglishFluency'
                                if english_col in selected_child.index:
                                    st.markdown(f"**English Fluency:** {selected_child[english_col]}")
                                
                                edu_level_col = 'educationlevel' if 'educationlevel' in selected_child.index else 'EducationLevel'
                                if edu_level_col in selected_child.index:
                                    st.markdown(f"**Education Level:** {selected_child[edu_level_col]}")
                        
                        with child_tabs[1]:  # Education
                            # Get education data for this specific child
                            child_education = education_df[education_df[person_id_col] == selected_person_id]
                            
                            if not child_education.empty:
                                edu = child_education.iloc[0]
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("### School Information")
                                    
                                    # School attendance
                                    attending_school_col = get_col_name('isattendingschool', 'IsAttendingSchool')
                                    if attending_school_col in edu.index:
                                        st.markdown(f"**Attending School:** {'Yes' if edu[attending_school_col] else 'No'}")
                                        
                                        if edu[attending_school_col]:
                                            school_name_col = get_col_name('schoolname', 'SchoolName')
                                            if school_name_col in edu.index and pd.notna(edu[school_name_col]):
                                                st.markdown(f"**School Name:** {edu[school_name_col]}")
                                            
                                            grade_col = get_col_name('schoolgrade', 'SchoolGrade')
                                            if grade_col in edu.index and pd.notna(edu[grade_col]):
                                                st.markdown(f"**Grade:** {edu[grade_col]}")
                                    
                                    # ECDC and REC attendance
                                    ecdc_col = get_col_name('isattendingecdc', 'IsAttendingECDC')
                                    if ecdc_col in edu.index:
                                        st.markdown(f"**Attending ECDC:** {'Yes' if edu[ecdc_col] else 'No'}")
                                    
                                    rec_col = get_col_name('isattendingrec', 'IsAttendingREC')
                                    if rec_col in edu.index:
                                        st.markdown(f"**Attending REC:** {'Yes' if edu[rec_col] else 'No'}")
                                
                                with col2:
                                    st.markdown("### Academic Performance")
                                    
                                    perf_col = get_col_name('academicperformance', 'AcademicPerformance')
                                    if perf_col in edu.index and pd.notna(edu[perf_col]):
                                        st.markdown(f"**Academic Performance:** {edu[perf_col]}")
                                    
                                    issues_col = get_col_name('hasacademicissues', 'HasAcademicIssues')
                                    if issues_col in edu.index:
                                        st.markdown(f"**Has Academic Issues:** {'Yes' if edu[issues_col] else 'No'}")
                                    
                                    extra_col = get_col_name('hasextracurriculars', 'HasExtraCurriculars')
                                    if extra_col in edu.index:
                                        st.markdown(f"**Has Extra Curriculars:** {'Yes' if edu[extra_col] else 'No'}")
                                
                                st.markdown("### Challenges & Support")
                                challenges = []
                                
                                bullied_col = get_col_name('isbullied', 'IsBullied')
                                if bullied_col in edu.index and edu[bullied_col]:
                                    challenges.append("Is bullied")
                                
                                behavior_col = get_col_name('hasbehaviorchallenges', 'HasBehaviorChallenges')
                                if behavior_col in edu.index and edu[behavior_col]:
                                    challenges.append("Has behavior challenges")
                                
                                disability_col = get_col_name('hasdisability', 'HasDisability')
                                if disability_col in edu.index and edu[disability_col]:
                                    challenges.append("Has disability")
                                
                                plans_col = get_col_name('hasspecializedlearningplans', 'HasSpecializedLearningPlans')
                                if plans_col in edu.index and edu[plans_col]:
                                    challenges.append("Has specialized learning plans")
                                
                                if challenges:
                                    st.markdown("**Current Challenges:**")
                                    for challenge in challenges:
                                        st.markdown(f"• {challenge}")
                                else:
                                    st.markdown("**Current Challenges:** None reported")
                                
                                # Education comments
                                comments_col = get_col_name('educationcomments', 'EducationComments')
                                if comments_col in edu.index and pd.notna(edu[comments_col]):
                                    st.markdown("### Additional Comments")
                                    st.markdown(edu[comments_col])
                            else:
                                st.info("No education data available for this child.")
                        
                        with child_tabs[2]:  # Social Inclusion
                            # Get social inclusion data for this child
                            child_social = social_inclusion_agency_df[social_inclusion_agency_df[person_id_col] == selected_person_id]
                            
                            if not child_social.empty:
                                social = child_social.iloc[0]
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("### Social Connection Status")
                                    
                                    # Check for various column name variations
                                    domain_status_cols = ['socialinclusiondomainstatus', 'SocialInclusionDomainStatus']
                                    for col in domain_status_cols:
                                        if col in social.index and pd.notna(social[col]):
                                            st.markdown(f"**Domain Status:** {social[col]}")
                                            break
                                    
                                    community_conn_cols = ['hascommunityconnection', 'HasCommunityConnection']
                                    for col in community_conn_cols:
                                        if col in social.index:
                                            st.markdown(f"**Has Community Connection:** {'Yes' if social[col] else 'No'}")
                                            break
                                    
                                    friend_conn_cols = ['hasfriendfamilyconnection', 'HasFriendFamilyConnection']
                                    for col in friend_conn_cols:
                                        if col in social.index:
                                            st.markdown(f"**Has Friend/Family Connection:** {'Yes' if social[col] else 'No'}")
                                            break
                                
                                with col2:
                                    st.markdown("### Jamat Khana Participation")
                                    
                                    attend_jk_cols = ['attendjk', 'AttendJK']
                                    for col in attend_jk_cols:
                                        if col in social.index:
                                            st.markdown(f"**Attends JK:** {'Yes' if social[col] else 'No'}")
                                            if social[col]:
                                                freq_cols = ['attendjkhowoften', 'AttendJkHowOften']
                                                for freq_col in freq_cols:
                                                    if freq_col in social.index and pd.notna(social[freq_col]):
                                                        st.markdown(f"**Attendance Frequency:** {social[freq_col]}")
                                                        break
                                            break
                                    
                                    jk_acceptance_cols = ['jkinstitutionalacceptance', 'JkInstitutionalAcceptance']
                                    for col in jk_acceptance_cols:
                                        if col in social.index:
                                            st.markdown(f"**JK Institutional Acceptance:** {'Yes' if social[col] else 'No'}")
                                            break
                                
                                # Current situation
                                st.markdown("### Current Situation")
                                current_sit_cols = ['currentsituation', 'CurrentSituation']
                                for col in current_sit_cols:
                                    if col in social.index and pd.notna(social[col]):
                                        st.markdown(f"**Current Situation:** {social[col]}")
                                        break
                                
                                # Comments
                                comment_cols = ['currentsituationcomments', 'CurrentSituationComments']
                                for col in comment_cols:
                                    if col in social.index and pd.notna(social[col]):
                                        st.markdown("### Additional Comments")
                                        st.markdown(social[col])
                                        break
                            else:
                                st.info("No social inclusion data available for this child.")
                        
                        with child_tabs[3]:  # Finance
                            # Get finance data for this child
                            child_finance = finance_df[finance_df[person_id_col] == selected_person_id]
                            
                            if not child_finance.empty:
                                finance = child_finance.iloc[0]
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("### Financial Status")
                                    
                                    domain_cols = ['financedomainstatus', 'FinanceDomainStatus']
                                    for col in domain_cols:
                                        if col in finance.index and pd.notna(finance[col]):
                                            st.markdown(f"**Finance Domain Status:** {finance[col]}")
                                            break
                                    
                                    benefits_cols = ['hasgovernmentbenefits', 'HasGovernmentBenefits']
                                    for col in benefits_cols:
                                        if col in finance.index:
                                            st.markdown(f"**Has Government Benefits:** {'Yes' if finance[col] else 'No'}")
                                            if finance[col]:
                                                benefit_type_cols = ['governmentbenefits', 'GovernmentBenefits']
                                                for bt_col in benefit_type_cols:
                                                    if bt_col in finance.index and pd.notna(finance[bt_col]):
                                                        st.markdown(f"**Benefit Types:** {finance[bt_col]}")
                                                        break
                                            break
                                
                                with col2:
                                    st.markdown("### Financial Support Needs")
                                    
                                    support_cols = ['financialsupport', 'FinancialSupport']
                                    for col in support_cols:
                                        if col in finance.index:
                                            st.markdown(f"**Needs Financial Support:** {'Yes' if finance[col] else 'No'}")
                                            break
                                    
                                    help_cols = ['ishelpneededmanagingfinance', 'IsHelpNeededManagingFinance']
                                    for col in help_cols:
                                        if col in finance.index:
                                            st.markdown(f"**Needs Help Managing Finances:** {'Yes' if finance[col] else 'No'}")
                                            break
                                
                                # Additional financial information
                                st.markdown("### Additional Financial Information")
                                
                                debt_cols = ['havedebt', 'HaveDebt']
                                for col in debt_cols:
                                    if col in finance.index:
                                        st.markdown(f"**Has Debt:** {'Yes' if finance[col] else 'No'}")
                                        break
                                
                                tax_cols = ['taxfiling', 'TaxFiling']
                                for col in tax_cols:
                                    if col in finance.index:
                                        st.markdown(f"**Tax Filing:** {'Yes' if finance[col] else 'No'}")
                                        break
                            else:
                                st.info("No financial data available for this child.")
                        
                        with child_tabs[4]:  # Health
                            # Get health data for this child
                            child_health = physical_mental_health_df[physical_mental_health_df[person_id_col] == selected_person_id]
                            
                            if not child_health.empty:
                                health = child_health.iloc[0]
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("### Physical Health")
                                    
                                    domain_cols = ['healthdomainstatus', 'HealthDomainStatus']
                                    for col in domain_cols:
                                        if col in health.index and pd.notna(health[col]):
                                            st.markdown(f"**Health Domain Status:** {health[col]}")
                                            break
                                    
                                    medical_cols = ['hasmedicalconditions', 'HasMedicalConditions']
                                    for col in medical_cols:
                                        if col in health.index:
                                            st.markdown(f"**Has Medical Conditions:** {'Yes' if health[col] else 'No'}")
                                            break
                                    
                                    insurance_cols = ['havehealthinsurance', 'HaveHealthInsurance']
                                    for col in insurance_cols:
                                        if col in health.index:
                                            st.markdown(f"**Has Health Insurance:** {'Yes' if health[col] else 'No'}")
                                            if health[col]:
                                                type_cols = ['typeofhealthinsurance', 'TypeOfHealthInsurance']
                                                for type_col in type_cols:
                                                    if type_col in health.index and pd.notna(health[type_col]):
                                                        st.markdown(f"**Insurance Type:** {health[type_col]}")
                                                        break
                                            break
                                    
                                    disability_cols = ['hasphysicaldisability', 'HasPhysicalDisability']
                                    for col in disability_cols:
                                        if col in health.index:
                                            st.markdown(f"**Has Physical Disability:** {'Yes' if health[col] else 'No'}")
                                            break
                                
                                with col2:
                                    st.markdown("### Healthcare Access")
                                    
                                    doctor_cols = ['hasprimarycaredoctor', 'HasPrimaryCareDoctor']
                                    for col in doctor_cols:
                                        if col in health.index:
                                            st.markdown(f"**Has Primary Care Doctor:** {'Yes' if health[col] else 'No'}")
                                            break
                                    
                                    preventive_cols = ['preventivecareexams', 'PreventiveCareExams']
                                    for col in preventive_cols:
                                        if col in health.index:
                                            st.markdown(f"**Gets Preventive Care:** {'Yes' if health[col] else 'No'}")
                                            break
                                    
                                    cost_cols = ['iscostpreventingmedicalcare', 'IsCostPreventingMedicalCare']
                                    for col in cost_cols:
                                        if col in health.index:
                                            st.markdown(f"**Cost Preventing Care:** {'Yes' if health[col] else 'No'}")
                                            break
                                
                                # Mental health indicators
                                st.markdown("### Mental Health Indicators")
                                mental_health_issues = []
                                
                                # Check for various mental health frequency indicators
                                freq_indicators = [
                                    ('littleinterestorpleasurefrequency', 'LittleInterestOrPleasureFrequency', 'Little interest or pleasure'),
                                    ('depressionfrequency', 'DepressionFrequency', 'Depression'),
                                    ('anxiousfrequency', 'AnxiousFrequency', 'Anxiety'),
                                    ('worryfrequency', 'WorryFrequency', 'Worry')
                                ]
                                
                                for lowercase, pascalcase, label in freq_indicators:
                                    for col in [lowercase, pascalcase]:
                                        if col in health.index and pd.notna(health[col]) and health[col] != "Never":
                                            mental_health_issues.append(f"{label}: {health[col]}")
                                            break
                                
                                if mental_health_issues:
                                    for issue in mental_health_issues:
                                        st.markdown(f"• {issue}")
                                else:
                                    st.markdown("No mental health concerns reported")
                            else:
                                st.info("No health data available for this child.")
                        
                        with child_tabs[5]:  # Social Camp Eligibility
                            st.markdown("### 🏕️ Camp Mosaic Eligibility")
                            
                            child_age = selected_child['age']
                            
                            # Camp Mosaic eligibility (ages 6-13)
                            st.markdown("#### Camp Mosaic")
                            st.markdown("**Age Range:** 6-13 years old")
                            
                            if 6 <= child_age <= 13:
                                st.success(f"✅ **ELIGIBLE** - {selected_child[firstname_col]} is {child_age} years old")
                                st.markdown("🎯 **Next Steps:** Contact camp coordinator to register")
                                
                                # Camp information for eligible children
                                st.markdown("---")
                                st.markdown("### 📋 Camp Mosaic Information")
                                st.markdown("""
                                **Camp Mosaic Program Features:**
                                - Social skills development and community building
                                - Age-appropriate activities and educational programming
                                - Cultural integration and peer interaction
                                - Leadership development opportunities
                                - Recreational and outdoor activities
                                """)
                                
                                # Action items
                                st.markdown("### 🎯 Recommended Actions")
                                st.markdown("- [ ] Contact camp coordinator for registration information")
                                st.markdown("- [ ] Check for upcoming camp dates and availability")
                                st.markdown("- [ ] Verify any additional requirements or documentation needed")
                                st.markdown("- [ ] Consider transportation arrangements if needed")
                                st.markdown("- [ ] Complete any required health forms or permissions")
                                
                            else:
                                st.error(f"❌ **NOT ELIGIBLE** - {selected_child[firstname_col]} is {child_age} years old")
                                
                                if child_age < 6:
                                    st.info(f"📅 **Future Eligibility:** Will be eligible for Camp Mosaic in {6 - child_age} year(s) when they turn 6")
                                elif child_age > 13:
                                    st.info("🔄 **Too old for Camp Mosaic** - May be eligible to be a guide or counselor for the camp")
            else:
                st.dataframe(children_df)
        else:
            st.info("No children (18 and under) found in the current dataset.")
        
    with case_lookup:
        st.subheader("Settlement Case Lookup")
        
        # Initialize session state for the assessment form
        if 'show_assessment_form' not in st.session_state:
            st.session_state.show_assessment_form = False
        if 'current_case_id' not in st.session_state:
            st.session_state.current_case_id = None
            
        # Function to toggle form visibility
        def toggle_assessment_form():
            st.session_state.show_assessment_form = not st.session_state.show_assessment_form
            
        # Get list of all case IDs for dropdown
        case_ids = df['caseid'].unique().tolist()
        case_ids.sort()
        
        # Create a search box for case ID
        selected_case_id = st.selectbox("Select or type a Case ID:", options=case_ids)
        
        if st.button("Look Up Case"):
            st.session_state.current_case_id = selected_case_id
            st.session_state.show_assessment_form = False
            
        if st.session_state.current_case_id:
            selected_case_id = st.session_state.current_case_id
            # Create a connection for this specific query
            try:
                conn = psycopg2.connect(DATABASE_URL)
                # Get case data
                case_data = df[df['caseid'] == selected_case_id].iloc[0]

                # Display case information in an expandable section
                with st.expander("Case Information", expanded=True):
                    # Create two columns for case info
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### Basic Information")
                        st.markdown(f"**Case ID:** {case_data['caseid']}")
                        st.markdown(f"**Region:** {case_data['region']}")
                        st.markdown(f"**Jamat Khana:** {case_data['jamatkhana']}")
                        st.markdown(f"**Status:** {case_data['status']}")
                        st.markdown(f"**Assigned To:** {case_data['assignedto']}")

                    with col2:
                        st.markdown("### Contact Information")
                        st.markdown(f"**Name:** {case_data['firstname']} {case_data['lastname']}")
                        st.markdown(f"**Phone:** {case_data['phonenumber']}")
                        st.markdown(f"**Email:** {case_data['email']}")
                        st.markdown(f"**Location:** {case_data['city']}, {case_data['state']} {case_data['zip']}")

                    st.markdown("### Case Timeline")
                    st.markdown(f"**Creation Date:** {case_data['creationdate'].strftime('%B %d, %Y') if pd.notna(case_data['creationdate']) else 'N/A'}")
                    st.markdown(f"**Open/Reopen Date:** {case_data['openreopendate'].strftime('%B %d, %Y') if pd.notna(case_data['openreopendate']) else 'N/A'}")
                    st.markdown(f"**Last Log Date:** {case_data['lastlogdate'].strftime('%B %d, %Y') if pd.notna(case_data['lastlogdate']) else 'N/A'}")

                # Add a Quick Form button with on-click handler to toggle form visibility
                if st.button("Add Quick Assessment", on_click=toggle_assessment_form):
                    pass  # The on_click handler will toggle the form visibility

                # Show the form if the toggle is True
                if st.session_state.show_assessment_form:
                    with st.form(key="FDP Assessment Form"):
                        st.markdown(
                            """
                            <div style="background-color:#191d36; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                                <h3 style="color:#abafc7; margin:0;">FDP Assessment Form</h3>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # Form fields
                        family_status = st.selectbox(
                            "Family Progress Status",
                            options=["Stable", "At Risk", "In Crisis", "Unknown"]
                        )

                        fdp_field1 = st.text_area("FDP Field 1", placeholder="Enter information here...")
                        fdp_field2 = st.text_area("FDP Field 2", placeholder="Enter information here...")
                        fdp_field3 = st.text_area("FDP Field 3", placeholder="Enter information here...")

                        # Form submission buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            submit_button = st.form_submit_button("Submit")
                        with col2:
                            clear_button = st.form_submit_button("Clear")

                        if submit_button:
                            st.success("Form submitted successfully! (Note: This is a dummy form, data is not saved)")
                            st.session_state.show_assessment_form = False  # Hide form after submission

                        if clear_button:
                            # This doesn't actually clear the form (would need JavaScript), 
                            # but provides user feedback
                            st.info("Form cleared (refresh to reset fields)")

                # Get all Jamati members associated with this case
                jamati_members = jamati_member_df[jamati_member_df['caseid'] == selected_case_id]

                # Display a summary of family members
                st.markdown(f"### Family Members ({len(jamati_members)})")

                # Loop through each family member
                for idx, member in jamati_members.iterrows():
                    person_id = member['personid']

                    # Create an expandable section for each member
                    with st.expander(f"{member['firstname']} {member['lastname']} ({member['relationtohead']})"):
                        tabs = st.tabs(["Personal Info", "Education", "Social Inclusion", "Finance", "Health"])
                        
                        with tabs[0]:  # Personal Info
                            st.markdown(f"**Name:** {member['firstname']} {member['lastname']}")
                            st.markdown(f"**Relation to Head:** {member['relationtohead']}")
                            st.markdown(f"**Year of Birth:** {int(member['yearofbirth']) if pd.notna(member['yearofbirth']) else 'N/A'}")
                            
                            # Calculate age if year of birth is available
                            if pd.notna(member['yearofbirth']):
                                age = datetime.now().year - int(member['yearofbirth'])
                                st.markdown(f"**Age:** {age}")
                                
                            st.markdown(f"**Country of Origin:** {member['countryoforigin']}")
                            st.markdown(f"**Legal Status:** {member['legalstatus']}")
                            st.markdown(f"**USA Arrival Year:** {int(member['usarrivalyear']) if pd.notna(member['usarrivalyear']) else 'N/A'}")
                            st.markdown(f"**Born in USA:** {'Yes' if member['borninusa'] else 'No'}")
                            st.markdown(f"**English Fluency:** {member['englishfluency']}")
                            st.markdown(f"**Education Level:** {member['educationlevel']}")
                        
                        with tabs[1]:  # Education
                            # Get education data for this person
                            edu_data = education_df[education_df['personid'] == person_id]
                            
                            if not edu_data.empty:
                                edu = edu_data.iloc[0]
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("### Education Status")
                                    st.markdown(f"**Education Level:** {edu['educationlevel']}")
                                    st.markdown(f"**English Fluency:** {edu['englishfluency']}")
                                    st.markdown(f"**Attending ECDC:** {'Yes' if edu['isattendingecdc'] else 'No'}")
                                    st.markdown(f"**Attending REC:** {'Yes' if edu['isattendingrec'] else 'No'}")
                                    st.markdown(f"**Attending School:** {'Yes' if edu['isattendingschool'] else 'No'}")
                                    
                                    if edu['isattendingschool']:
                                        st.markdown(f"**School Name:** {edu['schoolname']}")
                                        st.markdown(f"**Grade:** {edu['schoolgrade']}")
                                        st.markdown(f"**Attendance Type:** {edu['attendancetype']}")
                                
                                with col2:
                                    st.markdown("### Performance & Challenges")
                                    st.markdown(f"**Extra Curriculars:** {'Yes' if edu['hasextracurriculars'] else 'No'}")
                                    st.markdown(f"**Academic Issues:** {'Yes' if edu['hasacademicissues'] else 'No'}")
                                    st.markdown(f"**Academic Performance:** {edu['academicperformance']}")
                                    st.markdown(f"**Academic Assistance:** {edu['academicassistancetype']}")
                                    st.markdown(f"**Comfortable with Teacher:** {'Yes' if edu['comfortablewithteacher'] else 'No'}")
                                    
                                    if pd.notna(edu['comfortablewithteachercomments']):
                                        st.markdown(f"**Teacher Comments:** {edu['comfortablewithteachercomments']}")
                                
                                st.markdown("### Additional Challenges")
                                challenges = []
                                if edu['isbullied']: challenges.append("Is bullied")
                                if edu['hasbehaviorchallenges']: challenges.append("Has behavior challenges")
                                if edu['hasdisability']: challenges.append("Has disability")
                                if edu['hasspecializedlearningplans']: challenges.append("Has specialized learning plans")
                                if edu['hasotherchallenges']: challenges.append("Has other challenges")
                                
                                if challenges:
                                    st.markdown("**Challenges:** " + ", ".join(challenges))
                                else:
                                    st.markdown("**Challenges:** None reported")
                                
                                if pd.notna(edu['hasotherchallengescomments']):
                                    st.markdown(f"**Other Challenges Comments:** {edu['hasotherchallengescomments']}")
                                
                                st.markdown(f"**Coping with Challenges:** {'Yes' if edu['iscoping'] else 'No'}")
                                
                                if pd.notna(edu['educationcomments']):
                                    st.markdown("### Additional Comments")
                                    st.markdown(edu['educationcomments'])
                            else:
                                st.info("No education data available for this family member.")
                        
                        with tabs[2]:  # Social Inclusion
                            # Get social inclusion data for this person
                            social_data = social_inclusion_agency_df[social_inclusion_agency_df['personid'] == person_id]
                            
                            if not social_data.empty:
                                social = social_data.iloc[0]
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("### Social Inclusion Status")
                                    st.markdown(f"**Domain Status:** {social['socialinclusiondomainstatus']}")
                                    st.markdown(f"**Goal Status:** {social['socialinclusiondomaingoalstatus']}")
                                    st.markdown(f"**Commuting Type:** {social['commutingtype']}")
                                    st.markdown(f"**Community Connection:** {'Yes' if social['hascommunityconnection'] else 'No'}")
                                    st.markdown(f"**JK Institutional Acceptance:** {'Yes' if social['jkinstitutionalacceptance'] else 'No'}")
                                    
                                    if pd.notna(social['socialsupportcomments']):
                                        st.markdown(f"**Social Support Comments:** {social['socialsupportcomments']}")
                                
                                with col2:
                                    st.markdown("### Relationships & Connections")
                                    st.markdown(f"**Friend/Family Connection:** {'Yes' if social['hasfriendfamilyconnection'] else 'No'}")
                                    
                                    if pd.notna(social['familyfriendconnectioncomments']):
                                        st.markdown(f"**Connection Comments:** {social['familyfriendconnectioncomments']}")
                                    
                                    if pd.notna(social['familyrelationshipcomments']):
                                        st.markdown(f"**Family Relationship Comments:** {social['familyrelationshipcomments']}")
                                    
                                    st.markdown(f"**Attends JK:** {'Yes' if social['attendjk'] else 'No'}")
                                    
                                    if social['attendjk']:
                                        st.markdown(f"**JK Attendance Frequency:** {social['attendjkhowoften']}")
                                    elif pd.notna(social['reasonfornotattendingjk']):
                                        st.markdown(f"**Reason for Not Attending:** {social['reasonfornotattendingjk']}")
                                
                                st.markdown("### Additional Information")
                                st.markdown(f"**Needs Social Integration Assistance:** {'Yes' if social['assistancesocialintegration'] else 'No'}")
                                st.markdown(f"**Cell Phone Access:** {'Yes' if social['hascellphoneaccess'] else 'No'}")
                                
                                if pd.notna(social['cellphoneaccesscomments']):
                                    st.markdown(f"**Cell Phone Comments:** {social['cellphoneaccesscomments']}")
                                
                                st.markdown(f"**Current Situation:** {social['currentsituation']}")
                                
                                if pd.notna(social['currentsituationcomments']):
                                    st.markdown(f"**Current Situation Comments:** {social['currentsituationcomments']}")
                            else:
                                st.info("No social inclusion data available for this family member.")
                        
                        with tabs[3]:  # Finance
                            # Get finance data for this person
                            finance_data = finance_df[finance_df['personid'] == person_id]
                            
                            if not finance_data.empty:
                                finance = finance_data.iloc[0]
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("### Financial Status")
                                    st.markdown(f"**Domain Status:** {finance['financedomainstatus']}")
                                    st.markdown(f"**Goal Status:** {finance['financedomaingoalstatus']}")
                                    st.markdown(f"**Government Benefits:** {'Yes' if finance['hasgovernmentbenefits'] else 'No'}")
                                    
                                    if finance['hasgovernmentbenefits'] and pd.notna(finance['governmentbenefits']):
                                        st.markdown(f"**Benefit Types:** {finance['governmentbenefits']}")
                                    elif pd.notna(finance['nogovernmentbenefitscomments']):
                                        st.markdown(f"**No Benefits Comments:** {finance['nogovernmentbenefitscomments']}")
                                    
                                    st.markdown(f"**Tax Filing:** {'Yes' if finance['taxfiling'] else 'No'}")
                                
                                with col2:
                                    st.markdown("### Assets & Debts")
                                    if pd.notna(finance['assettype']):
                                        st.markdown(f"**Asset Types:** {finance['assettype']}")
                                    
                                    if pd.notna(finance['assetscomments']):
                                        st.markdown(f"**Assets Comments:** {finance['assetscomments']}")
                                    
                                    st.markdown(f"**Has Debt:** {'Yes' if finance['havedebt'] else 'No'}")
                                    
                                    if finance['havedebt'] and pd.notna(finance['debtcomments']):
                                        st.markdown(f"**Debt Comments:** {finance['debtcomments']}")
                                
                                st.markdown("### Financial Support")
                                st.markdown(f"**Sends Money to Home Country:** {'Yes' if finance['sendmoneybackhome'] else 'No'}")
                                st.markdown(f"**Needs Financial Support:** {'Yes' if finance['financialsupport'] else 'No'}")
                                
                                if finance['financialsupport'] and pd.notna(finance['financialsupportcomments']):
                                    st.markdown(f"**Financial Support Comments:** {finance['financialsupportcomments']}")
                                
                                st.markdown(f"**Needs Help Managing Finances:** {'Yes' if finance['ishelpneededmanagingfinance'] else 'No'}")
                                
                                if finance['ishelpneededmanagingfinance'] and pd.notna(finance['helpmanagingfinancecomments']):
                                    st.markdown(f"**Finance Management Comments:** {finance['helpmanagingfinancecomments']}")
                                
                                st.markdown(f"**Share Contact Info for Financial Planning:** {'Yes' if finance['sharecontactinfoforfinplanning'] else 'No'}")
                                
                                if pd.notna(finance['sharecontactinfoforfinplanningcomments']):
                                    st.markdown(f"**Contact Sharing Comments:** {finance['sharecontactinfoforfinplanningcomments']}")
                            else:
                                st.info("No financial data available for this family member.")
                        
                        with tabs[4]:  # Health
                            # Get health data for this person
                            health_data = physical_mental_health_df[physical_mental_health_df['personid'] == person_id]
                            
                            if not health_data.empty:
                                health = health_data.iloc[0]
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("### Health Status")
                                    st.markdown(f"**Domain Status:** {health['healthdomainstatus']}")
                                    st.markdown(f"**Goal Status:** {health['healthdomaingoalstatus']}")
                                    st.markdown(f"**Medical Conditions:** {'Yes' if health['hasmedicalconditions'] else 'No'}")
                                    
                                    if health['hasmedicalconditions'] and pd.notna(health['medicalcomments']):
                                        st.markdown(f"**Medical Comments:** {health['medicalcomments']}")
                                    
                                    st.markdown(f"**Cost Preventing Medical Care:** {'Yes' if health['iscostpreventingmedicalcare'] else 'No'}")
                                    
                                    if health['iscostpreventingmedicalcare'] and pd.notna(health['costpreventingmedicalcarecomments']):
                                        st.markdown(f"**Cost Comments:** {health['costpreventingmedicalcarecomments']}")
                                
                                with col2:
                                    st.markdown("### Healthcare Access")
                                    st.markdown(f"**Health Insurance:** {'Yes' if health['havehealthinsurance'] else 'No'}")
                                    
                                    if health['havehealthinsurance']:
                                        st.markdown(f"**Insurance Type:** {health['typeofhealthinsurance']}")
                                        
                                        if pd.notna(health['healthinsurancecomments']):
                                            st.markdown(f"**Insurance Comments:** {health['healthinsurancecomments']}")
                                    
                                    st.markdown(f"**Primary Care Doctor:** {'Yes' if health['hasprimarycaredoctor'] else 'No'}")
                                    
                                    if pd.notna(health['primarycaredoctorcomments']):
                                        st.markdown(f"**Doctor Comments:** {health['primarycaredoctorcomments']}")
                                    
                                    st.markdown(f"**Preventive Care Exams:** {'Yes' if health['preventivecareexams'] else 'No'}")
                                    
                                    if pd.notna(health['preventivecareexamscomments']):
                                        st.markdown(f"**Preventive Care Comments:** {health['preventivecareexamscomments']}")
                                
                                st.markdown("### Physical Health")
                                st.markdown(f"**Physical Disability:** {'Yes' if health['hasphysicaldisability'] else 'No'}")
                                
                                if health['hasphysicaldisability'] and pd.notna(health['physicaldisabilitycomments']):
                                    st.markdown(f"**Disability Comments:** {health['physicaldisabilitycomments']}")
                                
                                st.markdown(f"**Share Info with AKHB:** {'Yes' if health['shareinfowithakhb'] else 'No'}")
                                
                                if pd.notna(health['shareinfowithakhbcomments']):
                                    st.markdown(f"**AKHB Sharing Comments:** {health['shareinfowithakhbcomments']}")
                                
                                st.markdown("### Mental Health")
                                mental_health_issues = []
                                
                                if pd.notna(health['littleinterestorpleasurefrequency']) and health['littleinterestorpleasurefrequency'] != "Never":
                                    mental_health_issues.append(f"Little interest or pleasure: {health['littleinterestorpleasurefrequency']}")
                                
                                if pd.notna(health['depressionfrequency']) and health['depressionfrequency'] != "Never":
                                    mental_health_issues.append(f"Depression: {health['depressionfrequency']}")
                                
                                if pd.notna(health['anxiousfrequency']) and health['anxiousfrequency'] != "Never":
                                    mental_health_issues.append(f"Anxiety: {health['anxiousfrequency']}")
                                
                                if pd.notna(health['worryfrequency']) and health['worryfrequency'] != "Never":
                                    mental_health_issues.append(f"Worry: {health['worryfrequency']}")
                                
                                if pd.notna(health['relationshipfrequency']) and health['relationshipfrequency'] != "Never":
                                    mental_health_issues.append(f"Relationship issues: {health['relationshipfrequency']}")
                                
                                if mental_health_issues:
                                    for issue in mental_health_issues:
                                        st.markdown(f"• {issue}")
                                else:
                                    st.markdown("No mental health issues reported")
                                
                                if pd.notna(health['littleinterestcomments']):
                                    st.markdown(f"**Interest Comments:** {health['littleinterestcomments']}")
                                
                                if pd.notna(health['depressioncomments']):
                                    st.markdown(f"**Depression Comments:** {health['depressioncomments']}")
                                
                                if pd.notna(health['anxiouscomments']):
                                    st.markdown(f"**Anxiety Comments:** {health['anxiouscomments']}")
                                
                                if pd.notna(health['worrycomments']):
                                    st.markdown(f"**Worry Comments:** {health['worrycomments']}")
                                
                                if pd.notna(health['familyrelationshipcomments']):
                                    st.markdown(f"**Relationship Comments:** {health['familyrelationshipcomments']}")
                                
                                st.markdown("### Substance Use & Stress")
                                st.markdown(f"**Substance Use Affects Work:** {'Yes' if health['substanceuseaffectswork'] else 'No'}")
                                
                                if pd.notna(health['substanceusecomments']):
                                    st.markdown(f"**Substance Use Comments:** {health['substanceusecomments']}")
                                
                                st.markdown(f"**Has Stress Management Strategies:** {'Yes' if health['hasstressmanagementstrategies'] else 'No'}")
                                
                                if pd.notna(health['stressmanagementcomments']):
                                    st.markdown(f"**Stress Management Comments:** {health['stressmanagementcomments']}")
                            else:
                                st.info("No health data available for this family member.")
                    
                conn.close()

            except Exception as e:
                st.error(f"Error retrieving data: {e}")

except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")
