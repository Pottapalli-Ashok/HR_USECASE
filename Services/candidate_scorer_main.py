# import json
# from typing import Dict

# class CandidateScorer:
#     @staticmethod
#     def analyze_candidate(qa_chain, query: str, candidate_name: str) -> Dict[str, float]:
#         """Analyze a single candidate and return a matching score."""

#         qa_template = f"""
# You are an AI resume evaluator. Your task is to analyze how well the candidate '{candidate_name}' fits the job description (JD), using a weighted scoring system. You must strictly follow the logic and return only a valid JSON object.

# 🎯 Scoring Rules (Total: 100 points):

# 1. **Core Skills (0–50 points)**  
#    Compare the candidate’s skills with 6 core skills listed in the JD.  
#    - Formula: (Number of matched or closely related skills ÷ 6) × 50  
#    - Partial matches (e.g., related technologies or concepts) can be considered. 

# 2. Experience (0–20 points)  
#    - JD expects 3–6 years of experience.  
#    - Candidate with 3 years or more (including "3+") should get full 20 points.  
#    - Interpret "3+ years" as **3.5**, "5+ years" as **5.5**, etc. 
#    - Formula: Normalize candidate experience to a 20-point scale.
#    - Candidates with less than 3 years get proportional score: (candidate_experience / 3) * 20.  
#    - The explanation must mention the exact experience used (e.g., "3.5 years") and if full or partial marks are awarded.  
   
#     Examples:  
#     - "Experience": "20/20 - Candidate has 3.5 years of experience, fully meeting the JD’s 3–6 year requirement"  
#     - "Experience": "13.3/20 - Candidate has 2 years of experience, partially meeting JD requirement (score scaled proportionally)"  


# 3. **Project Exposure (0–15 points)**  
#    JD may specify a mix of End-to-End (ETE) and support/maintenance projects.  
#    Distribute 15 points as follows:
#    - Each required **ETE** project contributes **10 points**  
#    - Each required **Support** project contributes **5 points**
#    - If the JD has multiple support projects, divide the 5 points equally across them  
#    - Candidate score is based on how many of the listed project types match
#    - Partial scores are allowed if only some of the listed project types are matched  

#    Examples:
#    - JD: 1 ETE + 2 Support → ETE = 10 points, each Support = 2.5 points  
#    - Candidate matches all → 15/15  
#    - Candidate matches only 1 support → 2.5/15  
#    - Candidate matches ETE only → 10/15  


# 4. **Added Advantages (0–10 points)** 
#    - Match with advanced tools/tech from JD (e.g., SAP GRC, automation, data migration).  
#    - Formula: (Matched ÷ total in JD) × 10  
#    Example:
#      - JD lists 3 tools; candidate matches 2 → (2/3) × 10 = 10 points

# 5. **Soft Skills (0–5 points)**  
#    - If resume shows communication, collaboration, leadership, or adaptability → 5 points  
#    - Else: 0  
#    - You may infer soft skills from phrases like "led a team," "managed stakeholders," etc.

# 📌 Instructions:
# 1. Parse both the JD and candidate profile.
# 2. Evaluate each category using the rules above.
# 3. For **each individual score**, include:
#    - A short **positive explanation** (what was matched well)  
#    - A short **negative explanation** (what is missing or weak)
# 4. For the final **overall reason**, clearly summarize candidate’s strengths and any red flags.
# 5. **Return ONLY valid JSON** as shown below. No markdown, no extra text.

# ✅ JSON Output Format:
# {{
#   "individual_scores": {{
#     "Core Skills": "<score>/50 - <1-line positive/ negative>",
#     "Experience": "<score>/20 - <1-line positive/ negative>",
#     "Project Exposure": "<score>/15 - <1-line positive/ negative>",
#     "Added Advantages": "<score>/10 - <1-line positive/ negative>",
#     "Soft Skills": "<score>/5 - <1-line positive/ negative>"
#   }},
#   "rating": <total_score_out_of_100>,
#   "reason": "<1-2 sentence overall summary of candidate fit and concerns>"
# }}

# Job Description:
# {query}
# """


#         try:
#             response = qa_chain.invoke({"query": qa_template})
#             result = response.get('result') if isinstance(response, dict) else response
#             result = result.strip().replace("```json", "").replace("```", "").strip()

#             result_json = json.loads(result)

#             score = float(result_json.get("rating", 0))
#             score = min(100, max(0, score))  # Clamp score between 0 and 100

#             return {
#                 "rating": score,
#                 "reason": result_json.get("reason", "No reason provided"),
#                 "individual_scores": result_json.get("individual_scores", {})
#             }

#         except json.JSONDecodeError:
#             return {"rating": 0, "reason": "Invalid JSON response"}
#         except Exception as e:
#             print(f"Unexpected error: {e}")
#             return {"rating": 0, "reason": "No score calculated"}
