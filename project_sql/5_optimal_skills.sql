/*
Answer: What are the most optimal skills to learn (aka it's in high demand and a high-paying skill)?
- Why? Targets skills that offer job security (high demand) and financial benefits (high salaries),
  offering strategic insights for career development in data analysis
*/


SELECT sd.skills,
        COUNT(jpf.job_id) AS demand_count,
        ROUND(AVG(jpf.salary_year_avg),0) AS avg_salary_per_skill  
FROM skills_dim AS sd
INNER JOIN skills_job_dim AS sjd ON sjd.skill_id = sd.skill_id
INNER JOIN job_postings_fact AS jpf ON jpf.job_id = sjd.job_id
WHERE jpf.job_title_short = 'Data Analyst'
        AND jpf.salary_year_avg IS NOT NULL
GROUP BY sd.skills
HAVING COUNT(jpf.job_id) >=30
ORDER BY avg_salary_per_skill DESC, demand_count DESC;

SELECT sd.skills,
        COUNT(jpf.job_id) AS demand_count,
        ROUND(AVG(jpf.salary_year_avg),0) AS avg_salary_per_skill  
FROM skills_dim AS sd
INNER JOIN skills_job_dim AS sjd ON sjd.skill_id = sd.skill_id
INNER JOIN job_postings_fact AS jpf ON jpf.job_id = sjd.job_id
WHERE jpf.job_title_short = 'Data Analyst'
        AND jpf.salary_year_avg IS NOT NULL
GROUP BY sd.skills
HAVING COUNT(jpf.job_id) >=30
ORDER BY demand_count DESC, avg_salary_per_skill DESC