/* 
Question: What are the top-paying data analyst jobs?
- Why? Highlight the top-paying opportunities for Data Analysts, offering insights
*/

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
