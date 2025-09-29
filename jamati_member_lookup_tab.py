import streamlit as st
import pandas as pd
import plotly.express as px
import re

def render_jamati_member_lookup_tab(jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df):
    """Render the Jamati Member Lookup tab with member lookup and data display"""
    
    st.subheader("Jamati Member Lookup")
    st.markdown("Search and view detailed information for any jamati member in the system.")
    
    # Member detailed lookup
    render_member_detailed_lookup(jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df)
    
    st.markdown("---")
    
    # Display all jamati member data
    st.markdown("## 📊 All Jamati Member Data")
    st.markdown("Complete dataset of all jamati members in the system.")
    
    # Calculate age for display
    current_year = 2025
    display_df = jamati_member_df.copy()
    
    # Handle age calculation for all members
    year_col = 'yearofbirth' if 'yearofbirth' in display_df.columns else 'YearOfBirth'
    if year_col in display_df.columns:
        display_df['age'] = display_df[year_col].apply(
            lambda x: current_year - x if pd.notna(x) and x != 0 else None
        )
    
    # Handle column name variations for display
    member_column_mapping = {
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
    
    available_cols = []
    for display_name, possible_names in member_column_mapping.items():
        for col_name in possible_names:
            if col_name in display_df.columns:
                available_cols.append(col_name)
                break
    
    if available_cols:
        member_display_df = display_df[available_cols].copy()
        
        # Convert boolean columns to Yes/No for better readability
        bool_columns = member_display_df.select_dtypes(include=['bool']).columns
        for col in bool_columns:
            member_display_df[col] = member_display_df[col].replace({True: 'Yes', False: 'No'})
        
        # Add search functionality
        st.markdown("### 🔍 Search Members")
        search_term = st.text_input("Search by name, case ID, or person ID:", key="member_search")
        
        if search_term:
            # Create a mask for search
            search_mask = pd.Series([False] * len(member_display_df))
            
            for col in member_display_df.columns:
                if member_display_df[col].dtype == 'object':
                    search_mask |= member_display_df[col].astype(str).str.contains(search_term, case=False, na=False)
                elif pd.api.types.is_numeric_dtype(member_display_df[col]):
                    search_mask |= member_display_df[col].astype(str).str.contains(search_term, na=False)
            
            filtered_df = member_display_df[search_mask]
            st.markdown(f"**Found {len(filtered_df)} members matching '{search_term}'**")
            st.dataframe(filtered_df, hide_index=True, use_container_width=True)
        else:
            st.dataframe(member_display_df, hide_index=True, use_container_width=True)
    else:
        st.error("No compatible columns found in jamati member data.")

def render_member_detailed_lookup(jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df):
    """Render the detailed member lookup section"""
    
    st.markdown("### 🔍 Member Detailed Lookup")
    st.markdown("Select a jamati member to view their complete information.")
    
    if jamati_member_df.empty:
        st.info("No jamati members found in the system.")
        return
    
    # Get column names with fallbacks
    person_id_col = 'personid' if 'personid' in jamati_member_df.columns else 'PersonID'
    case_id_col = 'caseid' if 'caseid' in jamati_member_df.columns else 'CaseID'
    firstname_col = 'firstname' if 'firstname' in jamati_member_df.columns else 'FirstName'
    lastname_col = 'lastname' if 'lastname' in jamati_member_df.columns else 'LastName'
    year_col = 'yearofbirth' if 'yearofbirth' in jamati_member_df.columns else 'YearOfBirth'
    
    # Calculate age for all members
    current_year = 2025
    display_df = jamati_member_df.copy()
    if year_col in display_df.columns:
        display_df['age'] = display_df[year_col].apply(
            lambda x: current_year - x if pd.notna(x) and x != 0 else "Unknown"
        )
    else:
        display_df['age'] = "Unknown"
    
    # Create options for the selectbox
    member_options = []
    for idx, member in display_df.iterrows():
        member_name = f"{member[firstname_col]} {member[lastname_col]}"
        member_id = member[person_id_col]
        case_id = member[case_id_col]
        age = member['age']
        member_options.append(f"{member_name} (Age: {age}, Person ID: {member_id}, Case ID: {case_id})")
    
    selected_member_option = st.selectbox(
        "Select a jamati member to view detailed information:",
        options=["Select a member..."] + member_options,
        key="member_selector"
    )
    
    if selected_member_option != "Select a member...":
        # Extract person ID from the selected option
        person_id_match = re.search(r'Person ID: (\d+)', selected_member_option)
        if person_id_match:
            selected_person_id = int(person_id_match.group(1))
            selected_member = display_df[display_df[person_id_col] == selected_person_id].iloc[0]
            
            # Display detailed member information
            st.markdown("---")
            st.markdown(f"## 👤 Detailed Information for {selected_member[firstname_col]} {selected_member[lastname_col]}")
            
            # Create tabs for different data categories
            member_tabs = st.tabs(["Personal Info", "Education", "Social Inclusion", "Finance", "Health", "Jamati Activity Eligibility"])
            
            with member_tabs[0]:  # Personal Info
                render_personal_info_tab(selected_member, person_id_col, firstname_col, lastname_col)
            
            with member_tabs[1]:  # Education
                render_education_tab(education_df, person_id_col, selected_person_id)
            
            with member_tabs[2]:  # Social Inclusion
                render_social_inclusion_tab(social_inclusion_agency_df, person_id_col, selected_person_id)
            
            with member_tabs[3]:  # Finance
                render_finance_tab(finance_df, person_id_col, selected_person_id)
            
            with member_tabs[4]:  # Health
                render_health_tab(physical_mental_health_df, person_id_col, selected_person_id)
            
            with member_tabs[5]:  # Jamati Activity Eligibility
                render_jamati_activity_eligibility_tab(selected_member, firstname_col)

def render_personal_info_tab(selected_member, person_id_col, firstname_col, lastname_col):
    """Render the personal info tab for a member"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Basic Information")
        st.markdown(f"**Full Name:** {selected_member[firstname_col]} {selected_member[lastname_col]}")
        st.markdown(f"**Person ID:** {selected_member[person_id_col]}")
        
        case_id_col = 'caseid' if 'caseid' in selected_member.index else 'CaseID'
        st.markdown(f"**Case ID:** {selected_member[case_id_col]}")
        
        if 'age' in selected_member.index and selected_member['age'] != "Unknown":
            st.markdown(f"**Age:** {selected_member['age']}")
        
        year_col = 'yearofbirth' if 'yearofbirth' in selected_member.index else 'YearOfBirth'
        if year_col in selected_member.index and pd.notna(selected_member[year_col]) and selected_member[year_col] != 0:
            st.markdown(f"**Year of Birth:** {int(selected_member[year_col])}")
        
        relation_col = 'relationtohead' if 'relationtohead' in selected_member.index else 'RelationToHead'
        if relation_col in selected_member.index and pd.notna(selected_member[relation_col]):
            st.markdown(f"**Relation to Head:** {selected_member[relation_col]}")
    
    with col2:
        st.markdown("### Background Information")
        
        country_col = 'countryoforigin' if 'countryoforigin' in selected_member.index else 'CountryOfOrigin'
        if country_col in selected_member.index and pd.notna(selected_member[country_col]):
            st.markdown(f"**Country of Origin:** {selected_member[country_col]}")
        
        legal_col = 'legalstatus' if 'legalstatus' in selected_member.index else 'LegalStatus'
        if legal_col in selected_member.index and pd.notna(selected_member[legal_col]):
            st.markdown(f"**Legal Status:** {selected_member[legal_col]}")
        
        arrival_col = 'usarrivalyear' if 'usarrivalyear' in selected_member.index else 'USArrivalYear'
        if arrival_col in selected_member.index and pd.notna(selected_member[arrival_col]) and selected_member[arrival_col] != 0:
            st.markdown(f"**USA Arrival Year:** {int(selected_member[arrival_col])}")
        
        born_usa_col = 'borninusa' if 'borninusa' in selected_member.index else 'BornInUSA'
        if born_usa_col in selected_member.index and pd.notna(selected_member[born_usa_col]):
            st.markdown(f"**Born in USA:** {'Yes' if selected_member[born_usa_col] else 'No'}")
        
        education_col = 'educationlevel' if 'educationlevel' in selected_member.index else 'EducationLevel'
        if education_col in selected_member.index and pd.notna(selected_member[education_col]):
            st.markdown(f"**Education Level:** {selected_member[education_col]}")
        
        fluency_col = 'englishfluency' if 'englishfluency' in selected_member.index else 'EnglishFluency'
        if fluency_col in selected_member.index and pd.notna(selected_member[fluency_col]):
            st.markdown(f"**English Fluency:** {selected_member[fluency_col]}")

def render_education_tab(education_df, person_id_col, selected_person_id):
    """Render the education tab for a member"""
    member_education = education_df[education_df[person_id_col] == selected_person_id]
    
    if not member_education.empty:
        edu = member_education.iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### School Information")
            
            attending_school_col = 'isattendingschool' if 'isattendingschool' in edu.index else 'IsAttendingSchool'
            if attending_school_col in edu.index:
                st.markdown(f"**Attending School:** {'Yes' if edu[attending_school_col] else 'No'}")
                
                if edu[attending_school_col]:
                    school_name_col = 'schoolname' if 'schoolname' in edu.index else 'SchoolName'
                    if school_name_col in edu.index and pd.notna(edu[school_name_col]):
                        st.markdown(f"**School Name:** {edu[school_name_col]}")
                    
                    grade_col = 'schoolgrade' if 'schoolgrade' in edu.index else 'SchoolGrade'
                    if grade_col in edu.index and pd.notna(edu[grade_col]):
                        st.markdown(f"**Grade:** {edu[grade_col]}")
            
            # ECDC and REC attendance
            ecdc_col = 'isattendingecdc' if 'isattendingecdc' in edu.index else 'IsAttendingECDC'
            if ecdc_col in edu.index:
                st.markdown(f"**Attending ECDC:** {'Yes' if edu[ecdc_col] else 'No'}")
            
            rec_col = 'isattendingrec' if 'isattendingrec' in edu.index else 'IsAttendingREC'
            if rec_col in edu.index:
                st.markdown(f"**Attending REC:** {'Yes' if edu[rec_col] else 'No'}")
        
        with col2:
            st.markdown("### Academic Performance")
            
            perf_col = 'academicperformance' if 'academicperformance' in edu.index else 'AcademicPerformance'
            if perf_col in edu.index and pd.notna(edu[perf_col]):
                st.markdown(f"**Academic Performance:** {edu[perf_col]}")
            
            issues_col = 'hasacademicissues' if 'hasacademicissues' in edu.index else 'HasAcademicIssues'
            if issues_col in edu.index:
                st.markdown(f"**Has Academic Issues:** {'Yes' if edu[issues_col] else 'No'}")
            
            extra_col = 'hasextracurriculars' if 'hasextracurriculars' in edu.index else 'HasExtraCurriculars'
            if extra_col in edu.index:
                st.markdown(f"**Has Extra Curriculars:** {'Yes' if edu[extra_col] else 'No'}")
            
            bullied_col = 'isbullied' if 'isbullied' in edu.index else 'IsBullied'
            if bullied_col in edu.index:
                st.markdown(f"**Is Bullied:** {'Yes' if edu[bullied_col] else 'No'}")
            
            behavior_col = 'hasbehaviorchallenges' if 'hasbehaviorchallenges' in edu.index else 'HasBehaviorChallenges'
            if behavior_col in edu.index:
                st.markdown(f"**Has Behavior Challenges:** {'Yes' if edu[behavior_col] else 'No'}")
            
            disability_col = 'hasdisability' if 'hasdisability' in edu.index else 'HasDisability'
            if disability_col in edu.index:
                st.markdown(f"**Has Disability:** {'Yes' if edu[disability_col] else 'No'}")
    else:
        st.info("No education data available for this member.")

def render_social_inclusion_tab(social_inclusion_agency_df, person_id_col, selected_person_id):
    """Render the social inclusion tab for a member"""
    member_social = social_inclusion_agency_df[social_inclusion_agency_df[person_id_col] == selected_person_id]
    
    if not member_social.empty:
        social = member_social.iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Social Connection Status")
            
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
            
            friend_family_cols = ['hasfriendsfamilyconnection', 'HasFriendFamilyConnection']
            for col in friend_family_cols:
                if col in social.index:
                    st.markdown(f"**Has Friend/Family Connection:** {'Yes' if social[col] else 'No'}")
                    break
        
        with col2:
            st.markdown("### Jamat Khana Participation")
            
            attend_jk_cols = ['attendjk', 'AttendJK']
            for col in attend_jk_cols:
                if col in social.index:
                    st.markdown(f"**Attends JK:** {'Yes' if social[col] else 'No'}")
                    break
            
            jk_frequency_cols = ['attendjkhowoften', 'AttendJkHowOften']
            for col in jk_frequency_cols:
                if col in social.index and pd.notna(social[col]):
                    st.markdown(f"**JK Attendance Frequency:** {social[col]}")
                    break
    else:
        st.info("No social inclusion data available for this member.")

def render_finance_tab(finance_df, person_id_col, selected_person_id):
    """Render the finance tab for a member"""
    member_finance = finance_df[finance_df[person_id_col] == selected_person_id]
    
    if not member_finance.empty:
        finance = member_finance.iloc[0]
        
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
                    break
            
            debt_cols = ['havedebt', 'HaveDebt']
            for col in debt_cols:
                if col in finance.index:
                    st.markdown(f"**Has Debt:** {'Yes' if finance[col] else 'No'}")
                    break
        
        with col2:
            st.markdown("### Financial Support")
            
            tax_cols = ['taxfiling', 'TaxFiling']
            for col in tax_cols:
                if col in finance.index:
                    st.markdown(f"**Tax Filing:** {'Yes' if finance[col] else 'No'}")
                    break
            
            money_home_cols = ['sendmoneybackhome', 'SendMoneyBackHome']
            for col in money_home_cols:
                if col in finance.index:
                    st.markdown(f"**Sends Money Back Home:** {'Yes' if finance[col] else 'No'}")
                    break
            
            financial_support_cols = ['financialsupport', 'FinancialSupport']
            for col in financial_support_cols:
                if col in finance.index:
                    st.markdown(f"**Receives Financial Support:** {'Yes' if finance[col] else 'No'}")
                    break
    else:
        st.info("No financial data available for this member.")

def render_health_tab(physical_mental_health_df, person_id_col, selected_person_id):
    """Render the health tab for a member"""
    member_health = physical_mental_health_df[physical_mental_health_df[person_id_col] == selected_person_id]
    
    if not member_health.empty:
        health = member_health.iloc[0]
        
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
                    break
        
        with col2:
            st.markdown("### Mental Health")
            
            mental_health_cols = ['hasmentalhealthconditions', 'HasMentalHealthConditions']
            for col in mental_health_cols:
                if col in health.index:
                    st.markdown(f"**Has Mental Health Conditions:** {'Yes' if health[col] else 'No'}")
                    break
            
            counseling_cols = ['iscurrentlyincounseling', 'IsCurrentlyInCounseling']
            for col in counseling_cols:
                if col in health.index:
                    st.markdown(f"**Currently in Counseling:** {'Yes' if health[col] else 'No'}")
                    break
    else:
        st.info("No health data available for this member.")

def render_jamati_activity_eligibility_tab(selected_member, firstname_col):
    """Render the Jamati Activity Eligibility tab for a member"""
    st.markdown("### 🎯 Jamati Activity Eligibility")
    
    
    # Determine age (use precomputed 'age' if available, else compute from year of birth)
    age_value = None
    if 'age' in selected_member.index and pd.notna(selected_member['age']) and isinstance(selected_member['age'], (int, float)):
        age_value = int(selected_member['age'])
    else:
        year_col = 'yearofbirth' if 'yearofbirth' in selected_member.index else 'YearOfBirth'
        if year_col in selected_member.index and pd.notna(selected_member[year_col]) and selected_member[year_col] not in (0, ""):
            current_year = 2025
            try:
                age_value = int(current_year - int(selected_member[year_col]))
            except Exception:
                age_value = None

    # Compute Camp Mosaic eligibility based on age
    st.markdown("## 🏕️ Camp Mosaic Eligibility Check")
    st.markdown("#### Ages 6-13: Eligible for Camp Mosaic Participant")
    st.markdown(f"#### **🎂 {selected_member[firstname_col]}'s Age:** {age_value if age_value is not None else '❓ Unknown'}")
    if age_value is None:
        eligibility_text = "❓ Unknown (insufficient age information)"
        st.warning(f"**🎯 Status:** {eligibility_text}")
    elif age_value < 6:
        eligibility_text = "⛔ Not eligible for Camp Mosaic (under 6 years old)"
        st.error(f"**🎯 Status:** {eligibility_text}")
    elif 6 <= age_value <= 13:
        eligibility_text = "✨ Eligible – Camp Mosaic Participant!"
        st.success(f"**🎯 Status:** {eligibility_text}")
    else:
        eligibility_text = "👑 Eligible – Camp Mosaic Counselor!"
        st.info(f"**🎯 Status:** {eligibility_text}")

    # Display results with fun emojis
    
    