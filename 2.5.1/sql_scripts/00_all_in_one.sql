\set ON_ERROR_STOP on
\echo ==== STEP 1. Drop & create database ====
DROP DATABASE IF EXISTS mil_training_db;
CREATE DATABASE mil_training_db;

\echo ==== STEP 2. Connect to mil_training_db ====
\c mil_training_db

\echo ==== STEP 3. Create schema ====
-- Drop in right order
DROP TABLE IF EXISTS Training_Personnel CASCADE;
DROP TABLE IF EXISTS Training_Programs CASCADE;

CREATE TABLE Training_Programs (
  Training_Program_ID SERIAL PRIMARY KEY,
  Program_Name        VARCHAR(100) NOT NULL,
  Instructor          VARCHAR(100) NOT NULL,
  Start_Date          DATE NOT NULL,
  End_Date            DATE NOT NULL,
  CONSTRAINT chk_dates CHECK (End_Date >= Start_Date)
);

CREATE TABLE Training_Personnel (
  ID                   SERIAL PRIMARY KEY,
  Name                 VARCHAR(100) NOT NULL,
  "Rank"               VARCHAR(50)  NOT NULL,
  Training_Program_ID  INT REFERENCES Training_Programs(Training_Program_ID) ON DELETE SET NULL,
  Date_Enrolled        DATE NOT NULL
);

CREATE INDEX idx_training_personnel_program_id ON Training_Personnel(Training_Program_ID);
CREATE INDEX idx_training_personnel_rank ON Training_Personnel("Rank");

\echo ==== STEP 4. Import CSV data (run from project root 2.5.1) ====
\encoding UTF8

-- Import programs
\copy Training_Programs(Training_Program_ID,Program_Name,Instructor,Start_Date,End_Date)
FROM 'data/training_programs.csv' WITH (FORMAT csv, HEADER true);

-- Import personnel
\copy Training_Personnel(ID,Name,"Rank",Training_Program_ID,Date_Enrolled)
FROM 'data/training_personnel.csv' WITH (FORMAT csv, HEADER true);

-- Sync sequences to the max IDs from CSV
SELECT setval(pg_get_serial_sequence('Training_Programs','Training_Program_ID'),
              COALESCE((SELECT MAX(Training_Program_ID) FROM Training_Programs), 0), true);
SELECT setval(pg_get_serial_sequence('Training_Personnel','ID'),
              COALESCE((SELECT MAX(ID) FROM Training_Personnel), 0), true);

\echo ==== STEP 5. Quick sanity checks ====
SELECT 'Programs count' AS label, COUNT(*) AS value FROM Training_Programs;
SELECT 'Personnel count' AS label, COUNT(*) AS value FROM Training_Personnel;

\echo ==== STEP 6. Export results of 20 queries to CSV (results/*.csv) ====

-- 01
\copy (SELECT * FROM Training_Personnel) TO 'results/01_all_personnel.csv' WITH (FORMAT csv, HEADER true);

-- 02
\copy (SELECT * FROM Training_Programs) TO 'results/02_all_programs.csv' WITH (FORMAT csv, HEADER true);

-- 03
\copy (
  SELECT p.ID, p.Name, p."Rank", pr.Program_Name, p.Date_Enrolled
  FROM Training_Personnel p
  LEFT JOIN Training_Programs pr ON pr.Training_Program_ID = p.Training_Program_ID
) TO 'results/03_personnel_with_programs.csv' WITH (FORMAT csv, HEADER true);

-- 04
\copy (
  SELECT pr.Training_Program_ID, pr.Program_Name, COUNT(p.ID) AS personnel_count
  FROM Training_Programs pr
  LEFT JOIN Training_Personnel p ON p.Training_Program_ID = pr.Training_Program_ID
  GROUP BY pr.Training_Program_ID, pr.Program_Name
  ORDER BY personnel_count DESC, pr.Training_Program_ID
) TO 'results/04_count_per_program.csv' WITH (FORMAT csv, HEADER true);

-- 05
\copy (
  SELECT pr.Program_Name, COUNT(p.ID) AS cnt
  FROM Training_Programs pr
  LEFT JOIN Training_Personnel p ON p.Training_Program_ID = pr.Training_Program_ID
  GROUP BY pr.Program_Name
  HAVING COUNT(p.ID) > 3
) TO 'results/05_programs_more_than_3.csv' WITH (FORMAT csv, HEADER true);

-- 06
\copy (
  SELECT * FROM Training_Personnel
  WHERE Date_Enrolled > DATE '2025-10-01'
  ORDER BY Date_Enrolled
) TO 'results/06_enrolled_after_2025-10-01.csv' WITH (FORMAT csv, HEADER true);

-- 07
\copy (
  SELECT * FROM Training_Personnel
  WHERE Name ILIKE '%тен%'
) TO 'results/07_search_name_contains_ten.csv' WITH (FORMAT csv, HEADER true);

-- 08
\copy (
  SELECT *
  FROM Training_Programs
  WHERE Start_Date <= CURRENT_DATE AND End_Date >= CURRENT_DATE
  ORDER BY Start_Date
) TO 'results/08_active_today.csv' WITH (FORMAT csv, HEADER true);

-- 09
\copy (
  SELECT *
  FROM Training_Programs
  WHERE Start_Date > CURRENT_DATE
  ORDER BY Start_Date
) TO 'results/09_future_programs.csv' WITH (FORMAT csv, HEADER true);

-- 10
\copy (
  SELECT *
  FROM Training_Programs
  WHERE End_Date < CURRENT_DATE
  ORDER BY End_Date DESC
) TO 'results/10_past_programs.csv' WITH (FORMAT csv, HEADER true);

-- 11
\copy (
  SELECT Training_Program_ID, Program_Name,
         (End_Date - Start_Date + 1) AS duration_days
  FROM Training_Programs
  ORDER BY duration_days DESC, Training_Program_ID
) TO 'results/11_program_durations.csv' WITH (FORMAT csv, HEADER true);

-- 12
\copy (
  SELECT "Rank", COUNT(*) AS cnt
  FROM Training_Personnel
  GROUP BY "Rank"
  ORDER BY cnt DESC, "Rank"
) TO 'results/12_rank_distribution.csv' WITH (FORMAT csv, HEADER true);

-- 13
\copy (
  SELECT pr.Program_Name,
         MIN(p.Date_Enrolled) AS first_enrolled,
         MAX(p.Date_Enrolled) AS last_enrolled
  FROM Training_Programs pr
  LEFT JOIN Training_Personnel p ON p.Training_Program_ID = pr.Training_Program_ID
  GROUP BY pr.Program_Name
  ORDER BY pr.Program_Name
) TO 'results/13_enroll_min_max_by_program.csv' WITH (FORMAT csv, HEADER true);

-- 14
\copy (
  WITH cnt AS (
    SELECT pr.Training_Program_ID, pr.Program_Name, COUNT(p.ID) AS c
    FROM Training_Programs pr
    LEFT JOIN Training_Personnel p ON p.Training_Program_ID = pr.Training_Program_ID
    GROUP BY pr.Training_Program_ID, pr.Program_Name
  )
  SELECT Program_Name, c,
         RANK() OVER (ORDER BY c DESC) AS popularity_rank
  FROM cnt
  ORDER BY popularity_rank, Program_Name
) TO 'results/14_program_popularity_rank.csv' WITH (FORMAT csv, HEADER true);

-- 15
\copy (
  SELECT pr.Program_Name, p.Name, p.Date_Enrolled,
         ROW_NUMBER() OVER (PARTITION BY pr.Training_Program_ID ORDER BY p.Date_Enrolled, p.ID) AS row_in_program
  FROM Training_Personnel p
  JOIN Training_Programs pr ON pr.Training_Program_ID = p.Training_Program_ID
  ORDER BY pr.Program_Name, row_in_program
) TO 'results/15_row_number_in_program.csv' WITH (FORMAT csv, HEADER true);

-- 16
\copy (
  SELECT * FROM Training_Personnel
  WHERE Training_Program_ID IS NULL
) TO 'results/16_without_program.csv' WITH (FORMAT csv, HEADER true);

-- 17
\copy (
  SELECT Program_Name,
         (Start_Date - CURRENT_DATE) AS days_until_start,
         (CURRENT_DATE - End_Date) AS days_after_end
  FROM Training_Programs
  ORDER BY Program_Name
) TO 'results/17_days_until_start_after_end.csv' WITH (FORMAT csv, HEADER true);

-- 18
\copy (
  SELECT p.Name, pr.Program_Name,
         (pr.Start_Date - p.Date_Enrolled) AS days_between_enroll_and_start
  FROM Training_Personnel p
  JOIN Training_Programs pr ON pr.Training_Program_ID = p.Training_Program_ID
  ORDER BY days_between_enroll_and_start DESC, p.Name
) TO 'results/18_days_between_enroll_and_start.csv' WITH (FORMAT csv, HEADER true);

-- 19
\copy (
  SELECT pr.Program_Name, COUNT(p.ID) AS cnt
  FROM Training_Programs pr
  LEFT JOIN Training_Personnel p ON p.Training_Program_ID = pr.Training_Program_ID
  GROUP BY pr.Program_Name
  ORDER BY cnt DESC, pr.Program_Name
  LIMIT 3
) TO 'results/19_top3_by_count.csv' WITH (FORMAT csv, HEADER true);

-- 20
\copy (
  SELECT pr.Program_Name,
         COUNT(*) FILTER (WHERE p."Rank" ILIKE '%лейтенант%' OR p."Rank" ILIKE '%капітан%' OR p."Rank" ILIKE '%майор%') AS officers,
         COUNT(*) FILTER (WHERE p."Rank" ILIKE '%сержант%') AS sergeants,
         COUNT(*) FILTER (WHERE p."Rank" ILIKE '%солдат%') AS privates
  FROM Training_Programs pr
  LEFT JOIN Training_Personnel p ON p.Training_Program_ID = pr.Training_Program_ID
  GROUP BY pr.Program_Name
  ORDER BY pr.Program_Name
) TO 'results/20_aggregate_roles_per_program.csv' WITH (FORMAT csv, HEADER true);

\echo ==== DONE. CSVs saved in results/ ====
