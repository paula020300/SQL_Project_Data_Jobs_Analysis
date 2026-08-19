/*
Question: What are the most in-demand skills for data analysts?
- Why? Retrieves the top 5 skills with the highest demand in the job market,
  providing insights into the most valuable skills for job seekers.
*/

SELECT sd.skill_id, sd.skills, COUNT(jpf.job_id) AS job_count 
FROM skills_dim AS sd
INNER JOIN skills_job_dim AS sjd ON sjd.skill_id = sd.skill_id
INNER JOIN job_postings_fact AS jpf ON jpf.job_id = sjd.job_id
WHERE jpf.job_title_short = 'Data Analyst'
GROUP BY sd.skills, sd.skill_id
ORDER BY job_count DESC
LIMIT 5