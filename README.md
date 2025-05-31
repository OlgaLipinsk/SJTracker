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

## How to Run the App Locally

1. Clone the repository:

   git clone https://github.com/OlgaLipinsk/SJTracker.git  
   cd SJTracker

2. Install Python dependencies:

   pip install -r requirements.txt

3. Initialize the database:

   Run the following SQL scripts in your SQL environment (e.g., BigQuery):

   - create_tables.sql — defines the schema  
   - refresh_vacancy_data.sql — loads and links data via a stored procedure

   Example:
   CALL ProjectDB.refresh_vacancy_data();

4. Run the app:

   streamlit run streamlit_app.py

## Documentation

- The database model is described in ER_Diagram.pdf
- SQL operations are used throughout (including SELECT queries)
- A stored procedure is used for structured data ingestion from a staging table

## Project Files

- streamlit_app.py — Main Streamlit frontend that displays job data and interacts with the database
- create_tables.sql — SQL script that creates the normalized database schema
- refresh_vacancy_data.sql — SQL script that defines and runs the stored procedure to populate the schema
- requirements.txt — Python dependencies needed to run the app
- ER_Diagram.pdf — Entity-Relationship diagram showing database structure
- .gitignore — Excludes files from version control
- README.md — Project documentation and usage instructions

