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
            e.name AS employer_name,
            ARRAY_AGG(DISTINCT s.skill_name) AS skills
        FROM
            ProjectDB.vacancy v
        JOIN
            ProjectDB.employer e ON v.employer_id = e.employer_id
        LEFT JOIN
            ProjectDB.vacancy_skill vs ON v.vacancy_id = vs.vacancy_id
        LEFT JOIN
            ProjectDB.skill s ON vs.skill_id = s.skill_id
        GROUP BY
            v.vacancy_id, v.title, v.text, v.type, v.deadline, v.url, e.name


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

    employers = vacancies_df['employer_name'].dropna().unique()
    types = vacancies_df['type'].dropna().unique()
    locations = vacancies_df['location_kommune'].dropna().unique()
    skills = sorted(set(skill for skill_list in vacancies_df['skills'] for skill in skill_list if skill))
    
    selected_employers = st.multiselect("Employer", sorted(employers))
    selected_types = st.multiselect("Vacancy Type", sorted(types))    
    selected_skills = st.sidebar.multiselect("Skills", skills, default=skills)
    selected_locations = st.multiselect("Location", sorted(locations))




# Filter data
filtered_df = vacancies_df.copy()

if selected_employers:
    filtered_df = filtered_df[filtered_df['employer_name'].isin(selected_employers)]

if selected_types:
    filtered_df = filtered_df[filtered_df['type'].isin(selected_types)]

if selected_locations:
    filtered_df = filtered_df[filtered_df['location_kommune'].isin(selected_locations)]

if selected_skills:
    filtered_df = filtered_df[
        filtered_df['skills'].apply(lambda sk: any(skill in sk for skill in selected_skills))
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
                if pd.notnull(vacancy['deadline']):
                    st.markdown(f"**Deadline:** {vacancy['deadline'].strftime('%Y-%m-%d')}")

                if pd.notnull(vacancy.get('contact_email')):
                    st.markdown(f"**Contact Email:** {vacancy['contact_email']}")
                if pd.notnull(vacancy.get('contact_phone')):
                    st.markdown(f"**Phone:** {vacancy['contact_phone']}")

                skills = vacancy.get('skills')
                if isinstance(skills, list) and skills:
                    st.markdown(f"**Skills:** {', '.join(skills)}")



                with st.expander("Job Description", expanded=False):
                    full_text = highlight_keywords(vacancy['text'], keywords)
                    st.markdown(full_text, unsafe_allow_html=False)
                st.link_button("Apply", vacancy['url'])    
