import streamlit as st
import pandas as pd
import re
from google.cloud import bigquery
from google.oauth2 import service_account

# Set page configuration
st.set_page_config(page_title="Vacancy Dashboard", page_icon="🧩", layout="wide")
st.title("🧩 Vacancy Dashboard")

# Load credentials from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Initialize BigQuery client
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Highlight keywords in job description
def highlight_keywords(text, keywords):
    if not keywords or not isinstance(text, str):
        return text
    pattern = r"\b(" + "|".join(map(re.escape, keywords)) + r")\b"
    return re.sub(pattern, r"**\1**", text, flags=re.IGNORECASE)

# Load vacancy data
def load_vacancy_data():
    query = """
        SELECT
            v.vacancy_id,
            v.title,
            v.text,
            v.type,
            v.deadline,
            v.url,
            e.name AS employer_name
        FROM
            `ProjectDB.vacancy` v
        JOIN
            `ProjectDB.employer` e
        ON
            v.employer_id = e.employer_id
        ORDER BY v.deadline ASC
    """
    return client.query(query).to_dataframe()

vacancies_df = load_vacancy_data()

# Load keywords for highlighting
keyword_query = "SELECT word FROM ProjectDB.keyword"
keywords_df = client.query(keyword_query).to_dataframe()
keywords = keywords_df['word'].dropna().tolist()

# Sidebar filters
with st.sidebar:
    st.header("🔎 Filters")

    employers = vacancies_df['employer_name'].unique()
    selected_employers = st.multiselect("Employer", employers, default=employers)

    types = vacancies_df['type'].unique()
    selected_types = st.multiselect("Vacancy Type", types, default=types)


# Filter data
filtered_df = vacancies_df[
    (vacancies_df['employer_name'].isin(selected_employers)) &
    (vacancies_df['type'].isin(selected_types))
]

# Display vacancies
st.subheader(f"Showing {len(filtered_df)} vacancies")

cols_per_row = 3

for idx in range(0, len(filtered_df), cols_per_row):
    row = st.columns(cols_per_row)
    for col_idx, vacancy_idx in enumerate(range(idx, min(idx + cols_per_row, len(filtered_df)))):
        with row[col_idx]:
            vacancy = filtered_df.iloc[vacancy_idx]
            with st.container():
                st.markdown(f"### {vacancy['title']}")
                st.markdown(f"**Employer:** {vacancy['employer_name']}")
                st.markdown(f"**Type:** {vacancy['type']}")
                
                with st.expander("Job Description", expanded=False):
                    full_text = highlight_keywords(vacancy['text'], keywords)
                    st.markdown(full_text, unsafe_allow_html=False)
                st.link_button("Apply", vacancy['url'])    
