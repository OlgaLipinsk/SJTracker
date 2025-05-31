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
