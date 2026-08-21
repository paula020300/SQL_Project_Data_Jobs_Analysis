/*
Question: What skills are required for the top-paying data analyst jobs?
- Why? It provides a detailed look at which high-paying jobs demand certain skills, helping job seekers understand which skills to develop that align with top salaries
*/

WITH top_paying_jobs 
    AS(SELECT job_id,
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