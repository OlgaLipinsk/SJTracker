-- skill
DROP TABLE IF EXISTS `ProjectDB.skill`;
CREATE TABLE `ProjectDB.skill`
(
  skill_id STRING NOT NULL,
  skill_name STRING,
  category STRING
);

-- keyword
DROP TABLE IF EXISTS `ProjectDB.keyword`;
CREATE TABLE `ProjectDB.keyword`
(
  keyword_id STRING NOT NULL,
  word STRING
);

-- vacancy_keyword
DROP TABLE IF EXISTS `ProjectDB.vacancy_keyword`;
CREATE TABLE `ProjectDB.vacancy_keyword`
(
  vacancy_id STRING NOT NULL,
  keyword_id STRING NOT NULL
);

-- vacancy_location
DROP TABLE IF EXISTS `ProjectDB.vacancy_location`;
CREATE TABLE `ProjectDB.vacancy_location`
(
  vacancy_id STRING NOT NULL,
  location_id STRING NOT NULL
);

-- contact
DROP TABLE IF EXISTS `ProjectDB.contact`;
CREATE TABLE `ProjectDB.contact`
(
  contact_id STRING NOT NULL,
  name STRING,
  email STRING,
  phone STRING
);

-- vacancy_contact
DROP TABLE IF EXISTS `ProjectDB.vacancy_contact`;
CREATE TABLE `ProjectDB.vacancy_contact`
(
  vacancy_id STRING NOT NULL,
  contact_id STRING NOT NULL
);

-- location
DROP TABLE IF EXISTS `ProjectDB.location`;
CREATE TABLE `ProjectDB.location`
(
  location_id STRING NOT NULL,
  postcode STRING,
  kommune STRING
);

-- vacancy_skill
DROP TABLE IF EXISTS `ProjectDB.vacancy_skill`;
CREATE TABLE `ProjectDB.vacancy_skill`
(
  vacancy_id STRING NOT NULL,
  skill_id STRING NOT NULL
);

-- employer
DROP TABLE IF EXISTS `ProjectDB.employer`;
CREATE TABLE `ProjectDB.employer`
(
  employer_id STRING NOT NULL,
  name STRING,
  industry STRING
);

-- vacancy
DROP TABLE IF EXISTS `ProjectDB.vacancy`;
CREATE TABLE `ProjectDB.vacancy`
(
  vacancy_id STRING NOT NULL,
  title STRING,
  text STRING,
  type STRING,
  deadline DATE,
  url STRING,
  employer_id STRING
);

-- staging_vacancy
DROP TABLE IF EXISTS `ProjectDB.staging_vacancy`;
CREATE TABLE `ProjectDB.staging_vacancy`
(
  title STRING,
  text STRING,
  type STRING,
  deadline DATE,
  url STRING,
  employer_name STRING,
  skill_list ARRAY<STRING>,
  keyword_list ARRAY<STRING>,
  contact_name STRING,
  contact_email STRING,
  contact_phone STRING,
  location_postcode STRING,
  location_kommune STRING
);
