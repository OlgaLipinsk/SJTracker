# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("🔎 Filters")

    employers = vacancies_df['employer_name'].dropna().unique()
    types = vacancies_df['type'].dropna().unique()
    locations = vacancies_df['location_kommune'].dropna().unique()
    skills = sorted(set(skill for skill_list in vacancies_df['skills'] for skill in skill_list if skill))

    selected_employers = st.multiselect("Employer", sorted(employers))
    selected_types = st.multiselect("Vacancy Type", sorted(types))    
    selected_skills = st.multiselect("Skills", sorted(skills))
    selected_locations = st.multiselect("Location", sorted(locations))

# --- APPLY FILTERS ---
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

# --- DISPLAY WITH COMMENTS BUTTON ---
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
                    st.markdown(f"**Deadline:** {vacancy['deadline']}")

                with st.expander("Job Description", expanded=False):
                    full_text = highlight_keywords(vacancy['text'], keywords)
                    st.markdown(full_text, unsafe_allow_html=False)

                c1, c2 = st.columns([1,1])
                with c1:
                    st.link_button("Apply", vacancy['url'])
                with c2:
                    if st.button("Comments", key=f"cbtn-{vacancy['vacancy_id']}"):
                        st.session_state["show_comments"] = vacancy['vacancy_id']

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
