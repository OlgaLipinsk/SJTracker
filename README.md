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
- create_tables.sql — SQL script that creates the normalized database schema
- refresh_vacancy_data.sql — SQL script that defines and runs the stored procedure to populate the schema
- requirements.txt — Python dependencies needed to run the app
- ER_Diagram.pdf — Entity-Relationship diagram showing database structure
- .gitignore — Excludes files from version control
- README.md — Project documentation and usage instructions

## Adapting the Project to Your Own GCP Setup

This project is configured to use Google BigQuery with the following hardcoded identifiers:

- Project ID: `leafy-sanctuary-458206-f8`
- Dataset: `ProjectDB`

These values appear in the SQL scripts (`create_tables.sql`, `refresh_vacancy_data.sql`), where fully qualified table names are used (e.g., `leafy-sanctuary-458206-f8.ProjectDB.skill`).

The Streamlit app is also configured to connect to this specific GCP project via service account credentials loaded from Streamlit secrets.

To Deploy the App with Your Own GCP Project you need to:

1. **Create a BigQuery Dataset**

   In your Google Cloud project (e.g., `my-own-project-id`), create a dataset named `ProjectDB`, or choose your own name.

2. **Update SQL Scripts**

   Replace all references to the original project.

3. **Create and Configure a Service Account**

- In your GCP project, create a service account with BigQuery Admin or appropriate permissions.
- Download the service account key as a JSON file.

4. **Update Streamlit Secrets**

Add your service account credentials to `.streamlit/secrets.toml`

