import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import get_custom_data_by_case_id, save_custom_data, delete_custom_data

def render_case_lookup_tab(df, jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df):
    """Render the Case Lookup tab with comprehensive case and family member information"""
    
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
        
        # Get case data
        case_data = df[df['caseid'] == selected_case_id].iloc[0]

        # Display case information in an expandable section
        render_case_information(case_data)
        
        # Check if custom data exists for this case
        existing_custom_data = get_custom_data_by_case_id(selected_case_id)
        
        # Display existing custom data if available
        if existing_custom_data:
            with st.expander("Quick Assessment Data", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Family Progress Status:** {existing_custom_data['family_progress_status']}")
                    st.markdown(f"**Arrival Date:** {existing_custom_data['arrival_date'].strftime('%m/%d/%Y') if existing_custom_data['arrival_date'] else 'N/A'}")
                
                with col2:
                    languages = existing_custom_data['languages_spoken'] if existing_custom_data['languages_spoken'] else []
                    languages_str = ", ".join(languages) if languages else "None specified"
                    st.markdown(f"**Languages Spoken:** {languages_str}")
        
        # Add a Quick Assessment button with appropriate text
        button_text = "Edit Quick Assessment" if existing_custom_data else "Add Quick Assessment"
        if st.button(button_text, on_click=toggle_assessment_form):
            pass  # The on_click handler will toggle the form visibility

        # Show the form if the toggle is True
        if st.session_state.show_assessment_form:
            render_assessment_form()

        # Get all Jamati members associated with this case
        jamati_members = jamati_member_df[jamati_member_df['caseid'] == selected_case_id]

        # Display a summary of family members
        st.markdown(f"### Family Members ({len(jamati_members)})")

        # Loop through each family member
        for idx, member in jamati_members.iterrows():
            person_id = member['personid']

            # Create an expandable section for each member
            with st.expander(f"{member['firstname']} {member['lastname']} ({member['relationtohead']})"):
                render_family_member_tabs(member, person_id, education_df, social_inclusion_agency_df, finance_df, physical_mental_health_df)

def render_case_information(case_data):
    """Render the case information section"""
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
            st.markdown(f"**Input Type:** {case_data['inputtype'] if pd.notna(case_data['inputtype']) else 'N/A'}")

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

def render_assessment_form():
    """Render the Quick Assessment form"""
    case_id = st.session_state.current_case_id
    
    # Load existing data if available
    existing_data = get_custom_data_by_case_id(case_id)
    
    with st.form(key="Quick Assessment Form"):
        st.markdown(
            """
            <div style="background-color:#191d36; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                <h3 style="color:#abafc7; margin:0;">Quick Assessment Form</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Family Progress Status dropdown
        progress_options = [
            "Withdrawn/Migrated",
            "Stalled", 
            "Stabilizing",
            "Developing",
            "Self-Sufficient",
            "Graduated"
        ]
        
        default_progress = progress_options.index(existing_data['family_progress_status']) if existing_data and existing_data['family_progress_status'] in progress_options else 0
        family_progress_status = st.selectbox(
            "Family Progress Status",
            options=progress_options,
            index=default_progress
        )

        # Arrival Date
        default_arrival_date = None
        if existing_data and existing_data['arrival_date']:
            try:
                if isinstance(existing_data['arrival_date'], str):
                    default_arrival_date = datetime.strptime(existing_data['arrival_date'], '%Y-%m-%d').date()
                else:
                    default_arrival_date = existing_data['arrival_date']
            except:
                default_arrival_date = None
                
        arrival_date = st.date_input(
            "Arrival Date",
            value=default_arrival_date,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="MM/DD/YYYY"
        )

        # Languages Spoken - multi-select
        language_options = [
            "English",
            "Dari", 
            "Pashto",
            "Tajik",
            "Persian",
            "Urdu",
            "Hindi",
            "Gujarati"
        ]
        
        default_languages = []
        if existing_data and existing_data['languages_spoken']:
            default_languages = existing_data['languages_spoken'] if isinstance(existing_data['languages_spoken'], list) else []
        
        languages_spoken = st.multiselect(
            "Languages Spoken",
            options=language_options,
            default=default_languages
        )

        # Form submission buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            save_button = st.form_submit_button("Save", type="primary")
        with col2:
            delete_button = st.form_submit_button("Delete", type="secondary")
        with col3:
            cancel_button = st.form_submit_button("Cancel")

        if save_button:
            # Validate that arrival_date is not None
            if arrival_date is None:
                st.error("Please select an arrival date.")
            else:
                # Save to database
                success = save_custom_data(
                    case_id=case_id,
                    family_progress_status=family_progress_status,
                    languages_spoken=languages_spoken,
                    arrival_date=arrival_date
                )
                
                if success:
                    action = "updated" if existing_data else "saved"
                    st.success(f"Quick assessment {action} successfully!")
                    st.session_state.show_assessment_form = False
                    st.rerun()
                else:
                    st.error("Error saving quick assessment. Please try again.")

        if delete_button:
            if existing_data:
                success = delete_custom_data(case_id)
                if success:
                    st.success("Quick assessment deleted successfully!")
                    st.session_state.show_assessment_form = False
                    st.rerun()
                else:
                    st.error("Error deleting quick assessment. Please try again.")
            else:
                st.warning("No existing data to delete.")

        if cancel_button:
            st.session_state.show_assessment_form = False
            st.rerun()

def render_family_member_tabs(member, person_id, education_df, social_inclusion_agency_df, finance_df, physical_mental_health_df):
    """Render tabs for each family member with their detailed information"""
    tabs = st.tabs(["Personal Info", "Education", "Social Inclusion", "Finance", "Health"])
    
    with tabs[0]:  # Personal Info
        render_personal_info_tab(member)
    
    with tabs[1]:  # Education
        render_member_education_tab(person_id, education_df)
    
    with tabs[2]:  # Social Inclusion
        render_member_social_inclusion_tab(person_id, social_inclusion_agency_df)
    
    with tabs[3]:  # Finance
        render_member_finance_tab(person_id, finance_df)
    
    with tabs[4]:  # Health
        render_member_health_tab(person_id, physical_mental_health_df)

def render_personal_info_tab(member):
    """Render personal information for a family member"""
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

def render_member_education_tab(person_id, education_df):
    """Render education information for a family member"""
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
        
        with col2:
            st.markdown("### Performance & Challenges")
            st.markdown(f"**Extra Curriculars:** {'Yes' if edu['hasextracurriculars'] else 'No'}")
            st.markdown(f"**Academic Issues:** {'Yes' if edu['hasacademicissues'] else 'No'}")
            st.markdown(f"**Academic Performance:** {edu['academicperformance']}")
        
        # Additional challenges
        challenges = []
        if edu['isbullied']: challenges.append("Is bullied")
        if edu['hasbehaviorchallenges']: challenges.append("Has behavior challenges")
        if edu['hasdisability']: challenges.append("Has disability")
        if edu['hasspecializedlearningplans']: challenges.append("Has specialized learning plans")
        
        if challenges:
            st.markdown("**Challenges:** " + ", ".join(challenges))
        else:
            st.markdown("**Challenges:** None reported")
        
        # Display all comments
        comments = []
        comment_fields = [
            'comfortablewithteachercomments',
            'hasotherchallengescomments', 
            'educationcomments'
        ]
        
        for field in comment_fields:
            if field in edu.index and pd.notna(edu[field]) and str(edu[field]).strip():
                comments.append(str(edu[field]).strip())
        
        if comments:
            st.markdown("### Comments")
            st.markdown("**Comments:** " + "\n\n".join(comments))
    else:
        st.info("No education data available for this family member.")

def render_member_social_inclusion_tab(person_id, social_inclusion_agency_df):
    """Render social inclusion information for a family member"""
    # Get social inclusion data for this person
    social_data = social_inclusion_agency_df[social_inclusion_agency_df['personid'] == person_id]
    
    if not social_data.empty:
        social = social_data.iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Social Inclusion Status")
            st.markdown(f"**Domain Status:** {social['socialinclusiondomainstatus']}")
            st.markdown(f"**Community Connection:** {'Yes' if social['hascommunityconnection'] else 'No'}")
            st.markdown(f"**JK Institutional Acceptance:** {'Yes' if social['jkinstitutionalacceptance'] else 'No'}")
        
        with col2:
            st.markdown("### Relationships & Connections")
            st.markdown(f"**Friend/Family Connection:** {'Yes' if social['hasfriendfamilyconnection'] else 'No'}")
            st.markdown(f"**Attends JK:** {'Yes' if social['attendjk'] else 'No'}")
            
            if social['attendjk']:
                st.markdown(f"**JK Attendance Frequency:** {social['attendjkhowoften']}")
        
        st.markdown("### Additional Information")
        st.markdown(f"**Current Situation:** {social['currentsituation']}")
        
        # Display all comments
        comments = []
        comment_fields = [
            'socialsupportcomments',
            'familyfriendconnectioncomments',
            'familyrelationshipcomments',
            'reasonfornotattendingjk',
            'cellphoneaccesscomments',
            'currentsituationcomments'
        ]
        
        for field in comment_fields:
            if field in social.index and pd.notna(social[field]) and str(social[field]).strip():
                comments.append(str(social[field]).strip())
        
        if comments:
            st.markdown("### Comments")
            st.markdown("**Comments:** " + "\n\n".join(comments))
    else:
        st.info("No social inclusion data available for this family member.")

def render_member_finance_tab(person_id, finance_df):
    """Render finance information for a family member"""
    # Get finance data for this person
    finance_data = finance_df[finance_df['personid'] == person_id]
    
    if not finance_data.empty:
        finance = finance_data.iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Financial Status")
            st.markdown(f"**Domain Status:** {finance['financedomainstatus']}")
            st.markdown(f"**Government Benefits:** {'Yes' if finance['hasgovernmentbenefits'] else 'No'}")
            
            if finance['hasgovernmentbenefits'] and pd.notna(finance['governmentbenefits']):
                st.markdown(f"**Benefit Types:** {finance['governmentbenefits']}")
            
            st.markdown(f"**Tax Filing:** {'Yes' if finance['taxfiling'] else 'No'}")
        
        with col2:
            st.markdown("### Financial Support")
            st.markdown(f"**Needs Financial Support:** {'Yes' if finance['financialsupport'] else 'No'}")
            st.markdown(f"**Needs Help Managing Finances:** {'Yes' if finance['ishelpneededmanagingfinance'] else 'No'}")
            st.markdown(f"**Has Debt:** {'Yes' if finance['havedebt'] else 'No'}")
        
        # Display all comments
        comments = []
        comment_fields = [
            'governmentbenefits',
            'nogovernmentbenefitscomments',
            'assetscomments',
            'debtcomments',
            'financialsupportcomments',
            'helpmanagingfinancecomments',
            'sharecontactinfoforfinplanningcomments'
        ]
        
        for field in comment_fields:
            if field in finance.index and pd.notna(finance[field]) and str(finance[field]).strip():
                comments.append(str(finance[field]).strip())
        
        if comments:
            st.markdown("### Comments")
            st.markdown("**Comments:** " + "\n\n".join(comments))
    else:
        st.info("No financial data available for this family member.")

def render_member_health_tab(person_id, physical_mental_health_df):
    """Render health information for a family member"""
    # Get health data for this person
    health_data = physical_mental_health_df[physical_mental_health_df['personid'] == person_id]
    
    if not health_data.empty:
        health = health_data.iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Health Status")
            st.markdown(f"**Domain Status:** {health['healthdomainstatus']}")
            st.markdown(f"**Medical Conditions:** {'Yes' if health['hasmedicalconditions'] else 'No'}")
            st.markdown(f"**Health Insurance:** {'Yes' if health['havehealthinsurance'] else 'No'}")
            
            if health['havehealthinsurance']:
                st.markdown(f"**Insurance Type:** {health['typeofhealthinsurance']}")
        
        with col2:
            st.markdown("### Healthcare Access")
            st.markdown(f"**Primary Care Doctor:** {'Yes' if health['hasprimarycaredoctor'] else 'No'}")
            st.markdown(f"**Preventive Care Exams:** {'Yes' if health['preventivecareexams'] else 'No'}")
            st.markdown(f"**Cost Preventing Medical Care:** {'Yes' if health['iscostpreventingmedicalcare'] else 'No'}")
        
        st.markdown("### Mental Health")
        mental_health_issues = []
        
        if pd.notna(health['littleinterestorpleasurefrequency']) and health['littleinterestorpleasurefrequency'] != "Never":
            mental_health_issues.append(f"Little interest or pleasure: {health['littleinterestorpleasurefrequency']}")
        
        if pd.notna(health['depressionfrequency']) and health['depressionfrequency'] != "Never":
            mental_health_issues.append(f"Depression: {health['depressionfrequency']}")
        
        if pd.notna(health['anxiousfrequency']) and health['anxiousfrequency'] != "Never":
            mental_health_issues.append(f"Anxiety: {health['anxiousfrequency']}")
        
        if mental_health_issues:
            for issue in mental_health_issues:
                st.markdown(f"• {issue}")
        else:
            st.markdown("No mental health concerns reported")
        
        # Display all comments
        comments = []
        comment_fields = [
            'medicalcomments',
            'costpreventingmedicalcarecomments',
            'healthinsurancecomments',
            'primarycaredoctorcomments',
            'preventivecareexamscomments',
            'shareinfowithakhbcomments',
            'physicaldisabilitycomments',
            'littleinterestcomments',
            'depressioncomments',
            'anxiouscomments',
            'worrycomments',
            'familyrelationshipcomments',
            'substanceusecomments',
            'stressmanagementcomments'
        ]
        
        for field in comment_fields:
            if field in health.index and pd.notna(health[field]) and str(health[field]).strip():
                comments.append(str(health[field]).strip())
        
        if comments:
            st.markdown("### Comments")
            st.markdown("**Comments:** " + "\n\n".join(comments))
    else:
        st.info("No health data available for this family member.")