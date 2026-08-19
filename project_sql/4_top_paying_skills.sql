/*Answer: What are the top skills based on salary?
- Look at the average salary associated with each skill for Data Analyst positions
- Focuses on roles with specified salaries, regardless of location
- Why? It reveals how different skills impact salary levels for Data Analysts and helps identify
  the most financially rewarding skills to acquire or improve*/

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

/*
INSIGHT SUMMARY: top-paying skills for Data Analysts
(salary-disclosing postings only; skills with >= 25 postings; n = 25 skills, 2,013 skill-postings)

Skill groups represented:
- Distributed processing:  kafka, spark, pyspark, hadoop, scala, databricks
- Cloud data platforms:    gcp, snowflake, redshift, databricks
- Databases:               mongodb, nosql, db2, postgresql
- Pipeline orchestration:  airflow
- Systems / shell:         linux, unix, shell
- Engineering workflow:    git, jira, confluence
- Python analysis stack:   pandas, numpy, plotly
- General programming:     php, express

1. The pay range is narrow. 106,603 (plotly) to 129,999 (kafka), a 22% spread,
   median 111,496. Among skills with real hiring volume, which one you hold
   moves the average salary by a modest amount.

2. The list is data engineering, not analysis. Distributed processing, cloud
   platforms, databases, and orchestration account for roughly two thirds of it.
   The best-paid Data Analyst postings are ones that also own data pipelines.

3. Streaming leads. kafka tops the list at 129,999, about 12% above the second
   entry (airflow, 116,387), and is the only skill separated from the pack.
   Everything from rank 2 to 25 sits within a 9% band.

4. Demand and pay are unrelated inside this list. Spearman rank correlation
   between average salary and posting count is 0.065. snowflake (241 postings,
   111,578) and unix (37 postings, 111,123) pay the same.

5. sql, excel, tableau, power bi, and python are absent. All clear the 25-posting
   minimum by a wide margin, so each averages below 106,603. They are hiring
   requirements, not pay drivers.

6. Workflow tools pay above the list median. git (112,250), confluence (114,153),
   jira (107,931). These are not analysis capabilities; they mark teams that run
   analytics with engineering process, which is what the salary reflects.

*/
