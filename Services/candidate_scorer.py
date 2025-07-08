import json
from typing import Dict
import re
 
class Candidate:
   @staticmethod
   def analyze_candidate(qa_chain, query: str, candidate_name: str, resume_text: str) -> Dict[str, float]:
        """Analyze a single candidate and return a matching score."""

        qa_template = f"""
You are an AI resume evaluator specialized in scoring candidates against job descriptions (JD) on a scale of 0-100 points, broken down into categories.  
Use the job description provided and the candidate profile details you have to generate scores and detailed explanations.

Scoring Categories (Total 100 points):


1. Mandatory Skills (0-50 points):
Eveluate only the mandatory technical skills.
Your task is to evaluate only the **technical Mandatory Skills** section of a candidate’s resume based on the technical skills explicitly mentioned in the Job Description (JD).

Focus:  
- Only include **technical, hands-on skills** directly required by the JD.  
- Exclude soft skills, domain-level phrases, or behavioral traits (e.g., communication, collaboration, team player).
- If the JD includes compound phrases like “implement standard workflows (e.g., Risk Assessment; Risk validation; Request Response...)”, treat the entire phrase as **one technical skill**, not multiple.

Scoring Logic:
Let N = number of **technical mandatory skills** extracted from the JD.  
Each skill carries equal weight:  
Weight per skill = 50 / N

- If the candidate **clearly mentions** a JD skill → award full weight.
- If the skill is **missing or unrelated** → award 0.
- Do not award partial scores for similar or vaguely related terms.
- Do not count “learning,” “awareness,” or “interest in” as valid skill mentions.

No Rounding Rule:
**Do not round** the final score.  
Use the actual value of the calculation:  
**score = (matched_skills_count / total_skills) * 50**, formatted with two decimal places.  
The number shown in `Mandatory Skills: X/50` must **exactly match** the value in the `calculation` field.

Matching Rules:
- Count only directly mentioned skills in the resume.
- Count synonyms only when context strongly matches (e.g., "Google Cloud" = Cloud, "Snowflake SQL" = SQL).
- Exclude vague mentions or indirect context.

Output Requirements:
- `matched_skills`: List of JD skills clearly present in the resume.
- `missing_skills`: List of JD skills not found.
- `explanation`: Clearly justify why those skills were matched or missing.

Important Note:
The **final score shown in**  
`Mandatory Skills: X/50`  
must be **exactly equal** to the result in `calculation`. No rounding up or down is allowed.




2: Experience (Total 30 Points)

STRICT INSTRUCTIONS FOR EXPERIENCE SCORING — DO NOT COMPROMISE:

1. **Experience Parsing Logic**:
   - Extract all time ranges (e.g., "Jan 2022 – May 2023", "Aug 2023 – Present", etc.) from the candidate's work history.
   - If "Present" is mentioned, assume it is up to **June 2025**.
   - Add up **all employment periods** (even across multiple companies) to calculate the candidate’s total experience.
   - Phrases like "Currently working here for 1 year" or "Working since 2023" should be interpreted accordingly and converted into months/years accurately.

2. **JD Experience Range (e.g., “3-8 years”)**:
   - Treat the **minimum experience (e.g., 3 years)** as the required threshold.
   - If the candidate has **equal to or more than 3 years** of total experience, award **full marks (30/30)**.
   - Do **not give partial marks** for anything >= 3 years.
   - If total experience < required threshold, award **0 marks**.

3. **JD Format (e.g., “3+ years required”)**:
   - Interpret this as “minimum 3 years”.
   - If the candidate has **3 or more years**, give **full marks (30/30)**.
   - If the candidate has **less than 3 years**, give **0 marks**.
   - Do **not give any partial marks** here either.

4. **No Guesswork or Estimation**:
   - Do not estimate experience if unclear or ambiguous.
   - Only include durations that are **explicitly mentioned** in the resume.
   - If nothing is mentioned clearly, assume **0 experience**.

5. **Total Experience vs Relevant Domain Experience**:
   - Always mention **both** total experience and domain-relevant experience separately in the explanation.
   - But award marks **only based on total experience** against the JD requirement, unless otherwise instructed.

6. **Scoring Must Be Binary**:
   - This is a **binary evaluation**:
     - If candidate experience meets/exceeds the JD minimum: **Full 30 points**
     - If not: **0 points**
   - Do **not apply** partial credit (e.g., 20/30, 10/30) even if close.


8. **Standardize Dates and Ranges**:
   - Normalize all date formats (e.g., "Jan 2022", "01/2022", "2022-present") into structured ranges for comparison.
   - If only the year is mentioned (e.g., "2022"), assume January as the starting month and December as the ending month.




### ➤ 1. Total Experience
- **Definition**: Number of years from the earliest relevant work start date to the latest end date (or current date if currently employed).
- **Scoring Rules**:
 
- If JD requires 1+ years:
 
Candidate experience more than 6 months → Full score
 
Candidate experience 6 months or less → Zero score
 
- If JD requires 1.5+ years:
 
Candidate experience more than 1 year → Full score
 
Candidate experience 1 year or less → Zero score
 
- If JD requires 2+ years:
 
Candidate experience more than 1 year → Full score
 
Candidate experience 1 year or less → Zero score
 
- If JD requires 2.5+ years:
 
Candidate experience more than 1 year → Full score
 
Candidate experience 1 year or less → Zero score
 
- If JD requires 3+ years:
 
Candidate experience more than 2 years → Full score
 
Candidate experience 2 years or less → Zero score
 
- If JD requires 3.5+ years:
 
Candidate experience more than 2 years → Full score
 
Candidate experience 2 years or less → Zero score
 
- If JD requires 4+ years:
 
Candidate experience more than 2 years → Full score
 
Candidate experience 2 years or less → Zero score
 
- If JD requires 5+ years:
 
Candidate experience more than 3 years → Full score
 
Candidate experience 3 years or less → Zero score
 
- If JD requires 6+ years:
 
Candidate experience more than 4 years → Full score
 
Candidate experience 4 years or less → Zero score
 
- If JD requires 7+ years:
 
Candidate experience more than 5 years → Full score
 
Candidate experience 5 years or less → Zero score
 
- If JD requires 8+ years:
 
Candidate experience more than 6 years → Full score
 
Candidate experience 6 years or less → Zero score
 
- If JD requires 9+ years:
 
Candidate experience more than 7 years → Full score
 
Candidate experience 7 years or less → Zero score
 
- If JD requires 1-2 years:
 
Candidate experience more than 1 year → Full score
 
Candidate experience 1 year or less → Zero score
 
- If JD requires 2-3 years:
 
Candidate experience more than 2 years → Full score
 
Candidate experience 1 year or less → Zero score
 
- If JD requires 3-4 years:
 
Candidate experience more than 2 years → Full score
 
Candidate experience 2 years or less → Zero score
 
- If JD requires 2-4 years:
 
Candidate experience more than 2 years → Full score
 
Candidate experience 1 year or less → Zero score
 
- If JD requires 3-5 years:
 
Candidate experience more than 2 years → Full score
 
Candidate experience 1 year or less → Zero score
 
- If JD requires 4-6 years:
 
Candidate experience more than 3 years → Full score
 
Candidate experience 3 years or less → Zero score
 
- If JD requires 5-7 years:
 
Candidate experience more than 4 years → Full score
 
Candidate experience 4 years or less → Zero score
 
- If JD requires 6-8 years:
 
Candidate experience more than 4 years → Full score
 
Candidate experience 4 years or less → Zero score
 
- If JD requires 7-9 years:
 
Candidate experience more than 5 years → Full score
 
Candidate experience 5 years or less → Zero score
 
- If JD requires 8-10 years:
 
Candidate experience more than 6 years → Full score
 
Candidate experience 6 years or less → Zero score
 
- If JD requires 10+ years:
 
Candidate experience more than 8 years → Full score
 
Candidate experience 8 years or less → Zero score
 
- If JD requires 15+ years:
 
Candidate experience more than 12 years → Full score
 
Candidate experience 12 years or less → Zero score
 
- If JD requires 20+ years:
 
Candidate experience more than 17 years → Full score
 
Candidate experience 17 years or less → Zero score
 
- If JD requires 25+ years:
 
Candidate experience more than 21 years → Full score
 
Candidate experience 21 years or less → Zero score
 
- If JD requires 30+ years:
 
Candidate experience more than 25 years → Full score
 
Candidate experience 25 years or less → Zero score
 
- If JD requires 35+ years:
 
Candidate experience more than 29 years → Full score
 
Candidate experience 29 years or less → Zero score
 
- If JD requires 40+ years:
 
Candidate experience more than 33 years → Full score
 
Candidate experience 33 years or less → Zero score
 
- If JD requires 45+ years:
 
Candidate experience more than 37 years → Full score
 
Candidate experience 37 years or less → Zero score
 
- If JD requires 50+ years:
 
Candidate experience more than 40 years → Full score
 
Candidate experience 40 years or less → Zero score
 
 
 
#### ➤ Examples:
- JD requires 6+ years.
- Resume shows experience from **May 2017 to June 2025** → 8+ years.
- ➤ Score = 30 (since > 4 years)
 
- JD Requirement: 1+ years
Full score if candidate has > 6 months; otherwise zero
 
Example:
Candidate with 7 months → Full score
Candidate with 6 months  → Zero score
 
- JD Requirement: 1.5+ years
Full score if candidate has > 1 year; otherwise zero
 
Example:
Candidate with 1.2 years →  Full score
Candidate with 1.0 year →  Zero score
 
- JD Requirement: 2+ years
Full score if candidate has > 1 year; otherwise zero
 
Example:
Candidate with 1.5 years  →  Full score
Candidate with 1 year  →  Zero score
 
- JD Requirement: 2.5+ years
Full score if candidate has > 1 year; otherwise zero
 
Example:
Candidate with 2.2 years  →  Full score
Candidate with 1.0 year →  Zero score
 
- JD Requirement: 3+ years
Full score if candidate has > 2 years; otherwise zero
 
Example:
Candidate with 2.5 years →  Full score
Candidate with 2 years →  Zero score
 
-  JD Requirement: 3.5+ years
Full score if candidate has > 2 years; otherwise zero
 
Example:
Candidate with 3.2 years  →  Full score
Candidate with 2.0 years →  Zero score
 
- JD Requirement: 4+ years
Full score if candidate has > 2 years; otherwise zero
 
Example:
Candidate with 3.0 years →  Full score
Candidate with 2.0 years  →  Zero score
 
- JD Requirement: 5+ years
Full score if candidate has > 3 years; otherwise zero
 
Example:
Candidate with 4.5 years  →  Full score
Candidate with 3.0 years  →  Zero score
 
- JD Requirement: 6+ years
Full score if candidate has > 4 years; otherwise zero
 
Example:
Candidate with 5.2 years  →  Full score
Candidate with 4.0 years →  Zero score
 
- JD Requirement: 7+ years
Full score if candidate has > 5 years; otherwise zero
 
Example:
Candidate with 6.1 years  →  Full score
Candidate with 5.0 years →  Zero score
 
- JD Requirement: 8+ years
Full score if candidate has > 6 years; otherwise zero
 
Example:
Candidate with 7.5 years  → Full score
Candidate with 6.0 years → Zero score
 
- JD Requirement: 9+ years
Full score if candidate has > 7 years; otherwise zero
 
Example:
Candidate with 8.8 years  →  Full score
Candidate with 7.0 years →  Zero score
 
Example: A candidate with 1.5 years gets full score; a candidate with 0.9 or 2.1 years gets zero.
 
Example: A candidate with 2.7 years gets full score; a candidate with 1.9 or 3.1 years gets zero.
 
Example: A candidate with 3.5 years gets full score; a candidate with 1.5 or 4.5 years gets zero.
 
Example: A candidate with 4 years gets full score; a candidate with 2.9 or 5.1 years gets zero.
 
Example: A candidate with 5 years gets full score; a candidate with 3.8 or 6.5 years gets zero.
 
Example: A candidate with 6.2 years gets full score; a candidate with 4.5 or 7.5 years gets zero.
 
Example: A candidate with 7 years gets full score; a candidate with 5.9 or 8.2 years gets zero.
 
Example: A candidate with 8.5 years gets full score; a candidate with 6.9 or 9.3 years gets zero.
 
Example: A candidate with 9 years gets full score; a candidate with 7.5 or 10.5 years gets zero.
 
- JD Requirement: 10+ years
Full score if candidate has > 8 years; otherwise zero
 
Example:
Candidate with 9.4 years →  Full score
Candidate with 8.0 years →  Zero score
 
- JD Requirement: 15+ years
Full score if candidate has > 12 years; otherwise zero
 
Example:
Candidate with 13.5 years →  Full score
Candidate with 12.0 years →  Zero score
 
- JD Requirement: 20+ years
Full score if candidate has > 17 years; otherwise zero
 
Example:
Candidate with 19.0 years →  Full score
Candidate with 17.0 years →  Zero score
 
- JD Requirement: 25+ years
Full score if candidate has > 21 years; otherwise zero
 
Example:
Candidate with 23.0 years →  Full score
Candidate with 21.0 years →  Zero score
 
- JD Requirement: 30+ years
Full score if candidate has > 25 years; otherwise zero
 
Example:
Candidate with 27.0 years → Full score
Candidate with 25.0 years → Zero score
 
- JD Requirement: 35+ years
Full score if candidate has > 29 years; otherwise zero
 
Example:
Candidate with 30.5 years → Full score
Candidate with 29.0 years → Zero score
 
- JD Requirement: 40+ years
Full score if candidate has > 33 years; otherwise zero
 
Example:
Candidate with 35.0 years → Full score
Candidate with 33.0 years → Zero score
 
- JD Requirement: 45+ years
Full score if candidate has > 37 years; otherwise zero
 
Example:
Candidate with 39.0 years → Full score
Candidate with 37.0 years → Zero score
 
- JD Requirement: 50+ years
Full score if candidate has > 40 years; otherwise zero
 
Example:
Candidate with 42.0 years → Full score
Candidate with 40.0 years → Zero score
 
 
### ➤ 2. Relevant Job Experience (Domain Experience)
- **Definition**: Match the candidate’s work experience content with keywords from the JD domain (e.g., "ABAP, SAP", "ECS", "DATA SCIENCE", "AI/ML").
- **Scoring Rule**:
  - Identify the  domain relevance by matching terms from JD.
  
** strick instruction is if any one of the experience(total or relevant) is matching with the minimum experience of JD requirement then you have to give 30 marks don't pass any partial marks this should be pass very strictly.

- Output should include:
     - `total_experience_years`, `relevant_experience_years`, `jd_required_years', 'Explanation'

3. Project Exposure (0-20 points):

Evaluate ONLY the project section.

Scoring:
- 20/20 → At least one end-to-end (E2E) project with clear JD relevance.
- 10/20 → At least one support project relevant to JD (e.g., monitoring pipelines).
- 0/20 → Only academic or unrelated projects.

Must show actual contributions using verbs like built, deployed, automated, monitored, etc.

- Output must include:
  - ETE_projects: Names and short descriptions
  - support_projects: List of support tasks
  - explanation

  
📌 INSTRUCTIONS:
- Use the JD and resume to generate final JSON output.
- Always follow the logic provided.
- Return output **ONLY** in the structure shown below. No extra text.


IMPORTANT:
- Do NOT estimate or guess the final score.
- Only use the numeric values provided in the individual score sections.
- Extract the number **before the slash ("/")** in each individual score and add them directly.
- The final `"rating"` is the exact **sum** of the three individual numeric scores.
- Do NOT apply any additional weighting or logic beyond summing.

OUTPUT JSON FORMAT:
{{
  "individual_scores": {{
    "Mandatory Skills": "<score>/50. Matched skills: <matched_skills>. Missing: <missing_skills>. Explanation: <how score was derived and why others were missing>.",
    "Experience": "<score>/30. Total experience: <X> years. Relevant domain experience: <years>. JD requirement: <Z> years. Explanation: <how the relevant experience was derived and score awarded>.",
    "Project Exposure": "<score>/20. ETE projects: <summary>. Support projects: <summary>. Explanation: <project relevance to JD and involvement>"
  }},
  "rating": "<SUM of Mandatory Skills + Experience + Project Exposure scores, out of 100>",
  "reason": "<Short 3–5 sentence summary of overall candidate fit, key strengths, and any red flags>"
}}
 

 
Important:
- Use the exact same formula every time.
- Do not vary the score or interpretation across executions with the same data.
- The scoring must be reproducible and consistent across runs.
- If the input (JD and resume) does not change, the score must remain exactly the same.

Job Description:
{query}

Candidate Resume:
{resume_text}

Candidate Name:
{candidate_name}

"""

 
 
        try:
            response = qa_chain.invoke({"query": qa_template})
            result = response.get('result') if isinstance(response, dict) else response
            result = result.strip().replace("```json", "").replace("```", "").strip()
 
            result_json = json.loads(result)
 
            def extract_score(score_string):
               match = re.match(r"(\d+(\.\d+)?)/\d+", score_string.strip())
               return float(match.group(1)) if match else 0.0

            individual_scores = result_json.get("individual_scores", {})

            # Safely extract the three scores
            mandatory_score = extract_score(individual_scores.get("Mandatory Skills", "0.0/50"))
            experience_score = extract_score(individual_scores.get("Experience", "0.0/30"))
            project_score = extract_score(individual_scores.get("Project Exposure", "0.0/20"))

            # Sum and clamp the score
            score = mandatory_score + experience_score + project_score
            score = min(100, max(0, score))  # Clamp score between 0 and 100
 
            return {
                "rating": score,
                "reason": result_json.get("reason", "No reason provided"),
                "individual_scores": result_json.get("individual_scores", {})
            }
 
        except json.JSONDecodeError:
            return {"rating": 0, "reason": "Invalid JSON response"}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"rating": 0, "reason": "No score calculated"}
        
        
        
 