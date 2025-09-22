import streamlit as st
import pandas as pd
import re
import uuid
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account

# Page config
st.set_page_config(page_title="Vacancy Dashboard", page_icon="🧩", layout="wide")

# Load credentials
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

PROJECT = credentials.project_id
DATASET = "ProjectDB"

# --- COMMENTS HELPERS ---
def get_comments(job_id, limit=5):
    query = f"""
        SELECT comment_id, comment_text, created_at, deleted_by
        FROM `{PROJECT}.{DATASET}.comments`
        WHERE job_id=@jid
        ORDER BY created_at DESC
        LIMIT {limit}
    """
    params = [bigquery.ScalarQueryParameter("jid", "STRING", job_id)]
    return client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params)).to_dataframe()

def add_comment(job_id, text):
    row = {
        "comment_id": str(uuid.uuid4()),
        "job_id": job_id,
        "user_id": "anonymous",   # 👈 no login, just anonymous
        "comment_text": text,
        "created_at": datetime.utcnow().isoformat(),
        "deleted_by": None
    }
    table_id = f"{PROJECT}.{DATASET}.comments"
    errors = client.insert_rows_json(table_id, [row])
    return errors

# --- YOUR EXISTING JOB QUERY ---
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
          l.kommune AS location_kommune
        FROM ProjectDB.vacancy v
        JOIN ProjectDB.employer e ON v.employer_id = e.employer_id
        LEFT JOIN ProjectDB.vacancy_location vl ON v.vacancy_id = vl.vacancy_id
        LEFT JOIN ProjectDB.location l ON vl.location_id = l.location_id
    """
    return client.query(query).to_dataframe()

vacancies_df = load_vacancy_data()

# --- DISPLAY ---
st.subheader(f"Showing {len(vacancies_df)} vacancies")

cols_per_row = 3

for idx in range(0, len(vacancies_df), cols_per_row):
    row = st.columns(cols_per_row)
    for col_idx, vacancy_idx in enumerate(range(idx, min(idx + cols_per_row, len(vacancies_df)))):
        with row[col_idx]:
            vacancy = vacancies_df.iloc[vacancy_idx]
            with st.container():
                st.markdown(f"### {vacancy['title']}")
                st.markdown(f"**Employer:** {vacancy['employer_name']}")
                st.markdown(f"**Type:** {vacancy['type']}")
                if pd.notnull(vacancy['deadline']):
                    st.markdown(f"**Deadline:** {vacancy['deadline']}")

                with st.expander("Job Description", expanded=False):
                    st.markdown(vacancy['text'] or "")

                # Buttons row
                c1, c2 = st.columns([1,1])
                with c1:
                    st.link_button("Apply", vacancy['url'])
                with c2:
                    if st.button("Comments", key=f"cbtn-{vacancy['vacancy_id']}"):
                        st.session_state["show_comments"] = vacancy['vacancy_id']

                # Comments expander (only for clicked job)
                if st.session_state.get("show_comments") == vacancy["vacancy_id"]:
                    with st.expander("💬 Comments", expanded=True):
                        comments_df = get_comments(vacancy["vacancy_id"])
                        if comments_df.empty:
                            st.info("No comments yet.")
                        else:
                            for _, c in comments_df.iterrows():
                                if c["deleted_by"]:
                                    st.markdown(f"~~{c['comment_text']}~~ _(deleted by {c['deleted_by']})_")
                                else:
                                    st.markdown(f"- {c['comment_text']} _(at {c['created_at']})_")

                        # Comment form
                        new_comment = st.text_area("Write a comment", key=f"ta-{vacancy['vacancy_id']}")
                        if st.button("Post comment", key=f"pc-{vacancy['vacancy_id']}"):
                            if new_comment.strip():
                                err = add_comment(vacancy["vacancy_id"], new_comment.strip())
                                if err:
                                    st.error(f"Failed: {err}")
                                else:
                                    st.success("Comment added! Refresh to see it.")
                            else:
                                st.warning("Empty comment not posted.")
