import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# Set page configuration
st.set_page_config(page_title="Vacancy Dashboard", page_icon="🧩", layout="wide")

st.title("🧩 Vacancy Tile Dashboard")

# Load credentials from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Initialize BigQuery client
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Fetch vacancy data
# @st.cache_data
def load_vacancy_data():
    query = """
        SELECT
            v.vacancy_id,
            v.title,
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
    query_job = client.query(query)
    return query_job.to_dataframe()

vacancies_df = load_vacancy_data()

# Sidebar filters
with st.sidebar:
    st.header("🔎 Filters")

    employers = vacancies_df['employer_name'].unique()
    selected_employers = st.multiselect("Employer", employers, default=employers)

    types = vacancies_df['type'].unique()
    selected_types = st.multiselect("Vacancy Type", types, default=types)

    min_date = vacancies_df['deadline'].min()
    max_date = vacancies_df['deadline'].max()
    selected_dates = st.date_input("Deadline Range", [min_date, max_date])

# Filter data based on selections
filtered_df = vacancies_df[
    (vacancies_df['employer_name'].isin(selected_employers)) &
    (vacancies_df['type'].isin(selected_types)) &
    (vacancies_df['deadline'] >= pd.to_datetime(selected_dates[0])) &
    (vacancies_df['deadline'] <= pd.to_datetime(selected_dates[1]))
]

# Display vacancies as tiles
st.subheader(f"Showing {len(filtered_df)} vacancies")

cols_per_row = 3

for idx in range(0, len(filtered_df), cols_per_row):
    row = st.columns(cols_per_row)
    for col_idx, vacancy_idx in enumerate(range(idx, min(idx + cols_per_row, len(filtered_df)))):
        with row[col_idx]:
            vacancy = filtered_df.iloc[vacancy_idx]
            st.markdown(f"""
                <div style='border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px;'>
                    <h4 style='margin-bottom: 5px;'>{vacancy['title']}</h4>
                    <p><strong>Employer:</strong> {vacancy['employer_name']}</p>
                    <p><strong>Type:</strong> {vacancy['type']}</p>
                    <p><strong>Deadline:</strong> {vacancy['deadline'].strftime('%Y-%m-%d')}</p>
                    <a href='{vacancy['url']}' target='_blank'>
                        <button style='padding: 8px 12px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;'>Apply</button>
                    </a>
                </div>
            """, unsafe_allow_html=True)

