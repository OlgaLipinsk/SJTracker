INSERT INTO ProjectDB.staging_vacancy (
  title, text, type, deadline, url,
  employer_name, skill_list, keyword_list,
  contact_name, contact_email, contact_phone,
  location_postcode, location_kommune
)
VALUES (
  'Student Helper for Core Analytics Services',
  'Join a dynamic team of software engineers and quantitative analysts in Copenhagen. You will help develop and maintain advanced .NET analytics services supporting trading and financial operations. The role includes collaborating with business partners, maintaining cloud infrastructure using Terraform, and working in an agile environment with modern tech stacks like .NET and Cloud technologies.',
  'Student Assistant',
  DATE('2025-06-12'),
  'https://ejqi.fa.ocs.oraclecloud.eu/hcmUI/CandidateExperience/en/sites/CX_1001/jobs?keyword=Student+Helper+for+Core+Analytics+Services&lastSelectedFacet=LOCATIONS&mode=location&selectedLocationsFacet=300000000294904', 
  'Danske Bank',
  [
    '.NET Development', 'Cloud Infrastructure', 'Terraform',
    'Business Understanding', 'Agile Workflow', 'Collaboration Skills',
    'Attention to Detail', 'English Communication'
  ],
  [
    'Core Analytics', 'Software Development', 'Cloud Computing',
    'Student Job', 'IT Services', 'Danske Bank'
  ],
  'Kenneth Lindgaard Kristensen',
  'kkr@danskebank.dk',
  '+45 26 34 37 33',
  '1577',
  'København'
);
