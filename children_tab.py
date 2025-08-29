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
            with st.expander("📈 Children Age Distribution", expanded=True):
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
            with st.expander("🌍 Children Country of Origin Distribution", expanded=True):
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
                    with st.expander("🏆 Academic Performance Distribution", expanded=True):
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
        

        
    else:
        st.info("No children (18 and under) found in the current dataset.")

