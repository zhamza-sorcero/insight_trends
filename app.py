# dashboard.py - Example Streamlit Dashboard with Cross-Frame Communication

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(layout="wide", page_title="Insight Trends Dashboard")


# Setup cross-frame communication using streamlit's built-in components
def send_to_parent(message_type, payload):
    message = {"type": message_type, "payload": payload}
    js_code = f"""
    <script>
    window.parent.postMessage({json.dumps(message)}, '*');
    </script>
    """
    components.html(js_code, height=0)


def receive_from_parent():
    """
    Sets up a listener for messages from the parent frame.
    Note: In this simplified version, we're not actually retrieving values
    from JavaScript - that would require session state or custom components.
    """
    js_code = """
    <script>
    if (!window._received_message) {
        window._received_message = {};
        window.addEventListener('message', function(event) {
            window._received_message = event.data;
            // Store message in sessionStorage so we can retrieve it later
            sessionStorage.setItem('parentMessage', JSON.stringify(event.data));
            console.log('Message received from parent:', event.data);
        });
    }
    </script>
    """
    components.html(js_code, height=0)


# Get context from parent frame
receive_from_parent()
# Since we can't directly get values from JS in this way, we'll use default values
# In a real implementation, you would need to find a way to pass data from JS to Python
# Options include URL parameters, session state, or custom components

# Define default context values
context = {"userContext": {}, "filters": {}}
user_context = {}  # Default empty user context
initial_filters = {}  # Default empty filters

# Application title
st.title("Insight Trends Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter with defaults
default_start_date = datetime.now() - timedelta(days=90)
# Try to use initial filters if available
try:
    default_start = datetime.strptime(initial_filters.get("startDate", ""), "%Y-%m-%d") if initial_filters.get(
        "startDate") else default_start_date
    default_end = datetime.strptime(initial_filters.get("endDate", ""), "%Y-%m-%d") if initial_filters.get(
        "endDate") else datetime.now()
except (ValueError, TypeError):
    # Fallback to default dates if there's any issue
    default_start = default_start_date
    default_end = datetime.now()

start_date = st.sidebar.date_input(
    "Start date",
    default_start
)
end_date = st.sidebar.date_input(
    "End date",
    default_end
)

# Topic filter
topics = ["Safety", "Efficacy", "Market Access", "Competitive Landscape", "Unmet Need", "Treatment Patterns", "All"]
default_topic = "All"

# Try to use initial filters if available
if initial_filters and isinstance(initial_filters, dict):
    default_topic = initial_filters.get("topic", "All")
    # Ensure the topic is valid
    if default_topic not in topics:
        default_topic = "All"

selected_topic = st.sidebar.selectbox(
    "Select Topic",
    topics,
    index=topics.index(default_topic)
)

# When filters change, notify parent
if st.sidebar.button("Apply Filters"):
    filter_payload = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "topic": selected_topic
    }
    send_to_parent("filterChanged", filter_payload)


# Load data
@st.cache_data
def load_data():
    # This would be replaced with actual data loading code
    try:
        # For production, this would make a secure API call
        return pd.read_csv("insights_data.csv")
    except FileNotFoundError:
        # Create dummy data if file doesn't exist
        st.warning("Sample data file not found. Using dummy data.")
        # Create sample data
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        regions = ['North America', 'Europe', 'Asia', 'Latin America']
        countries = ['United States', 'Canada', 'Germany', 'France', 'China', 'Japan', 'Brazil', 'Mexico']
        stages = ['Early', 'Mid', 'Late']
        topics_list = topics[:-1]  # All topics except "All"

        import numpy as np

        n_samples = 100
        data = {
            'id': range(1, n_samples + 1),
            'created_at': np.random.choice(dates, n_samples),
            'region': np.random.choice(regions, n_samples),
            'country': np.random.choice(countries, n_samples),
            'stage': np.random.choice(stages, n_samples),
            'topic': np.random.choice(topics_list, n_samples)
        }
        return pd.DataFrame(data)


data = load_data()

# Filter data based on selections
if selected_topic != "All":
    data = data[data["topic"] == selected_topic]
data = data[(data["created_at"] >= pd.Timestamp(start_date)) &
            (data["created_at"] <= pd.Timestamp(end_date))]

# Layout with columns
col1, col2 = st.columns(2)

# Trend chart
with col1:
    st.subheader("Insight Generation Over Time by Region")

    # Aggregate data by region and date
    trend_data = data.groupby(["region", pd.Grouper(key="created_at", freq="W")])["id"].count().reset_index()
    trend_data = trend_data.rename(columns={"id": "count", "created_at": "week"})

    fig = px.line(trend_data, x="week", y="count", color="region",
                  title="Weekly Insight Count by Region",
                  labels={"count": "Number of Insights", "week": "Week"})

    # Add click handler to communicate with parent
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>%{y} Insights<extra></extra>',
    )

    st.plotly_chart(fig, use_container_width=True)

# Map visualization
with col2:
    st.subheader("Insight Distribution by Country")

    # Aggregate data by country
    map_data = data.groupby("country")["id"].count().reset_index()
    map_data = map_data.rename(columns={"id": "count"})

    fig = px.choropleth(map_data, locations="country", locationmode="country names",
                        color="count", hover_name="country",
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title="Insight Count by Country")

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    # Note: Built-in click handling with parent communication requires custom JavaScript

# Stage breakdown
st.subheader("Insight Stages Breakdown")
stage_data = data.groupby("stage")["id"].count().reset_index()
stage_data = stage_data.rename(columns={"id": "count"})

fig = px.bar(stage_data, x="stage", y="count",
             title="Insights by Stage",
             labels={"count": "Number of Insights", "stage": "Stage"})

st.plotly_chart(fig, use_container_width=True)

# Add action buttons that communicate with parent
st.subheader("Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Create Collection from Selection"):
        filter_payload = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "topic": selected_topic
        }
        send_to_parent("createCollection", {"filters": filter_payload})

with col2:
    if st.button("Export Data"):
        send_to_parent("exportRequest", {"format": "csv"})

with col3:
    if st.button("Share Dashboard"):
        # Using components.html for JavaScript execution
        js_code = """
        <script>
        const currentUrl = window.location.href;
        window.parent.postMessage({"type": "shareRequest", "payload": {"url": currentUrl}}, '*');
        </script>
        """
        components.html(js_code, height=0)

# Additional metadata
st.markdown("---")
st.caption(f"Dashboard generated for {user_context.get('name', 'User')} | Showing data from {start_date} to {end_date}")
