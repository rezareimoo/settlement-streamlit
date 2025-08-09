import streamlit as st
import pandas as pd
import plotly.express as px
import re

def get_col_name(preferred, alternative):
    """Get the appropriate column name with fallback options"""
    return preferred if preferred else alternative

def render_children_tab(df, jamati_member_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df):
    """Render the Children's Data tab with comprehensive children analysis"""
    
    st.subheader("Children's Data (18 and Under)")
    
    # Filter children based on birth year
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
        
        regions = df['region'].unique()
        active_cases = df[df['status'].isin(['Open', 'Reopen'])]['caseid'].unique()
        children_active_cases = children_df[children_df['caseid'].isin(active_cases)]
        
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
        summary_df['Total Children'] = summary_df['Total Children'].map('{:,}'.format)
        summary_df['Children in Active Cases'] = summary_df['Children in Active Cases'].map('{:,}'.format)
        summary_df = summary_df.set_index('Region')
        
        st.dataframe(summary_df.style.set_properties(**{'font-size': '16px'}))
        st.markdown("---")
        
        # Charts
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
        
        person_id_col = 'personid' if 'personid' in education_df.columns else 'PersonID'
        children_education = education_df[education_df[person_id_col].isin(children_df[person_id_col])]
        
        if not children_education.empty:
            children_edu_merged = children_df.merge(children_education, on=person_id_col, how='inner')
            
            # Create education summary
            education_summary = {}
            for col_pair in [
                ('isattendingschool', 'IsAttendingSchool', 'Attending School'),
                ('isattendingecdc', 'IsAttendingECDC', 'Attending ECDC'),
                ('isattendingrec', 'IsAttendingREC', 'Attending REC'),
                ('hasacademicissues', 'HasAcademicIssues', 'Has Academic Issues'),
                ('hasextracurriculars', 'HasExtraCurriculars', 'Has Extra Curriculars'),
                ('isbullied', 'IsBullied', 'Is Bullied'),
                ('hasbehaviorchallenges', 'HasBehaviorChallenges', 'Has Behavior Challenges'),
                ('hasdisability', 'HasDisability', 'Has Disability'),
                ('hasspecializedlearningplans', 'HasSpecializedLearningPlans', 'Has Specialized Learning Plans')
            ]:
                col_name = col_pair[0] if col_pair[0] in children_edu_merged.columns else col_pair[1]
                if col_name in children_edu_merged.columns:
                    education_summary[col_pair[2]] = children_edu_merged[col_name].sum()
            
            if education_summary:
                edu_summary_df = pd.DataFrame(list(education_summary.items()), columns=['Category', 'Count'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Education Statistics")
                    st.dataframe(edu_summary_df, hide_index=True)
                
                with col2:
                    # Academic performance distribution
                    perf_col = 'academicperformance' if 'academicperformance' in children_edu_merged.columns else 'AcademicPerformance'
                    if perf_col in children_edu_merged.columns:
                        perf_counts = children_edu_merged[perf_col].dropna().value_counts()
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
        else:
            st.info("No education data available for children in the system.")
        
        # Children data table
        st.markdown("### All Children Data")
        
        # Handle column name variations
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
            children_display_df = children_df[available_child_cols].copy()
            bool_columns = children_display_df.select_dtypes(include=['bool']).columns
            for col in bool_columns:
                children_display_df[col] = children_display_df[col].replace({True: 'Yes', False: 'No'})
            
            st.dataframe(children_display_df, hide_index=True, use_container_width=True)
        
        # Child detailed lookup
        render_child_detailed_lookup(children_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df)
        
    else:
        st.info("No children (18 and under) found in the current dataset.")

def render_child_detailed_lookup(children_df, education_df, finance_df, physical_mental_health_df, social_inclusion_agency_df):
    """Render the detailed child lookup section"""
    
    st.markdown("### 🔍 Child Detailed Lookup")
    st.markdown("Select a child to view their complete information.")
    
    # Get column names
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
        person_id_match = re.search(r'Person ID: (\d+)', selected_child_option)
        if person_id_match:
            selected_person_id = int(person_id_match.group(1))
            selected_child = children_df[children_df[person_id_col] == selected_person_id].iloc[0]
            
            # Display detailed child information
            st.markdown("---")
            st.markdown(f"## 👶 Detailed Information for {selected_child[firstname_col]} {selected_child[lastname_col]}")
            
            # Create tabs for different data categories
            child_tabs = st.tabs(["Personal Info", "Education", "Social Inclusion", "Finance", "Health", "Camp Eligibility"])
            
            with child_tabs[0]:  # Personal Info
                render_personal_info_tab(selected_child, person_id_col, firstname_col, lastname_col)
            
            with child_tabs[1]:  # Education
                render_education_tab(education_df, person_id_col, selected_person_id)
            
            with child_tabs[2]:  # Social Inclusion
                render_social_inclusion_tab(social_inclusion_agency_df, person_id_col, selected_person_id)
            
            with child_tabs[3]:  # Finance
                render_finance_tab(finance_df, person_id_col, selected_person_id)
            
            with child_tabs[4]:  # Health
                render_health_tab(physical_mental_health_df, person_id_col, selected_person_id)
            
            with child_tabs[5]:  # Camp Eligibility
                render_camp_eligibility_tab(selected_child, firstname_col)

def render_personal_info_tab(selected_child, person_id_col, firstname_col, lastname_col):
    """Render the personal info tab for a child"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Basic Information")
        st.markdown(f"**Full Name:** {selected_child[firstname_col]} {selected_child[lastname_col]}")
        st.markdown(f"**Person ID:** {selected_child[person_id_col]}")
        case_id_col = 'caseid' if 'caseid' in selected_child.index else 'CaseID'
        st.markdown(f"**Case ID:** {selected_child[case_id_col]}")
        st.markdown(f"**Age:** {selected_child['age']}")
        
        year_col = 'yearofbirth' if 'yearofbirth' in selected_child.index else 'YearOfBirth'
        if year_col in selected_child.index and pd.notna(selected_child[year_col]):
            st.markdown(f"**Year of Birth:** {int(selected_child[year_col])}")
        
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
        if arrival_col in selected_child.index and pd.notna(selected_child[arrival_col]):
            st.markdown(f"**USA Arrival Year:** {int(selected_child[arrival_col])}")

def render_education_tab(education_df, person_id_col, selected_person_id):
    """Render the education tab for a child"""
    child_education = education_df[education_df[person_id_col] == selected_person_id]
    
    if not child_education.empty:
        edu = child_education.iloc[0]
        
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
    else:
        st.info("No education data available for this child.")

def render_social_inclusion_tab(social_inclusion_agency_df, person_id_col, selected_person_id):
    """Render the social inclusion tab for a child"""
    child_social = social_inclusion_agency_df[social_inclusion_agency_df[person_id_col] == selected_person_id]
    
    if not child_social.empty:
        social = child_social.iloc[0]
        
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
        
        with col2:
            st.markdown("### Jamat Khana Participation")
            
            attend_jk_cols = ['attendjk', 'AttendJK']
            for col in attend_jk_cols:
                if col in social.index:
                    st.markdown(f"**Attends JK:** {'Yes' if social[col] else 'No'}")
                    break
    else:
        st.info("No social inclusion data available for this child.")

def render_finance_tab(finance_df, person_id_col, selected_person_id):
    """Render the finance tab for a child"""
    child_finance = finance_df[finance_df[person_id_col] == selected_person_id]
    
    if not child_finance.empty:
        finance = child_finance.iloc[0]
        
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
    else:
        st.info("No financial data available for this child.")

def render_health_tab(physical_mental_health_df, person_id_col, selected_person_id):
    """Render the health tab for a child"""
    child_health = physical_mental_health_df[physical_mental_health_df[person_id_col] == selected_person_id]
    
    if not child_health.empty:
        health = child_health.iloc[0]
        
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
    else:
        st.info("No health data available for this child.")

def render_camp_eligibility_tab(selected_child, firstname_col):
    """Render the camp eligibility tab for a child"""
    st.markdown("### 🏕️ Camp Mosaic Eligibility")
    
    child_age = selected_child['age']
    
    st.markdown("#### Camp Mosaic")
    st.markdown("**Age Range:** 6-13 years old")
    
    if 6 <= child_age <= 13:
        st.success(f"✅ **ELIGIBLE** - {selected_child[firstname_col]} is {child_age} years old")
        st.markdown("🎯 **Next Steps:** Contact camp coordinator to register")
        
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
    else:
        st.error(f"❌ **NOT ELIGIBLE** - {selected_child[firstname_col]} is {child_age} years old")
        
        if child_age < 6:
            st.info(f"📅 **Future Eligibility:** Will be eligible for Camp Mosaic in {6 - child_age} year(s) when they turn 6")
        elif child_age > 13:
            st.info("🔄 **Too old for Camp Mosaic** - May be eligible to be a guide or counselor for the camp")