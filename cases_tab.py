import streamlit as st
import pandas as pd
import plotly.express as px

def render_cases_tab(df, jamati_member_df, data_source="CMS Data", fdp_df=None, user_regions=None):
    """Render the Cases tab with regional summary, filtering, and visualizations"""
    
    if data_source != "Compare Both":
        # Single view mode
        render_single_view(df, jamati_member_df, data_source, user_regions=user_regions)
    else:
        # Comparison mode
        render_comparison_view(df, jamati_member_df, fdp_df, user_regions=user_regions)

def render_single_view(df, jamati_member_df, data_source, user_regions=None):
    """Render single data source view"""
    data_label = "CMS" if data_source == "CMS Data" else "FDP"
    
    # Date Filter Section (integrated with data source selection)
    st.markdown("Select a date range to filter all data:")
    
    # Convert creationdate to datetime if it's not already
    df['creationdate'] = pd.to_datetime(df['creationdate'], errors='coerce')
    
    # Get min and max dates from the data
    min_date = df['creationdate'].min()
    max_date = df['creationdate'].max()
    
    # Create date picker columns
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=min_date.date() if pd.notna(min_date) else None,
            min_value=min_date.date() if pd.notna(min_date) else None,
            max_value=max_date.date() if pd.notna(max_date) else None,
            key=f"start_date_{data_source}"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=max_date.date() if pd.notna(max_date) else None,
            min_value=min_date.date() if pd.notna(min_date) else None,
            max_value=max_date.date() if pd.notna(max_date) else None,
            key=f"end_date_{data_source}"
        )
    
    # Apply date filter to the dataframe
    date_range_text = ""
    if start_date and end_date:
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)
        df = df[(df['creationdate'] >= start_datetime) & (df['creationdate'] <= end_datetime)]
        date_range_text = f"{start_date} to {end_date}"
        st.info(f"Showing data from {start_date} to {end_date}")
    elif start_date:
        start_datetime = pd.to_datetime(start_date)
        df = df[df['creationdate'] >= start_datetime]
        date_range_text = f"from {start_date}"
        st.info(f"Showing data from {start_date} onwards")
    elif end_date:
        end_datetime = pd.to_datetime(end_date)
        df = df[df['creationdate'] <= end_datetime]
        date_range_text = f"up to {end_date}"
        st.info(f"Showing data up to {end_date}")
    else:
        date_range_text = "all available data"
    
    # Region filter - only show user's allowed regions
    regions = df['region'].unique()
    if user_regions and len(user_regions) > 0:
        # Filter to only show regions that user has access to
        available_regions = [r for r in regions if r in user_regions]
        if len(available_regions) == 1:
            # If only one region, default to it (but still show selector)
            default_region = available_regions[0]
            region_options = [default_region]
        else:
            region_options = ["All"] + sorted(available_regions)
    else:
        region_options = ["All"] + sorted(list(regions))
    
    selected_region = st.selectbox("Select Region", options=region_options, key=f"region_filter_{data_source}")
    
    st.markdown("---")
    
    # Current Date Range heading
    st.markdown(f"### 📅 Current Date Range: {date_range_text}")
    st.markdown("---")
    
    # --- Summary Table at the Top ---
    st.markdown(f"## 🗺️ Regional Summary ({data_label} Data)")
    
    # 1. Aggregate number of cases per region
    case_counts = df.groupby('region')['caseid'].nunique().reset_index(name='Number of Cases')

    # 2. For each region, count the number of individuals
    if data_source == "CMS Data":
        def count_individuals(region):
            case_ids = df[df['region'] == region]['caseid'].unique()
            return jamati_member_df[jamati_member_df['caseid'].isin(case_ids)].shape[0]
        case_counts['Number of Individuals'] = case_counts['region'].apply(count_individuals)
    else:
        # For FDP data, use aggregated family size data if available
        def count_fdp_individuals(region):
            region_cases = df[df['region'] == region]
            if 'number_in_family' in region_cases.columns:
                return region_cases['number_in_family'].fillna(0).sum()
            return 0
        case_counts['Number of Individuals'] = case_counts['region'].apply(count_fdp_individuals)

    # 3. Calculate number of open cases per region
    open_cases_df = df[df['status'].isin(['Open', 'Reopen'])]
    open_case_counts = open_cases_df.groupby('region')['caseid'].nunique().reset_index(name='Open Cases')

    # 4. Calculate number of closed cases per region
    closed_cases_df = df[df['status'].isin(['Closed'])]
    closed_case_counts = closed_cases_df.groupby('region')['caseid'].nunique().reset_index(name='Closed Cases')

    # 5. Merge open and closed case counts into the summary table
    case_counts = case_counts.merge(open_case_counts, on='region', how='left').fillna(0)
    case_counts = case_counts.merge(closed_case_counts, on='region', how='left').fillna(0)

    # 6. Format numbers with commas
    case_counts['Number of Cases'] = case_counts['Number of Cases'].map('{:,}'.format)
    case_counts['Number of Individuals'] = case_counts['Number of Individuals'].map('{:,}'.format)
    case_counts['Open Cases'] = case_counts['Open Cases'].astype(int).map('{:,}'.format)
    case_counts['Closed Cases'] = case_counts['Closed Cases'].astype(int).map('{:,}'.format)

    # 6. Set region as index for a cleaner look
    case_counts = case_counts.set_index('region')

    # 7. Display with description
    st.markdown(
        f"This table summarizes the number of settlement cases, open cases, closed cases, and the aggregate number of individuals per region using {data_label} data."
    )
    st.dataframe(
        case_counts.style.set_properties(**{'font-size': '16px'})
    )
    st.markdown("---")
    
    # Filter the dataframe based on region selection
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

    # Create two columns for pie chart and map
    pie_col, map_col = st.columns(2)

    with pie_col:
        with st.expander("📊 Case Status Distribution (Pie Chart)", expanded=False):
            # Display pie chart
            status_counts = filtered_df['status'].value_counts()
            fig = px.pie(status_counts, values=status_counts.values, names=status_counts.index, 
                         title=f'Case Status Distribution ({data_label}) - {date_range_text}')
            st.plotly_chart(fig, use_container_width=True)

    with map_col:
        with st.expander("🗺️ Cases by State (US Map)", expanded=False):
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
                title=f'Number of Cases by State ({data_label}) - {date_range_text}',
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

    # Create stacked bar chart showing case statuses by region
    with st.expander("📊 Case Status by Region (Stacked Bar Chart)", expanded=False):
        # Prepare data for stacked bar chart
        status_region_df = filtered_df.groupby(['region', 'status']).size().reset_index(name='count')
        
        if not status_region_df.empty:
            # Create stacked bar chart
            stacked_fig = px.bar(
                status_region_df, 
                x='region', 
                y='count', 
                color='status',
                title=f'Case Status Distribution by Region ({data_label}) - {date_range_text}',
                labels={'count': 'Number of Cases', 'region': 'Region'},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            # Update layout for better readability
            stacked_fig.update_layout(
                xaxis_tickangle=-45,
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                )
            )
            
            st.plotly_chart(stacked_fig, use_container_width=True)
        else:
            st.warning(f"No data available for status distribution by region ({data_label})")

    # Create a line chart based on the CreationDate, grouped by Region
    with st.expander("📈 New Cases Over Time by Region (Line Chart)", expanded=False):
        line_df = filtered_df.copy()
        line_df['creationdate'] = pd.to_datetime(line_df['creationdate'])

        if not line_df.empty:
            # Create a month column for monthly aggregation
            line_df['month_year'] = line_df['creationdate'].dt.to_period('M')
            
            # Group by Month and Region, then count the number of cases
            df_grouped = line_df.groupby([line_df['month_year'].astype(str), 'region']).size().reset_index(name='case_count')
            
            # Calculate total cases per month (sum across all regions)
            df_total = line_df.groupby([line_df['month_year'].astype(str)]).size().reset_index(name='case_count')
            df_total['region'] = 'Total'
            
            # Combine regional data with total data
            df_combined = pd.concat([df_grouped, df_total], ignore_index=True)

            # Create the line chart
            line_fig = px.line(df_combined, x='month_year', y='case_count', color='region', 
                               title=f'New Cases Over Time by Region - Monthly ({data_label}) - {date_range_text}', 
                               labels={'month_year': 'Month', 'case_count': 'Number of Cases'})
            
            # Update layout to double the height
            line_fig.update_layout(height=600)
            
            st.plotly_chart(line_fig)
        else:
            st.warning(f"No valid {data_label} data available for timeline visualization")

def render_comparison_view(cms_df, jamati_member_df, fdp_df, user_regions=None):
    """Render comparison view between CMS and FDP data"""
    
    # Date Filter Section (integrated with data source selection)
    st.markdown("Select a date range to filter all data:")
    
    # Convert creationdate to datetime for both datasets
    cms_df['creationdate'] = pd.to_datetime(cms_df['creationdate'], errors='coerce')
    if fdp_df is not None:
        fdp_df['creationdate'] = pd.to_datetime(fdp_df['creationdate'], errors='coerce')
    
    # Get min and max dates from both datasets
    cms_min_date = cms_df['creationdate'].min()
    cms_max_date = cms_df['creationdate'].max()
    
    fdp_min_date = fdp_df['creationdate'].min() if fdp_df is not None else None
    fdp_max_date = fdp_df['creationdate'].max() if fdp_df is not None else None
    
    # Find overall min and max dates
    all_dates = [d for d in [cms_min_date, cms_max_date, fdp_min_date, fdp_max_date] if pd.notna(d)]
    min_date = min(all_dates) if all_dates else None
    max_date = max(all_dates) if all_dates else None
    
    # Create date picker columns
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=min_date.date() if pd.notna(min_date) else None,
            min_value=min_date.date() if pd.notna(min_date) else None,
            max_value=max_date.date() if pd.notna(max_date) else None,
            key="start_date_comparison"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=max_date.date() if pd.notna(max_date) else None,
            min_value=min_date.date() if pd.notna(min_date) else None,
            max_value=max_date.date() if pd.notna(max_date) else None,
            key="end_date_comparison"
        )
    
    # Apply date filter to both dataframes
    date_range_text = ""
    if start_date and end_date:
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)
        cms_df = cms_df[(cms_df['creationdate'] >= start_datetime) & (cms_df['creationdate'] <= end_datetime)]
        if fdp_df is not None:
            fdp_df = fdp_df[(fdp_df['creationdate'] >= start_datetime) & (fdp_df['creationdate'] <= end_datetime)]
        date_range_text = f"{start_date} to {end_date}"
        st.info(f"Showing data from {start_date} to {end_date}")
    elif start_date:
        start_datetime = pd.to_datetime(start_date)
        cms_df = cms_df[cms_df['creationdate'] >= start_datetime]
        if fdp_df is not None:
            fdp_df = fdp_df[fdp_df['creationdate'] >= start_datetime]
        date_range_text = f"from {start_date}"
        st.info(f"Showing data from {start_date} onwards")
    elif end_date:
        end_datetime = pd.to_datetime(end_date)
        cms_df = cms_df[cms_df['creationdate'] <= end_datetime]
        if fdp_df is not None:
            fdp_df = fdp_df[fdp_df['creationdate'] <= end_datetime]
        date_range_text = f"up to {end_date}"
        st.info(f"Showing data up to {end_date}")
    else:
        date_range_text = "all available data"
    
    # Region filter for comparison view
    # Get unique regions from both datasets
    cms_regions = cms_df['region'].unique()
    fdp_regions = fdp_df['region'].unique() if fdp_df is not None else []
    all_regions = list(set(list(cms_regions) + list(fdp_regions)))
    
    # Filter to only show user's allowed regions
    if user_regions and len(user_regions) > 0:
        available_regions = [r for r in all_regions if r in user_regions]
        if len(available_regions) == 1:
            # If only one region, default to it (but still show selector)
            default_region = available_regions[0]
            region_options = [default_region]
        else:
            region_options = ["All"] + sorted(available_regions)
    else:
        region_options = ["All"] + sorted(all_regions)
    
    selected_region = st.selectbox("Select Region", options=region_options, key="region_filter_comparison")
    
    # Apply region filter to both dataframes
    if selected_region != "All":
        cms_df = cms_df[cms_df['region'] == selected_region]
        if fdp_df is not None:
            fdp_df = fdp_df[fdp_df['region'] == selected_region]
    
    st.markdown("---")
    
    # Current Date Range heading
    st.markdown(f"### 📅 Current Date Range: {date_range_text}")
    st.markdown("---")
    
    st.markdown("## 🔄 Data Source Comparison")
    st.markdown("Side-by-side comparison of CMS and FDP data sources")
    
    # Data quality metrics at the top
    st.markdown("### 📈 Data Quality Overview")
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        cms_total = len(cms_df)
        fdp_total = len(fdp_df) if fdp_df is not None else 0
        st.metric("Total Cases", f"CMS: {cms_total:,} | FDP: {fdp_total:,}")
    
    with metric_col2:
        cms_regions = len(cms_df['region'].unique())
        fdp_regions = len(fdp_df['region'].unique()) if fdp_df is not None else 0
        st.metric("Regions Covered", f"CMS: {cms_regions} | FDP: {fdp_regions}")
    
    with metric_col3:
        cms_date_range = "N/A"
        fdp_date_range = "N/A"
        if not cms_df['creationdate'].isna().all():
            cms_min = cms_df['creationdate'].min().strftime('%Y-%m') if pd.notna(cms_df['creationdate'].min()) else "N/A"
            cms_max = cms_df['creationdate'].max().strftime('%Y-%m') if pd.notna(cms_df['creationdate'].max()) else "N/A"
            cms_date_range = f"{cms_min} to {cms_max}"
        
        if fdp_df is not None and not fdp_df['creationdate'].isna().all():
            try:
                fdp_min = fdp_df['creationdate'].min().strftime('%Y-%m') if pd.notna(fdp_df['creationdate'].min()) else "N/A"
                fdp_max = fdp_df['creationdate'].max().strftime('%Y-%m') if pd.notna(fdp_df['creationdate'].max()) else "N/A"
                fdp_date_range = f"{fdp_min} to {fdp_max}"
            except:
                fdp_date_range = "Invalid dates"
        
        st.write("**Date Ranges:**")
        st.write(f"CMS: {cms_date_range}")
        st.write(f"FDP: {fdp_date_range}")
    
    st.markdown("---")
    
    # Regional Summary Comparison
    st.markdown("### 🗺️ Regional Summary Comparison")
    
    cms_col, fdp_col = st.columns(2)
    
    with cms_col:
        st.markdown("#### CMS Data")
        render_regional_summary(cms_df, jamati_member_df, "CMS")
    
    with fdp_col:
        st.markdown("#### FDP Data")
        if fdp_df is not None:
            render_regional_summary(fdp_df, pd.DataFrame(), "FDP")
        else:
            st.error("FDP data not available")
    
    # Status Distribution Comparison
    with st.expander("📊 Status Distribution Comparison (Pie Charts)", expanded=False):
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            st.markdown("#### CMS Status Distribution")
            cms_status_counts = cms_df['status'].value_counts()
            cms_fig = px.pie(cms_status_counts, values=cms_status_counts.values, 
                            names=cms_status_counts.index, title=f'CMS Case Status - {date_range_text}')
            st.plotly_chart(cms_fig, use_container_width=True)
        
        with status_col2:
            st.markdown("#### FDP Status Distribution")
            if fdp_df is not None:
                fdp_status_counts = fdp_df['status'].value_counts()
                fdp_fig = px.pie(fdp_status_counts, values=fdp_status_counts.values, 
                               names=fdp_status_counts.index, title=f'FDP Case Status - {date_range_text}')
                st.plotly_chart(fdp_fig, use_container_width=True)
            else:
                st.error("FDP data not available")
    
    # Case Status by Region Comparison
    with st.expander("📊 Case Status by Region Comparison (Stacked Bar Charts)", expanded=False):
        region_status_col1, region_status_col2 = st.columns(2)
        
        with region_status_col1:
            st.markdown("#### CMS Case Status by Region")
            cms_status_region_df = cms_df.groupby(['region', 'status']).size().reset_index(name='count')
            
            if not cms_status_region_df.empty:
                cms_stacked_fig = px.bar(
                    cms_status_region_df, 
                    x='region', 
                    y='count', 
                    color='status',
                    title=f'CMS Case Status by Region - {date_range_text}',
                    labels={'count': 'Number of Cases', 'region': 'Region'},
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                cms_stacked_fig.update_layout(
                    xaxis_tickangle=-45,
                    height=500,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.02
                    )
                )
                
                st.plotly_chart(cms_stacked_fig, use_container_width=True)
            else:
                st.warning("No CMS data available for status distribution by region")
        
        with region_status_col2:
            st.markdown("#### FDP Case Status by Region")
            if fdp_df is not None:
                fdp_status_region_df = fdp_df.groupby(['region', 'status']).size().reset_index(name='count')
                
                if not fdp_status_region_df.empty:
                    fdp_stacked_fig = px.bar(
                        fdp_status_region_df, 
                        x='region', 
                        y='count', 
                        color='status',
                        title=f'FDP Case Status by Region - {date_range_text}',
                        labels={'count': 'Number of Cases', 'region': 'Region'},
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    
                    fdp_stacked_fig.update_layout(
                        xaxis_tickangle=-45,
                        height=500,
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="top",
                            y=1,
                            xanchor="left",
                            x=1.02
                        )
                    )
                    
                    st.plotly_chart(fdp_stacked_fig, use_container_width=True)
                else:
                    st.warning("No FDP data available for status distribution by region")
            else:
                st.error("FDP data not available")

def render_regional_summary(df, jamati_df, data_label):
    """Render regional summary for a specific dataset"""
    case_counts = df.groupby('region')['caseid'].nunique().reset_index(name='Number of Cases')
    
    if data_label == "CMS" and not jamati_df.empty:
        def count_individuals(region):
            case_ids = df[df['region'] == region]['caseid'].unique()
            return jamati_df[jamati_df['caseid'].isin(case_ids)].shape[0]
        case_counts['Number of Individuals'] = case_counts['region'].apply(count_individuals)
    else:
        def count_fdp_individuals(region):
            region_cases = df[df['region'] == region]
            if 'number_in_family' in region_cases.columns:
                return region_cases['number_in_family'].fillna(0).sum()
            return 0
        case_counts['Number of Individuals'] = case_counts['region'].apply(count_fdp_individuals)
    
    open_cases = df[df['status'].isin(['Open', 'Reopen'])]
    open_counts = open_cases.groupby('region')['caseid'].nunique().reset_index(name='Open Cases')
    case_counts = case_counts.merge(open_counts, on='region', how='left').fillna(0)
    
    closed_cases = df[df['status'].isin(['Closed'])]
    closed_counts = closed_cases.groupby('region')['caseid'].nunique().reset_index(name='Closed Cases')
    case_counts = case_counts.merge(closed_counts, on='region', how='left').fillna(0)
    
    # Format numbers
    display_df = case_counts.copy()
    display_df['Number of Cases'] = display_df['Number of Cases'].map('{:,}'.format)
    display_df['Number of Individuals'] = display_df['Number of Individuals'].astype(int).map('{:,}'.format)
    display_df['Open Cases'] = display_df['Open Cases'].astype(int).map('{:,}'.format)
    display_df['Closed Cases'] = display_df['Closed Cases'].astype(int).map('{:,}'.format)
    display_df = display_df.set_index('region')
    
    st.dataframe(display_df.style.set_properties(**{'font-size': '14px'}))