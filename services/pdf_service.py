from fpdf import FPDF
import os

class PDFService:
    def __init__(self):
        self.font_name = "Helvetica"

    def _sanitize_text(self, text):
        if not text:
            return ""
        
        replacements = {
            "\u2022": "-", 
            "\u2013": "-", 
            "\u2014": "-", 
            "\u2018": "\"", 
            "\u2019": "\"", 
            "\u201c": "\"", 
            "\u201d": "\"", 
            "\u2026": "...", 
            "\u00a0": " ", 
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
            
        try:
            return text.encode("latin-1", "ignore").decode("latin-1")
        except Exception:
            return "".join(c for c in text if ord(c) < 128)

    def generate_cv_pdf(self, cv_json_content: dict, output_path: str):
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font(self.font_name, size=12)
        page_width = pdf.w - 2 * pdf.l_margin
        right_margin = pdf.w - pdf.r_margin

        personal_info = cv_json_content.get("personal_info", {})
        
        pdf.set_font(self.font_name, "B", 24)
        pdf.set_text_color(30, 30, 30)
        full_name = self._sanitize_text(personal_info.get("full_name", ""))
        pdf.multi_cell(page_width, 15, full_name, align='L')
        
        pdf.set_font(self.font_name, size=10)
        pdf.set_text_color(80, 80, 80)
        
        contact_lines = []
        email = self._sanitize_text(personal_info.get("email", ""))
        phone = self._sanitize_text(personal_info.get("phone", ""))
        address = self._sanitize_text(personal_info.get("address", ""))
        linkedin = self._sanitize_text(personal_info.get("linkedin", ""))
        portfolio = self._sanitize_text(personal_info.get("portfolio", ""))

        if email: contact_lines.append(email)
        if phone: contact_lines.append(phone)
        if address: contact_lines.append(address)
        
        if contact_lines:
            pdf.multi_cell(page_width, 6, " | ".join(contact_lines), align='L')
        
        links = []
        if linkedin: links.append(f"LinkedIn: {linkedin}")
        if portfolio: links.append(f"Portfolio: {portfolio}")
        
        if links:
            pdf.multi_cell(page_width, 6, " | ".join(links), align='L')

        pdf.ln(5)
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.2)
        pdf.line(pdf.l_margin, pdf.get_y(), right_margin, pdf.get_y())
        pdf.ln(8)

        summary = self._sanitize_text(cv_json_content.get("summary", ""))
        if summary:
            self._add_section_title(pdf, "Summary")
            pdf.set_font(self.font_name, size=11)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(page_width, 7, summary, align='L')
            pdf.ln(5)

        experiences = cv_json_content.get("experience", [])
        if experiences:
            self._add_section_title(pdf, "Experience")
            for exp in experiences:
                pdf.set_font(self.font_name, "B", 12)
                pdf.set_text_color(30, 30, 30)
                title = self._sanitize_text(exp.get('title', ''))
                company = self._sanitize_text(exp.get('company', ''))
                start_date = self._sanitize_text(exp.get('start_date', ''))
                end_date = self._sanitize_text(exp.get('end_date', ''))
                is_current = exp.get('is_current', False)

                date_str = f"{start_date} - {"Present" if is_current else end_date}"
                
                location = self._sanitize_text(exp.get("location", ""))

                start_y = pdf.get_y()
                pdf.multi_cell(page_width * 0.7, 8, f"{title} at {company}", align='L')
                
                current_y = pdf.get_y()
                pdf.set_xy(pdf.l_margin + page_width * 0.7, start_y)
                pdf.multi_cell(page_width * 0.3, 8, date_str, align='R')
                
                pdf.set_y(max(current_y, pdf.get_y()))
                pdf.set_x(pdf.l_margin)

                if location:
                    pdf.set_font(self.font_name, size=10)
                    pdf.set_text_color(80, 80, 80)
                    pdf.multi_cell(page_width, 6, location, align='L')
                
                pdf.set_font(self.font_name, size=10)
                pdf.set_text_color(50, 50, 50)
                bullet_indent = 5 
                bullet_width = page_width - bullet_indent
                for point in exp.get("description_points", []):
                    clean_point = self._sanitize_text(point)
                    if clean_point.strip():
                        pdf.set_x(pdf.l_margin + bullet_indent)
                        pdf.multi_cell(bullet_width, 6, f"- {clean_point.strip()}", align='L')
                pdf.ln(4)

        education_list = cv_json_content.get("education", [])
        if education_list:
            self._add_section_title(pdf, "Education")
            for edu in education_list:
                pdf.set_font(self.font_name, "B", 12)
                pdf.set_text_color(30, 30, 30)
                degree = self._sanitize_text(edu.get('degree', ''))
                field = self._sanitize_text(edu.get('field_of_study', ''))
                institution = self._sanitize_text(edu.get("institution", ""))
                start_date = self._sanitize_text(edu.get('start_date', ''))
                end_date = self._sanitize_text(edu.get('end_date', ''))
                is_current = edu.get('is_current', False)

                date_str = f"{start_date} - {"Present" if is_current else end_date}"
                
                start_y = pdf.get_y()
                pdf.multi_cell(page_width * 0.7, 8, f"{degree} in {field}", align='L')
                
                current_y = pdf.get_y()
                pdf.set_xy(pdf.l_margin + page_width * 0.7, start_y)
                pdf.multi_cell(page_width * 0.3, 8, date_str, align='R')
                
                pdf.set_y(max(current_y, pdf.get_y()))
                pdf.set_x(pdf.l_margin)

                pdf.set_font(self.font_name, size=10)
                pdf.set_text_color(80, 80, 80)
                pdf.multi_cell(page_width, 6, institution, align='L')
                pdf.ln(3)

        skills = cv_json_content.get("skills", [])
        if skills:
            self._add_section_title(pdf, "Skills")
            pdf.set_font(self.font_name, size=11)
            pdf.set_text_color(50, 50, 50)
            
            skill_strings = []
            for skill in skills:
                name = self._sanitize_text(skill.get('name', ''))
                level = self._sanitize_text(skill.get('level', ''))
                level_str = f" ({level})" if level else ""
                skill_strings.append(f"{name}{level_str}")
            
            pdf.multi_cell(page_width, 7, ", ".join(skill_strings), align='L')
            pdf.ln(5)

        projects = cv_json_content.get("projects", [])
        if projects:
            self._add_section_title(pdf, "Projects")
            for project in projects:
                pdf.set_font(self.font_name, "B", 12)
                pdf.set_text_color(30, 30, 30)
                name = self._sanitize_text(project.get("name", ""))
                pdf.multi_cell(page_width, 8, name, align='L')
                
                pdf.set_font(self.font_name, size=10)
                pdf.set_text_color(50, 50, 50)
                description = self._sanitize_text(project.get("description", ""))
                if description:
                    pdf.multi_cell(page_width, 6, description, align='L')
                
                techs = project.get("technologies", [])
                if isinstance(techs, list) and techs:
                    tech_str = ", ".join(techs)
                    pdf.set_font(self.font_name, "I", 9)
                    pdf.set_text_color(80, 80, 80)
                    pdf.multi_cell(page_width, 6, f"Technologies: {self._sanitize_text(tech_str)}", align='L')
                
                url = self._sanitize_text(project.get("url", ""))
                if url:
                    pdf.set_font(self.font_name, size=9)
                    pdf.set_text_color(50, 150, 200)
                    pdf.multi_cell(page_width, 5, f"Link: {url}", align='L')
                pdf.ln(4)

        certifications = cv_json_content.get("certifications", [])
        if certifications:
            self._add_section_title(pdf, "Certifications")
            for cert in certifications:
                pdf.set_font(self.font_name, "B", 12)
                pdf.set_text_color(30, 30, 30)
                name = self._sanitize_text(cert.get('name', ''))
                issuing_organization = self._sanitize_text(cert.get('issuing_organization', ''))
                issue_date = self._sanitize_text(cert.get('issue_date', ''))

                date_str = f"{issue_date}"
                
                start_y = pdf.get_y()
                pdf.multi_cell(page_width * 0.7, 8, f"{name} from {issuing_organization}", align='L')
                
                current_y = pdf.get_y()
                pdf.set_xy(pdf.l_margin + page_width * 0.7, start_y)
                pdf.multi_cell(page_width * 0.3, 8, date_str, align='R')
                
                pdf.set_y(max(current_y, pdf.get_y()))
                pdf.set_x(pdf.l_margin)

                url = self._sanitize_text(cert.get("url", ""))
                if url:
                    pdf.set_font(self.font_name, size=9)
                    pdf.set_text_color(50, 150, 200)
                    pdf.multi_cell(page_width, 5, f"Link: {url}", align='L')
                pdf.ln(4)

        pdf.output(output_path)
        return True

    def _add_section_title(self, pdf, title):
        page_width = pdf.w - 2 * pdf.l_margin
        pdf.set_font(self.font_name, "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(page_width, 10, title, align='L')
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(3)
