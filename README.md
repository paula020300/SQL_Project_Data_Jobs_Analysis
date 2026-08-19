# Data Analyst Job Market: A SQL Analysis

## Introduction

This project examines the 2023 job posting market for Data Analyst roles: which
postings have higher salaries and which skills are demanded in those postings, which skills are most
in demand, which pay best, and which combine both.

The dataset comes from [Luke Barousse's SQL for Data Analytics course](https://github.com/lukebarousse/SQL_Project_Data_Job_Analysis),
which collects job postings scraped from Google's job search results. The SQL in
this repository, the analysis, and the charts are my own work.

SQL queries: [project_sql/](project_sql/)

## Background

The data is loaded into a local PostgreSQL database as four tables:

| Table | Contents |
|---|---|
| `job_postings_fact` | one row per posting: title, salary, location, remote working availability |
| `company_dim` | company names |
| `skills_dim` | one row per skill: `skill_id`, name, type |
| `skills_job_dim` | bridge table: one row per (posting, skill) pair |

### Five questions, one query file each:

1. What are the top-paying Data Analyst postings?
2. What skills do those top-paying postings require?
3. Which skills are most in demand for Data Analysts?
4. Which skills are associated with the highest average salaries?
5. Which skills are both in demand and well paid?

**Scope note.** Questions 4 and 5 restrict to postings that disclose a salary,
because an average salary cannot be computed otherwise. That is a small and
self-selected subset of all postings, so the counts in those queries are much
lower than the raw demand figures in question 3. No query filters by location.

## Tools I Used

- **PostgreSQL 18** running locally (in pgAdmin 4), as the database engine for every query.
- **VS Code** for writing and executing SQL, connected to the local database
  through the SQLTools extension.
- **Python** (matplotlib, pandas) for the charts, in a virtual environment in this
  repository. See [charts/make_charts.py](charts/make_charts.py).
- **Git and GitHub** for version control and publishing.

## The Analysis

### 1. Top-paying Data Analyst postings

Filtered to `Data Analyst` postings with a disclosed salary only and took the ten
highest.

```sql
SELECT job_id,
        job_title,
        salary_year_avg,
        name AS company_name
FROM job_postings_fact as jpf
LEFT JOIN company_dim as cd ON jpf.company_id = cd.company_id
WHERE salary_year_avg IS NOT NULL
        AND job_title_short = 'Data Analyst'
ORDER BY salary_year_avg DESC
LIMIT 10
```

![Top 10 highest-paying Data Analyst postings](assets/01_top_paying_jobs.png)

- The range is wide: $285,000 to $650,000.
- Titles are mostly senior or leadership: Director, Head of, Principal, Senior.
  "Data Analyst" as a plain title without seniority level occurs only twice.
- The top entry from Mantys is suspiciously high ($250,000 higher than the next posting). The second, "Data base administrator", is a database administration
  role that the `job_title_short` classifier has grouped wrongly under Data Analyst.

### 2. Skills required by the top-paying postings

Reused query 1 as a CTE, then joined through the bridge table to get each posting's
skills.

```sql
WITH top_paying_jobs AS (
    SELECT job_id,
        job_title,
        salary_year_avg,
        name AS company_name
    FROM job_postings_fact as jpf
    LEFT JOIN company_dim as cd ON jpf.company_id = cd.company_id
    WHERE salary_year_avg IS NOT NULL
        AND job_title_short = 'Data Analyst'
    ORDER BY salary_year_avg DESC
    LIMIT 10)

SELECT tpj.*, sd.skills
FROM top_paying_jobs AS tpj
INNER JOIN skills_job_dim AS sjd ON tpj.job_id = sjd.job_id
INNER JOIN skills_dim AS sd ON sjd.skill_id = sd.skill_id
ORDER BY tpj.salary_year_avg DESC
```
### Results:
| Skill | Postings (of 7) |
|---|---|
| python | 4 |
| sql | 3 |
| r | 3 |
| excel | 3 |
| tableau | 3 |
| power bi | 2 |

- The `INNER JOIN` reduces ten postings to **seven**. Three of the top ten list no
  skills at all.
- Python leads at 4 of 7 postings; SQL, R, Excel, and Tableau each appear in 3.

### 3. Most in-demand skills

Counted postings per skill across all Data Analyst postings, with no salary filter, and picked the top 5.

```sql
SELECT sd.skill_id, sd.skills, COUNT(jpf.job_id) AS job_count
FROM skills_dim AS sd
INNER JOIN skills_job_dim AS sjd ON sjd.skill_id = sd.skill_id
INNER JOIN job_postings_fact AS jpf ON jpf.job_id = sjd.job_id
WHERE jpf.job_title_short = 'Data Analyst'
GROUP BY sd.skills, sd.skill_id
ORDER BY job_count DESC
LIMIT 5
```

![Top 5 most in-demand Data Analyst skills](assets/03_top_demanded_skills.png)

- SQL is required by 92,628 postings, 38% more than the second skill.
- The top five split into two groups: two languages (SQL, Python), one
  spreadsheet tool (Excel), and two BI tools (Tableau, Power BI).

### 4. Skills associated with the highest salaries

Average salary per skill, restricted to postings with a disclosed salary. I added
`HAVING COUNT(*) >= 25` and a visible posting count for clarity. Without a defined job count minimum, the top of this ranking was crowded with non-representative skills.

```sql
SELECT sd.skills,
    ROUND(AVG(salary_year_avg),0) AS avg_salary_per_skill,
    COUNT(*) AS postings_count
FROM skills_dim AS sd
INNER JOIN skills_job_dim AS sjd ON sd.skill_id = sjd.skill_id
INNER JOIN job_postings_fact AS jpf ON jpf.job_id = sjd.job_id
WHERE jpf.job_title_short = 'Data Analyst'
    AND salary_year_avg IS NOT NULL
GROUP BY sd.skills
HAVING COUNT(*) >= 25
ORDER BY avg_salary_per_skill DESC
LIMIT 25
```

![Top 25 highest-paying Data Analyst skills](assets/04_top_paying_skills.png)

- The spread is narrow: $106,603 to $129,999, about 22% from bottom to top, with
  Kafka the only skill clearly separated from the rest. Ranks 2 to 25 sit within a
  9% band.
- The list is data engineering, not analysis. Distributed processing (Kafka,
  Spark, PySpark, Hadoop, Scala, Databricks), cloud platforms (GCP, Snowflake,
  Redshift), databases (MongoDB, NoSQL, DB2, PostgreSQL), and orchestration
  (Airflow) make up roughly two thirds of it.
- Engineering workflow tools appear: Git, Confluence, Jira. These are not analysis
  capabilities. They mark teams that run analytics with engineering process, which
  is what the salary reflects.
- None of the five skills from query 3 appear here. Each clears the 25-posting
  minimum comfortably, so each averages below $106,603.

### 5. Skills that are both in demand and well paid

Demand and salary come from the same grouped row set, so one `GROUP BY` produces
both needed information pieces. A minimum of 30 postings was used as a filter.

```sql
SELECT sd.skills,
        COUNT(jpf.job_id) AS demand_count,
        ROUND(AVG(jpf.salary_year_avg),0) AS avg_salary_per_skill
FROM skills_dim AS sd
INNER JOIN skills_job_dim AS sjd ON sjd.skill_id = sd.skill_id
INNER JOIN job_postings_fact AS jpf ON jpf.job_id = sjd.job_id
WHERE jpf.job_title_short = 'Data Analyst'
        AND jpf.salary_year_avg IS NOT NULL
GROUP BY sd.skills
HAVING COUNT(jpf.job_id) >= 30
ORDER BY avg_salary_per_skill DESC, demand_count DESC
```

The same query sorted by the other measure first:

```sql
SELECT sd.skills,
        COUNT(jpf.job_id) AS demand_count,
        ROUND(AVG(jpf.salary_year_avg),0) AS avg_salary_per_skill
FROM skills_dim AS sd
INNER JOIN skills_job_dim AS sjd ON sjd.skill_id = sd.skill_id
INNER JOIN job_postings_fact AS jpf ON jpf.job_id = sjd.job_id
WHERE jpf.job_title_short = 'Data Analyst'
        AND jpf.salary_year_avg IS NOT NULL
GROUP BY sd.skills
HAVING COUNT(jpf.job_id) >= 30
ORDER BY demand_count DESC, avg_salary_per_skill DESC
```

Below are the top ten by each order group, either demand or best salary.

![Most in demand and best paid Data Analyst skills](assets/05_optimal_skills.png)

- **The two lists have no skill in common.** Nothing in the ten most demanded
  skills appears among the ten best paid, and the reverse.
- SQL has 3,083 postings and averages $96,435. Kafka has 40 postings and averages $129,999.
- More postings generally mean lower average pay, because they describe the minimal requirements for the job.
- The best-paid jobs demand more specialized and unique skills, not typical for standard Data Analyst offers, thus rewarding with a higher salary.

## What I Learned

**Clause order is very important.** The order is always as follows: `SELECT`, `FROM`, `JOIN`, `WHERE`, `GROUP BY`,
`HAVING`, `ORDER BY`, `LIMIT`. `HAVING` cannot appear before `GROUP BY`, because it filters the grouping results.

**`COUNT(*)` and `COUNT(column)` are not interchangeable.** `COUNT(column)` skips
NULLs. It must be always thought through if the potential NULLs should be counted in. On an inner join key that makes no difference, since the join already
removes the NULLs.


## Conclusions

1. **The most demanded skills and the best-paid skills are two different data sets and don't have much in common.**
   SQL, Excel, Python, Tableau, and Power BI top the demand ranking and none of
   them reaches the top 25 by salary. They can be seen as minimum requirement for the job postings.
2. **The best-paid skills belong to the data engineering skill-set.** Distributed processing,
   cloud platforms, orchestration, and the surrounding workflow tools dominate the
   top-paying list. The best-paid Data Analyst postings are ones that also expect
   data pipeline tasks.
3. **SQL is the biggest entry requirement.** 92,628 postings ask
   for it, more than any other skill, and its average of $96,435 sits below the
   median of the skills examined.
4. **No high-demand skill after SQL leads in the salary.** Among skills with genuine hiring volume,
   the full range of average salaries is about 22%. They don't belong to the skills which offer a salary lever.
5. **Snowflake, Spark, and Databricks are the strongest middle**, each
   above $111,000 with 100 or more postings. These are useful skills to learn to boost the salary range and have a good chance for acquiring a position.

### Limitations

- `skills_dim` contains a few duplicate skill names under different `skill_id`
  values, so grouping by `skill_id` and grouping by name give slightly different
  results. These queries group by name.
- Results are sensitive to the minimum-posting thresholds (25 and 30). Different
  thresholds reorder the tail.

## Reproducing the charts

The charts are generated from the query results committed in
[charts/data/](charts/data/), so they can be rebuilt without a database
connection.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows
# .venv/bin/python -m pip install -r requirements.txt     # macOS / Linux

.venv/Scripts/python charts/make_charts.py
```

PNGs are written to [assets/](assets/).
