import os
import json
from google import genai
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()


class GeminiAIService:
    def __init__(self):
        """Initialize the AI service with API key from environment variables."""
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("Could not find GEMINI_API_KEY. Check your .env file.")

        try:
            self.client = genai.Client(api_key=api_key)
            self.model = "gemini-2.5-flash"
        except Exception as e:
            raise Exception(f"Model Initialization Failed: {str(e)}")

    def generate_tailored_cv_content(self, profile_data, job_description=None, user_prompt=None):
        """Generate CV content using AI, optionally tailored for a specific job description."""
        user = profile_data.get("user", {})
        user = profile_data.get("user", {})
        formatted_profile_data = {
            "personal_info": {
                "full_name": user.get("full_name", ""),
                "email": user.get("email", ""),
                "phone": user.get("phone_number", ""),
                "address": user.get("address", ""),
                "linkedin": profile_data.get("linkedin", ""), # Added linkedin
                "portfolio": profile_data.get("portfolio", "")
            },
            "summary": profile_data.get("bio", ""),
            "experience": [
                {
                    "title": exp.get("title", ""),
                    "company": exp.get("company", ""),
                    "location": "", 
                    "start_date": f"{exp['start_date'][5:7]}/{exp['start_date'][0:4]}" if exp.get("start_date") else "",
                    "end_date": f"{exp['end_date'][5:7]}/{exp['end_date'][0:4]}" if exp.get("end_date") and not exp.get("is_current") else ("Present" if exp.get("is_current") else ""),
                    "is_current": exp.get("is_current", False),
                    "description_points": [exp.get("description", "")] if exp.get("description") else []
                }
                for exp in profile_data.get("experiences", [])
            ],
            "education": [
                {
                    "degree": edu.get("degree", ""),
                    "field_of_study": edu.get("field_of_study", ""),
                    "institution": edu.get("institution", ""),
                    "location": "",
                    "start_date": f"{edu['start_date'][5:7]}/{edu['start_date'][0:4]}" if edu.get("start_date") else "",
                    "end_date": f"{edu['end_date'][5:7]}/{edu['end_date'][0:4]}" if edu.get("end_date") and not edu.get("is_current") else ("Present" if edu.get("is_current") else ""),
                    "is_current": edu.get("is_current", False)
                }
                for edu in profile_data.get("education", [])
            ],
            "skills": [
                {
                    "name": skill.get("name", ""),
                    "level": skill.get("level", "")
                }
                for skill in profile_data.get("skills", [])
            ],
            "projects": [
                {
                    "name": proj.get("name", ""),
                    "description": proj.get("description", ""),
                    "technologies": proj.get("technologies", []),
                    "url": proj.get("url", ""),
                    "is_current": proj.get("is_current", False)
                }
                for proj in profile_data.get("projects", [])
            ],
            "certifications": [
                {
                    "name": cert.get("name", ""),
                    "issuing_organization": cert.get("issuing_organization", ""),
                    "issue_date": f"{cert['issue_date'][5:7]}/{cert['issue_date'][0:4]}" if cert.get("issue_date") else "",
                    "url": cert.get("url", "")
                }
                for cert in profile_data.get("certifications", [])
            ]
        }

        profile_json_input = json.dumps(formatted_profile_data, ensure_ascii=False, indent=2)
        
        system_instructions = """You are an expert CV writer and data analyst. Your task is to analyze the candidate\"s profile data and the target job description (if provided), then generate an optimized and well-structured CV in JSON format. The output MUST be a perfectly valid JSON object.

**Key Instructions:**
1.  **Output Format:** The output MUST be a JSON object following the exact structure provided below. Do NOT add any extra text before or after the JSON object.
2.  **Job-Specific Customization (if job description is available):**
    *   Carefully analyze the job description to identify keywords, required skills, and relevant experience.
    *   Rewrite the \"summary\" to clearly highlight the candidate\"s suitability for the target role.
    *   In the \"experience\" section, focus on description points that emphasize achievements and responsibilities most relevant to the job. Use strong action verbs (e.g., developed, designed, implemented, optimized, managed) and quantifiable metrics where possible.
3.  **General CV (if no job description is available):**
    *   If no job description is provided, create a strong general CV that showcases the candidate\"s best achievements and skills comprehensively and appealingly.
4.  **Accuracy:** Maintain the accuracy of core information (dates, company names, degrees).
5.  **Conciseness and Focus:** Keep descriptions concise and focused on value and accomplishments.
6.  **Language:** All generated content MUST be in **English**.
7.  **ATS-Friendly:** Ensure the language and structure are optimized for Applicant Tracking Systems (ATS) to maximize keyword matching and readability.

**Required JSON Structure:**
{
  \"personal_info\": {
    \"full_name\": \"[Candidate\\\"s Full Name]\",
    \"email\": \"[Email Address]\",
    \"phone\": \"[Phone Number]\",
    \"address\": \"[Address]\",
    \"linkedin\": \"[LinkedIn Profile URL]\",
    \"portfolio\": \"[Portfolio URL]\"
  },
  \"summary\": \"[Strong professional summary, tailored for the job or general]\",
  \"experience\": [
    {
      \"title\": \"[Job Title]\",
      \"company\": \"[Company Name]\",
      \"location\": \"[Company Location]\",
      \"start_date\": \"[MM/YYYY]\",
      \"end_date\": \"[MM/YYYY or Present]\",
      \"is_current\": [true/false],
      \"description_points\": [
        \"[Achievement point 1]\",
        \"[Achievement point 2]\"
      ]
    }
  ],
  \"education\": [
    {
      \"degree\": \"[Degree]\",
      \"field_of_study\": \"[Field of Study]\",
      \"institution\": \"[Educational Institution Name]\",
      \"location\": \"[Institution Location]\",
      \"start_date\": \"[MM/YYYY]\",
      \"end_date\": \"[MM/YYYY or Present]\",
      \"is_current\": [true/false]
    }
  ],
  \"skills\": [
    {
      \"name\": \"[Skill Name]\",
      \"level\": \"[Skill Level: Beginner, Intermediate, Advanced, Expert]\"
    }
  ],
  \"projects\": [
    {
      \"name\": \"[Project Name]\",
      \"description\": \"[Brief description of the project and its achievements]\",
      \"technologies\": [\"[Technology 1]\", \"[Technology 2]\"],
      \"url\": \"[Project URL (optional)]\",
      \"is_current\": [true/false]
    }
  ],
  \"certifications\": [
    {
      \"name\": \"[Certification Name]\",
      \"issuing_organization\": \"[Issuing Organization]\",
      \"issue_date\": \"[MM/YYYY]\",
      \"url\": \"[Certification URL (optional)]\"
    }
  ]
}"""

        full_prompt = f"{system_instructions}\n\n**Candidate Profile Data (Input):**\n{profile_json_input}"
        
        if job_description:
            full_prompt += f"\n\n**Target Job Description:**\n{job_description}"
        
        if user_prompt:
            full_prompt += f"\n\n**Additional User Instructions:**\n{user_prompt}"

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
            )

            if not response:
                raise Exception("AI returned an empty response (Check safety settings or quota).")

            content = (response.text or "").strip()

            if not content:
                raise Exception("AI returned an empty response (Check safety settings or quota).")

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"--- FAILED CONTENT: {content} ---")
                raise Exception(f"AI output is not a valid JSON. Error: {str(e)}")

        except Exception as e:
            print(f"--- CRITICAL AI ERROR: {str(e)} ---")
            raise Exception(f"Detailed AI Error: {str(e)}")
