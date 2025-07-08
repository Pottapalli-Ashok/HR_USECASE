class CandidateRenderer:
    def __init__(self, candidates):
        self.candidates = candidates

    def generate_section_details_html(self, section_name, section):
        html = ""
        if section_name == "Core_Skills":
            html += "<li><strong>Matched Core Skills:</strong><ul>"
            for skill in section.get("matched_core_skills", []):
                html += f"<li>{skill}</li>"
            html += "</ul></li>"

            html += "<li><strong>Missing Core Skills:</strong><ul>"
            for skill in section.get("missing_core_skills", []):
                html += f"<li>{skill}</li>"
            html += "</ul></li>"

            html += f"<li><strong>Calculation:</strong> {section.get('calculation', '')}</li>"
            html += f"<li><strong>Explanation:</strong> {section.get('explanation', '')}</li>"

        elif section_name == "Experience":
            html += f"<li>Total Years of Experience: {section.get('total_years_of_experience', 'N/A')}</li>"
            html += f"<li>JD Required Years: {section.get('jd_required_years', 'N/A')}</li>"
            html += f"<li>Calculation: {section.get('calculation', '')}</li>"
            html += f"<li>Explanation: {section.get('explanation', '')}</li>"

        elif section_name == "Project_Exposure":
            html += f"<li>Relevant Projects Found: {section.get('relevant_projects_found', False)}</li>"
            html += "<li>Project Details:<ul>"
            for proj in section.get("project_details", []):
                html += f"<li>{proj}</li>"
            html += "</ul></li>"
            html += f"<li>Explanation: {section.get('explanation', '')}</li>"

        elif section_name == "Added_Advantages":
            html += "<li>Matched Advantages:<ul>"
            for adv in section.get("matched_advantages", []):
                html += f"<li>{adv}</li>"
            html += "</ul></li>"
            html += "<li>Missing Advantages:<ul>"
            for adv in section.get("missing_advantages", []):
                html += f"<li>{adv}</li>"
            html += "</ul></li>"
            html += f"<li>Calculation: {section.get('calculation', '')}</li>"
            html += f"<li>Explanation: {section.get('explanation', '')}</li>"

        elif section_name == "Soft_Skills":
            html += "<li>Matched Soft Skills:<ul>"
            for skill in section.get("matched_soft_skills", []):
                html += f"<li>{skill}</li>"
            html += "</ul></li>"
            html += "<li>Missing Soft Skills:<ul>"
            for skill in section.get("missing_soft_skills", []):
                html += f"<li>{skill}</li>"
            html += "</ul></li>"
            html += f"<li>Explanation: {section.get('explanation', '')}</li>"

        else:
            html += "<li>No details available</li>"

        return html

    def render_candidate_card(self, candidate, rank):
        html = f"""
        <div class="candidate-card" style="border:1px solid #ddd; padding:15px; margin-bottom:20px;">
          <h3>{rank}. {candidate.get('name', 'Unknown')}</h3>
          <p><strong>Match Score:</strong> <span style="color: red;">{candidate.get('score', 0):.1f}%</span></p>
          <p><strong>Reason:</strong> {candidate.get('reason', 'No reason provided')}</p>
          <h4>Individual Scores:</h4>
          <ul>
        """

        for section_name, section_data in candidate.get('individual_scores', {}).items():
            html += f"""
            <li>
              <strong>{section_name.replace('_', ' ')}</strong>: {section_data.get('score', 'N/A')}
              <ul>
                {self.generate_section_details_html(section_name, section_data)}
              </ul>
            </li>
            """

        html += "</ul></div>"
        return html

    def render_all_candidates(self):
        all_html = ""
        for i, candidate in enumerate(self.candidates, start=1):
            all_html += self.render_candidate_card(candidate, i)
        return all_html
