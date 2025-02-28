# marvel_dashboard.py - Streamlit Dashboard for Marvel Healthcare Data

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import plotly.graph_objects as go
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(layout="wide", page_title="Marvel Healthcare Insights Dashboard")

# Application title
st.title("🦸‍♂️ Marvel Healthcare Insights Dashboard")
st.markdown("Analyzing stakeholder interactions for Vibranium therapeutic assets")

# Load data
@st.cache_data
def load_data():
    try:
        # Load the Marvel dataset
        df = pd.read_csv("honeypot_data_Marvel.csv")
        
        # Convert date column to datetime
        df['occurrence_date'] = pd.to_datetime(df['occurrence_date'])
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Return empty DataFrame with expected columns if there's an error
        return pd.DataFrame(columns=['occurrence_date', 'country', 'therapeutic_area_names', 
                                    'interaction_type', 'stakeholder_type', 'asset_names', 
                                    'stakeholder_names', 'msl_names', 'text'])

# Load the data
data = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
min_date = data['occurrence_date'].min().date() if not data.empty else datetime.now().date() - timedelta(days=365)
max_date = data['occurrence_date'].max().date() if not data.empty else datetime.now().date()

start_date = st.sidebar.date_input(
    "Start date", 
    min_date
)
end_date = st.sidebar.date_input(
    "End date", 
    max_date
)

# Convert to datetime for filtering
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

# Country filter
if not data.empty:
    countries = ['All'] + sorted(data['country'].unique().tolist())
    selected_country = st.sidebar.selectbox("Select Country", countries)
else:
    selected_country = 'All'

# Stakeholder type filter
if not data.empty:
    stakeholder_types = ['All'] + sorted(data['stakeholder_type'].unique().tolist())
    selected_stakeholder_type = st.sidebar.selectbox("Select Stakeholder Type", stakeholder_types)
else:
    selected_stakeholder_type = 'All'

# Interaction type filter
if not data.empty:
    interaction_types = ['All'] + sorted(data['interaction_type'].unique().tolist())
    selected_interaction_type = st.sidebar.selectbox("Select Interaction Type", interaction_types)
else:
    interaction_types = ['All']
    selected_interaction_type = 'All'

# Filter data based on selections
filtered_data = data.copy()

# Date filter
filtered_data = filtered_data[(filtered_data['occurrence_date'] >= start_date) & 
                            (filtered_data['occurrence_date'] <= end_date)]

# Country filter
if selected_country != 'All':
    filtered_data = filtered_data[filtered_data['country'] == selected_country]

# Stakeholder type filter
if selected_stakeholder_type != 'All':
    filtered_data = filtered_data[filtered_data['stakeholder_type'] == selected_stakeholder_type]

# Interaction type filter
if selected_interaction_type != 'All':
    filtered_data = filtered_data[filtered_data['interaction_type'] == selected_interaction_type]

# Display basic metrics
st.subheader("Summary Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Interactions", len(filtered_data))

with col2:
    unique_stakeholders = filtered_data['stakeholder_names'].nunique()
    st.metric("Unique Stakeholders", unique_stakeholders)

with col3:
    unique_msls = filtered_data['msl_names'].nunique()
    st.metric("Unique MSLs", unique_msls)

with col4:
    unique_assets = filtered_data['asset_names'].nunique() if 'asset_names' in filtered_data.columns else 0
    st.metric("Unique Assets", unique_assets)

# Create layouts for visualizations
tab1, tab2, tab3 = st.tabs(["Timeline Analysis", "Geographic Distribution", "Stakeholder Engagement"])

# Tab 1: Timeline Analysis
with tab1:
    st.subheader("Interaction Trends Over Time")
    
    # Aggregate data by date
    if not filtered_data.empty:
        # Group by month and count interactions
        filtered_data['year_month'] = filtered_data['occurrence_date'].dt.strftime('%Y-%m')
        monthly_counts = filtered_data.groupby(['year_month', 'interaction_type']).size().reset_index(name='count')
        
        # Create time series chart
        fig = px.line(monthly_counts, x='year_month', y='count', color='interaction_type',
                    title="Monthly Interactions by Type",
                    labels={'count': 'Number of Interactions', 'year_month': 'Month', 'interaction_type': 'Interaction Type'})
        
        # Improve layout
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Number of Interactions",
            legend_title="Interaction Type",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Stakeholder type distribution over time
        stakeholder_monthly = filtered_data.groupby(['year_month', 'stakeholder_type']).size().reset_index(name='count')
        
        fig2 = px.line(stakeholder_monthly, x='year_month', y='count', color='stakeholder_type',
                     title="Monthly Interactions by Stakeholder Type",
                     labels={'count': 'Number of Interactions', 'year_month': 'Month', 'stakeholder_type': 'Stakeholder Type'})
        
        # Improve layout
        fig2.update_layout(
            xaxis_title="Month",
            yaxis_title="Number of Interactions",
            legend_title="Stakeholder Type",
            height=500
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

# Tab 2: Geographic Distribution
with tab2:
    st.subheader("Geographic Distribution of Interactions")
    
    if not filtered_data.empty:
        # Country distribution
        country_counts = filtered_data.groupby('country').size().reset_index(name='count')
        
        fig = px.choropleth(country_counts, locations='country', locationmode='country names',
                          color='count', hover_name='country',
                          color_continuous_scale=px.colors.sequential.Plasma,
                          title="Interaction Count by Country")
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Bar chart for country comparison
        fig2 = px.bar(country_counts.sort_values('count', ascending=False), 
                    x='country', y='count',
                    title="Interactions by Country",
                    labels={'count': 'Number of Interactions', 'country': 'Country'})
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Distribution of interaction types by country
        country_interaction = filtered_data.groupby(['country', 'interaction_type']).size().reset_index(name='count')
        
        fig3 = px.bar(country_interaction, x='country', y='count', color='interaction_type',
                    title="Interaction Types by Country",
                    labels={'count': 'Number of Interactions', 'country': 'Country', 'interaction_type': 'Interaction Type'})
        
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

# Tab 3: Stakeholder Engagement
with tab3:
    st.subheader("Stakeholder Engagement Analysis")
    
    if not filtered_data.empty:
        # Stakeholder type distribution
        stakeholder_counts = filtered_data.groupby('stakeholder_type').size().reset_index(name='count')
        
        fig = px.pie(stakeholder_counts, values='count', names='stakeholder_type',
                   title="Distribution of Stakeholder Types")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Interaction type distribution
        interaction_counts = filtered_data.groupby('interaction_type').size().reset_index(name='count')
        
        fig2 = px.pie(interaction_counts, values='count', names='interaction_type',
                    title="Distribution of Interaction Types")
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Top stakeholders by number of interactions
        top_stakeholders = filtered_data.groupby('stakeholder_names').size().reset_index(name='count').sort_values('count', ascending=False).head(10)
        
        fig3 = px.bar(top_stakeholders, x='stakeholder_names', y='count',
                    title="Top 10 Most Engaged Stakeholders",
                    labels={'count': 'Number of Interactions', 'stakeholder_names': 'Stakeholder Name'})
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Top MSLs by number of interactions
        top_msls = filtered_data.groupby('msl_names').size().reset_index(name='count').sort_values('count', ascending=False).head(10)
        
        fig4 = px.bar(top_msls, x='msl_names', y='count',
                    title="Top 10 Most Active MSLs",
                    labels={'count': 'Number of Interactions', 'msl_names': 'MSL Name'})
        
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

# Text Analysis section
st.subheader("Insight Text Analysis")

if not filtered_data.empty:
    # Display random sample of insight texts
    sample_size = min(5, len(filtered_data))
    text_sample = filtered_data.sample(sample_size)
    
    for i, (_, row) in enumerate(text_sample.iterrows()):
        with st.expander(f"Insight {i+1} - {row['stakeholder_names']} ({row['occurrence_date'].strftime('%Y-%m-%d')})"):
            st.write(f"**Stakeholder:** {row['stakeholder_names']} ({row['stakeholder_type']})")
            st.write(f"**MSL:** {row['msl_names']}")
            st.write(f"**Interaction Type:** {row['interaction_type']}")
            st.write(f"**Country:** {row['country']}")
            st.write(f"**Date:** {row['occurrence_date'].strftime('%Y-%m-%d')}")
            st.write("**Text:**")
            st.info(row['text'])
else:
    st.info("No data available for text analysis with the selected filters.")

# Export functionality
st.subheader("Export Data")
if st.button("Export Filtered Data to CSV"):
    # Create a download link for the filtered data
    csv = filtered_data.to_csv(index=False)
    
    # Use components.html to create a download link
    download_link = f"""
    <a href="data:text/csv;charset=utf-8,{csv}" download="marvel_filtered_data.csv" target="_blank">
        Click here to download the filtered data as CSV
    </a>
    """
    st.markdown(download_link, unsafe_allow_html=True)

# Additional metadata
st.markdown("---")
st.caption(f"Dashboard showing data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
st.caption("Note: This dashboard uses fictional Marvel-themed healthcare data for demonstration purposes.")
