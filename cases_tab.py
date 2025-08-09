import streamlit as st
import pandas as pd
import plotly.express as px

def render_cases_tab(df, jamati_member_df):
    """Render the Cases tab with regional summary, filtering, and visualizations"""
    
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

    # Region filter
    regions = df['region'].unique()
    selected_region = st.selectbox("Select Region", options=["All"] + list(regions))

    # Filter the dataframe based on selections
    filtered_df = df.copy()
    if selected_region != "All":
        filtered_df = filtered_df[filtered_df['region'] == selected_region]

    # Calculate total number of cases and open cases
    total_cases = len(filtered_df)
    open_cases = filtered_df[filtered_df['status'].isin(['Open', 'Reopen'])]

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
        filtered_df = filtered_df[filtered_df['status'].isin(['Open', 'Reopen'])]
    
    st.subheader("Settlement Cases")
    st.dataframe(filtered_df)

    # Create two columns for pie chart and map
    pie_col, map_col = st.columns(2)

    with pie_col:
        # Display pie chart
        status_counts = filtered_df['status'].value_counts()
        fig = px.pie(status_counts, values=status_counts.values, names=status_counts.index, title='Case Status Distribution')
        st.plotly_chart(fig, use_container_width=True)

    with map_col:
        # Create US map visualization
        state_counts = filtered_df['state'].value_counts().reset_index()
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
    line_df = filtered_df.copy()
    line_df['creationdate'] = pd.to_datetime(line_df['creationdate'])
    
    # Filter cases created after 2022
    line_df = line_df[line_df['creationdate'].dt.year > 2022]

    # Create a month column for monthly aggregation
    line_df['month_year'] = line_df['creationdate'].dt.to_period('M')
    
    # Group by Month and Region, then count the number of cases
    df_grouped = line_df.groupby([line_df['month_year'].astype(str), 'region']).size().reset_index(name='case_count')

    # Create the line chart
    line_fig = px.line(df_grouped, x='month_year', y='case_count', color='region', 
                       title='New Cases Over Time by Region (Monthly)', 
                       labels={'month_year': 'Month', 'case_count': 'Number of Cases'})
    st.plotly_chart(line_fig)