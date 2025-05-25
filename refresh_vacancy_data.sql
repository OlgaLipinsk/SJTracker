CREATE OR REPLACE PROCEDURE `leafy-sanctuary-458206-f8.ProjectDB.refresh_vacancy_data`()
BEGIN

  -- Insert employers
  MERGE ProjectDB.employer AS T
  USING (
    SELECT DISTINCT employer_name AS name, 'Unknown' AS industry
    FROM ProjectDB.staging_vacancy
    WHERE employer_name IS NOT NULL
  ) AS S
  ON T.name = S.name
  WHEN NOT MATCHED THEN
    INSERT (employer_id, name, industry) VALUES (GENERATE_UUID(), S.name, S.industry);

  -- Insert contacts
  MERGE ProjectDB.contact AS T
  USING (
    SELECT DISTINCT contact_name AS name, contact_email AS email, contact_phone AS phone
    FROM ProjectDB.staging_vacancy
    WHERE contact_email IS NOT NULL
  ) AS S
  ON T.email = S.email
  WHEN NOT MATCHED THEN
    INSERT (contact_id, name, email, phone) VALUES (GENERATE_UUID(), S.name, S.email, S.phone);

  -- Insert locations
  MERGE ProjectDB.location AS T
  USING (
    SELECT DISTINCT location_postcode AS postcode, location_kommune AS kommune
    FROM ProjectDB.staging_vacancy
    WHERE location_postcode IS NOT NULL AND location_kommune IS NOT NULL
  ) AS S
  ON (T.postcode = S.postcode AND T.kommune = S.kommune)
  WHEN NOT MATCHED THEN
    INSERT (location_id, postcode, kommune) VALUES (GENERATE_UUID(), S.postcode, S.kommune);

  -- Insert skills
  MERGE ProjectDB.skill AS T
  USING (
    SELECT DISTINCT skill AS skill_name, 'Unknown' AS category
    FROM ProjectDB.staging_vacancy, UNNEST(skill_list) AS skill
    WHERE skill IS NOT NULL
  ) AS S
  ON T.skill_name = S.skill_name
  WHEN NOT MATCHED THEN
    INSERT (skill_id, skill_name, category) VALUES (GENERATE_UUID(), S.skill_name, S.category);

  -- Insert keywords
  MERGE ProjectDB.keyword AS T
  USING (
    SELECT DISTINCT keyword AS word
    FROM ProjectDB.staging_vacancy, UNNEST(keyword_list) AS keyword
    WHERE keyword IS NOT NULL
  ) AS S
  ON T.word = S.word
  WHEN NOT MATCHED THEN
    INSERT (keyword_id, word) VALUES (GENERATE_UUID(), S.word);

  -- Insert vacancies with MERGE (no duplicates)
  MERGE ProjectDB.vacancy AS T
  USING (
    SELECT DISTINCT
      v.title,
      v.text,
      v.type,
      v.deadline,
      v.url,
      e.employer_id
    FROM ProjectDB.staging_vacancy v
    JOIN ProjectDB.employer e ON v.employer_name = e.name
  ) AS S
  ON T.title = S.title AND T.url = S.url
  WHEN NOT MATCHED THEN
    INSERT (vacancy_id, title, text, type, deadline, url, employer_id)
    VALUES (GENERATE_UUID(), S.title, S.text, S.type, S.deadline, S.url, S.employer_id);

  -- Insert into vacancy_skill
  INSERT INTO ProjectDB.vacancy_skill (vacancy_id, skill_id)
  SELECT
    vac.vacancy_id,
    s.skill_id
  FROM
    ProjectDB.staging_vacancy v
  JOIN
    ProjectDB.vacancy vac ON v.title = vac.title AND v.url = vac.url
  JOIN
    UNNEST(v.skill_list) AS skill_name
  JOIN
    ProjectDB.skill s ON s.skill_name = skill_name;

  -- Insert into vacancy_keyword
  INSERT INTO ProjectDB.vacancy_keyword (vacancy_id, keyword_id)
  SELECT
    vac.vacancy_id,
    k.keyword_id
  FROM
    ProjectDB.staging_vacancy v
  JOIN
    ProjectDB.vacancy vac ON v.title = vac.title AND v.url = vac.url
  JOIN
    UNNEST(v.keyword_list) AS keyword
  JOIN
    ProjectDB.keyword k ON k.word = keyword;

  -- Insert into vacancy_contact
  INSERT INTO ProjectDB.vacancy_contact (vacancy_id, contact_id)
  SELECT
    vac.vacancy_id,
    c.contact_id
  FROM
    ProjectDB.staging_vacancy v
  JOIN
    ProjectDB.vacancy vac ON v.title = vac.title AND v.url = vac.url
  JOIN
    ProjectDB.contact c ON v.contact_email = c.email;

  -- Insert into vacancy_location
  INSERT INTO ProjectDB.vacancy_location (vacancy_id, location_id)
  SELECT
    vac.vacancy_id,
    l.location_id
  FROM
    ProjectDB.staging_vacancy v
  JOIN
    ProjectDB.vacancy vac ON v.title = vac.title AND v.url = vac.url
  JOIN
    ProjectDB.location l ON v.location_postcode = l.postcode AND v.location_kommune = l.kommune;

END;