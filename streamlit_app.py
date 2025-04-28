import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# Set Streamlit page config
st.set_page_config(page_title="BigQuery Connection Test", page_icon="✅", layout="wide")

# Title
st.title("✅ BigQuery Connection Test")

# Load credentials from Streamlit Secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Initialize BigQuery client
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Test query to check if connection works
query = """
    SELECT CURRENT_DATE() AS today_date
"""

# Execute query
try:
    query_job = client.query(query)
    df = query_job.to_dataframe()

    # Success!
    st.success("🎉 Connection to BigQuery was successful!")
    st.write("Today's date from BigQuery server:", df)

except Exception as e:
    st.error(f"❌ Failed to connect to BigQuery: {e}")
