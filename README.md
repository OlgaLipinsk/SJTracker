# Student Job Tracker

A Streamlit web application for tracking and exploring job vacancies, built with BigQuery database backend.

## Launch the App

https://studentjobtracker.streamlit.app/

## Features

- Searchable and filterable job vacancies
- Normalized SQL schema with employers, locations, contacts, skills, and keywords
- Data loading via a stored procedure
- Deployable and interactive via Streamlit

## Database Schema

See the included ER_Diagram.pdf for the database model.

## Documentation

- The database model is described in `ER_Diagram.pdf`.
- The Streamlit app uses SQL `SELECT` queries to fetch and display data from BigQuery.
- Backend data preparation is handled via SQL scripts that include `MERGE` and `INSERT` operations to normalize and populate the database.
- The `staging_vacancy` table is populated manually using `INSERT` statements. This is an area for potential extension — for example, by integrating an automated scraper.
- The `refresh_vacancy_data` procedure loads and normalizes data from the staging table into the main schema using `MERGE` and `INSERT`, and is run manually via `CALL ProjectDB.refresh_vacancy_data()`.

## Project Files

- streamlit_app.py — Main Streamlit frontend that displays job data and interacts with the database
- create_tables.sql — SQL script that creates the tables
- refresh_vacancy_data.sql — SQL script that defines the stored procedure to populate the schema
- requirements.txt — Python dependencies needed to run the app
- ER_Diagram.pdf — Entity-Relationship diagram showing database structure
- example_insert.sql - An example of correct insert statement for staging_vacancy
- .gitignore — Excludes files from version control
- README.md — Project documentation and usage instructions

## Usage of regular expressions

- In the SQL procedure: to validate email addresses and URLs — non-matching values are discarded (NULL).
- In the app: to highlight predefined keywords in the vacancy description dynamically.

# More Detailed instructions

## How to Run and Set Up the App

This project uses **Streamlit** for the frontend and **Google BigQuery** for data storage. There is no compilation step — the app runs as a standard Streamlit script.

### Running Locally

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Add your GCP service account credentials to a file:

   `.streamlit/secrets.toml` (you may need to create the `.streamlit/` folder)

   ```toml
   [gcp_service_account]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "..."
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account@gcp-project.iam.gserviceaccount.com"
   ...
   ```

3. Run the app:

   ```bash
   streamlit run streamlit_app.py
   ```

---

### Deploying on Streamlit Community Cloud

1. Create a [Streamlit account](https://streamlit.io/cloud)
2. Connect your GitHub repo
3. Add the `secrets.toml` under **App Settings > Secrets**
4. Click **Deploy**

---

## How to Initialize the BigQuery Database

You’ll need a GCP project with BigQuery enabled. Instructions assume you are familiar with GCP or can follow [official BigQuery documentation](https://cloud.google.com/bigquery/docs).

1. Create a BigQuery dataset called `ProjectDB`
2. Run `create_tables.sql` to initialize the schema
3. Run `refresh_vacancy_data.sql` to create the loading procedure
4. Manually insert data into `ProjectDB.staging_vacancy` using INSERT statements following the format given in example_insert.sql
5. Run CALL ProjectDB.refresh_vacancy_data(). This will populate all normalized tables and make the data available to the app.
