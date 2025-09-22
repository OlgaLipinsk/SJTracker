import streamlit as st
import pandas as pd
import re
import uuid
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
st.set_page_config(page_title="Vacancy Dashboard", page_icon="🧩", layout="wide")

# Load credentials from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

PROJECT = credentials.project_id
DATASET = "ProjectDB"

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------
def run_query(query, params=None):
    job_config = bigquery.QueryJobConfig(query_parameters=params or [])
    return client.query(query, job_config=job_config).to_dataframe()

def insert_row(table, row):
    table_id = f"{PROJECT}.{DATASET}.{table}"
    errors = client.insert_rows_json(table_id, [row])
    return errors

# -------------------------------------------------------------------
# AUTHENTICATION
# -------------------------------------------------------------------
def register_user(email):
    user_id = str(uuid.uuid4())
    row = {
        "user_id": user_id,
        "email": email,
        "role": "user",
        "created_at": datetime.utcnow().isoformat()
    }
    insert_row("users", row)
    return row

def get_user(email):
    query = f"SELECT * FROM `{PROJECT}.{DATASET}.users` WHERE email=@e LIMIT 1"
    params = [bigquery.ScalarQueryParameter("e", "STRING", email)]
    df = run_query(query, params)
    return df.iloc[0].to_dict() if not df.empty else None

# Login / registration UI
if "user" not in st.session_state:
    st.session_state["user"] = None

menu = st.sidebar.radio("Navigation", ["Job Board", "Register/Login"])

if menu == "Register/Login":
    st.header("🔑 Register / Login")
    email = st.text_input("Your email")
    if st.button("Login / Register"):
        if email:
            user = get_user(email)
            if not user:
                user = register_user(email)
                st.success("New user registered")
            else:
                st.success("Welcome back!")
            st.session_state["user"] = user
        else:
            st.warning("Please enter an email")

# -------------------------------------------------------------------
# COMMENTS
# -------------------------------------------------------------------
def get_comments(job_id):
    query = f"""
        SELECT comment_id, user_id, comment_text, created_at, deleted_by
        FROM `{PROJECT}.{DATASET}.comments`
        WHERE job_id=@j
        ORDER BY created_at ASC
    """
    params = [bigquery.ScalarQueryParameter("j", "STRING", job_id)]
    return run_query(query, params)

def add_comment(job_id, user_id, text):
    row = {
        "comment_id": str(uuid.uuid4()),
        "job_id": job_id,
        "user_id": user_id,
        "comment_text": text,
        "created_at": datetime.utcnow().isoformat()
    }
    return insert_row("comments", row)

def delete_comment(comment_id, rep_email):
    query = f"""
        UPDATE `{PROJECT}.{DATASET}.comments`
        SET deleted_by=@rep
        WHERE comment_id=@cid
    """
    job_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("rep", "STRING", rep_email),
        bigquery.ScalarQueryParameter("cid", "STRING", comment_id),
    ])
    client.query(query, job_config=job_config).result()

# -------------------------------------------------------------------
# JOB LIST & DETAIL
# -------------------------------------------------------------------
def load_vacancy_data():
    query = """
        SELECT v.vacancy_id, v.title, v.text, v.type, v.deadline, v.url,
               e.name AS employer_name, l.kommune AS location_kommune,
               v.contact_email
        FROM ProjectDB.vacancy v
        JOIN ProjectDB.employer e ON v.employer_id = e.employer_id
        LEFT JOIN ProjectDB.vacancy_location vl ON v.vacancy_id = vl.vacancy_id
        LEFT JOIN ProjectDB.location l ON vl.location_id = l.location_id
    """
    return client.query(query).to_dataframe()

vacancies_df = load_vacancy_data()

if menu == "Job Board":
    st.title("💼 Student Job Tracker")

    if "selected_job" not in st.session_state:
        st.session_state["selected_job"] = None

    if not st.session_state["selected_job"]:
        st.subheader(f"Showing {len(vacancies_df)} vacancies")
        for _, vacancy in vacancies_df.iterrows():
            with st.container():
                st.markdown(f"### {vacancy['title']}")
                st.markdown(f"**Employer:** {vacancy['employer_name']}")
                if st.button("View details", key=vacancy['vacancy_id']):
                    st.session_state["selected_job"] = vacancy['vacancy_id']
                    st.experimental_rerun()
    else:
        job_id = st.session_state["selected_job"]
        job = vacancies_df[vacancies_df["vacancy_id"] == job_id].iloc[0]

        st.subheader(job["title"])
        st.caption(f"{job['employer_name']} | {job['location_kommune']}")
        st.write(job["text"])
        st.link_button("Apply", job["url"])

        st.markdown("### 💬 Comments")
        comments_df = get_comments(job_id)
        if comments_df.empty:
            st.info("No comments yet.")
        else:
            for _, row in comments_df.iterrows():
                if row["deleted_by"]:
                    st.markdown(f"~~{row['comment_text']}~~ _(deleted by {row['deleted_by']})_")
                else:
                    st.markdown(f"- {row['comment_text']} _(by {row['user_id']})_")

                    # Rep moderation control
                    if st.session_state["user"] and job["contact_email"] == st.session_state["user"]["email"]:
                        if st.button(f"Delete {row['comment_id']}", key=row["comment_id"]):
                            delete_comment(row["comment_id"], st.session_state["user"]["email"])
                            st.experimental_rerun()

        if st.session_state["user"]:
            st.text_area("Add a comment", key="new_comment")
            if st.button("Post comment"):
                text = st.session_state["new_comment"]
                if text.strip():
                    add_comment(job_id, st.session_state["user"]["email"], text)
                    st.experimental_rerun()
        else:
            st.info("Login to add comments.")
