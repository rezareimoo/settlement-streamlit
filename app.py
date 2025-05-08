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

    cases, jamati_demographics, case_lookup = st.tabs(["Cases", "Jamati Demographics", "Case Lookup"])

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
        
    with case_lookup:
        st.subheader("Settlement Case Lookup")
        
        # Get list of all case IDs for dropdown
        case_ids = df['caseid'].unique().tolist()
        case_ids.sort()
        
        # Create a search box for case ID
        selected_case_id = st.selectbox("Select or type a Case ID:", options=case_ids)
        
        if st.button("Look Up Case"):
            if selected_case_id:
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
                                        elif pd.notna(social['reasonfornotattendingk']):
                                            st.markdown(f"**Reason for Not Attending:** {social['reasonfornotattendingk']}")
                                    
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
                    
                    # Close the connection
                    conn.close()
                    
                except Exception as e:
                    st.error(f"Error retrieving data: {e}")
            else:
                st.warning("Please select a Case ID to look up.")

except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")
