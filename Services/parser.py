import re
from typing import Dict, List

class JDParser:
    @staticmethod
    def extract_jd_requirements(jd_text: str) -> Dict:
        # 1. Extract experience years
        experience_patterns = [
            r"(?i)(?:minimum|at least|over|around)?\s*(\d+(\.\d+)?)\+?\s*years?", 
            r"(?i)require[d]?[^.,;\n]*?(\d+(\.\d+)?)\+?\s*years"
        ]
        experience_years = 0
        for pattern in experience_patterns:
            match = re.search(pattern, jd_text)
            if match:
                experience_years = int(float(match.group(1)))
                break

        # 2. Extract technical skills
        technical_keywords = re.findall(r"(?i)\b([A-Z][a-zA-Z0-9\.\+\#]+(?: [A-Z][a-z]+)?)\b", jd_text)
        # Extract phrases like "such as X, Y, Z" or "technologies like A, B"
        custom_phrases = re.findall(r"(?i)(?:such as|e\.g\.|technologies like)\s+([^.)\n]+)", jd_text)

        skills = set()
        for phrase in custom_phrases:
            for item in re.split(r"[,;/]", phrase):
                cleaned = item.strip()
                if cleaned:
                    skills.add(cleaned)

        # 3. Extract project requirements
        project_keywords = []
        for keyword in ["end-to-end", "support", "monitor", "maintain", "build", "deploy", "design", "implement", "optimize"]:
            if re.search(rf"(?i)\b{keyword}\b", jd_text):
                project_keywords.append(keyword)

        return {
            "core_skills": list(sorted(skills)),
            "min_experience_years": experience_years,
            "project_keywords": project_keywords
        }
