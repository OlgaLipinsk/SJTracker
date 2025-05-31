import streamlit as st
import pandas as pd
import re
from google.cloud import bigquery
from google.oauth2 import service_account

# Set page configuration
st.set_page_config(page_title="Vacancy Dashboard", page_icon="🧩", layout="wide")
st.title("Vacancy Dashboard")

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

# Load vacancy main data
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

# Load location mappings
def load_location_data():
    query = """
        SELECT
            vl.vacancy_id,
            l.name AS location
        FROM
            `ProjectDB.vacancy_location` vl
        JOIN
            `ProjectDB.location` l
        ON
            vl.location_id = l.location_id
    """
    return client.query(query).to_dataframe()

# Load keyword mappings
def load_keyword_data():
    query = """
        SELECT
            vk.vacancy_id,
            k.word AS keyword
        FROM
            `ProjectDB.vacancy_keyword` vk
        JOIN
            `ProjectDB.keyword` k
        ON
            vk.keyword_id = k.keyword_id
    """
    return client.query(query).to_dataframe()

# Load all data
vacancies_df = load_vacancy_data()
location_df = load_location_data()
keyword_map_df = load_keyword_data()

# Aggregate keywords and locations per vacancy
vacancies_df = vacancies_df.merge(
    location_df.groupby("vacancy_id")["location"].apply(list).reset_index(), 
    on="vacancy_id", how="left"
)
vacancies_df = vacancies_df.merge(
    keyword_map_df.groupby("vacancy_id")["keyword"].apply(list).reset_index(),
    on="vacancy_id", how="left"
)

# Flatten all unique values for filters
all_locations = sorted({loc for sublist in vacancies_df['location'].dropna() for loc in sublist})
all_keywords = sorted({kw for sublist in vacancies_df['keyword'].dropna() for kw in sublist})
employers = sorted(vacancies_df['employer_name'].unique())
types = sorted(vacancies_df['type'].unique())

# Sidebar filters
with st.sidebar:
    st.header("🔎 Filters")
    selected_employers = st.multiselect("Employer", employers, default=employers)
    selected_types = st.multiselect("Vacancy Type", types, default=types)
    selected_locations = st.multiselect("Location", all_locations, default=all_locations)
    selected_keywords = st.multiselect("Keyword", all_keywords, default=all_keywords)
    min_date = vacancies_df['deadline'].min()
    max_date = vacancies_df['deadline'].max()
    selected_dates = st.date_input("Deadline Range", [min_date, max_date])

# Apply filters
filtered_df = vacancies_df[
    (vacancies_df['employer_name'].isin(selected_employers)) &
    (vacancies_df['type'].isin(selected_types)) &
    (vacancies_df['deadline'] >= pd.to_datetime(selected_dates[0])) &
    (vacancies_df['deadline'] <= pd.to_datetime(selected_dates[1])) &
    (vacancies_df['location'].apply(lambda locs: any(l in locs for l in selected_locations) if isinstance(locs, list) else False)) &
    (vacancies_df['keyword'].apply(lambda kws: any(k in kws for k in selected_keywords) if isinstance(kws, list) else False))
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
                st.markdown(f"**Deadline:** {vacancy['deadline'].strftime('%Y-%m-%d')}")
                st.markdown(f"**Location:** {', '.join(vacancy['location']) if vacancy['location'] else 'N/A'}")
                with st.expander("Job Description", expanded=False):
                    full_text = highlight_keywords(vacancy['text'], all_keywords)
                    st.markdown(full_text, unsafe_allow_html=False)
                st.link_button("Apply", vacancy['url'])
