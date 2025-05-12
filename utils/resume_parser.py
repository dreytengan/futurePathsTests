# resume_parser.py
import fitz  # PyMuPDF
import re
from collections import Counter # Not used in current version, but can be useful for advanced skill counting

def pdf_to_text(uploaded_file_object):
    """Converts a PDF file object to text."""
    try:
        # uploaded_file_object is Streamlit's UploadedFile, which has a read() method
        pdf_document = fitz.open(stream=uploaded_file_object.getvalue(), filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text("text")
        pdf_document.close()
        return text
    except Exception as e:
        print(f"Error converting PDF to text: {e}")
        return None

def extract_sections(text):
    """
    Tries to identify common resume sections and their content.
    Returns a dictionary like {'Experience': 'text content', 'Skills': 'text content'}
    """
    sections = {}
    section_keywords = [
        "summary", "objective", "profile",
        "experience", "work experience", "professional experience", "employment history",
        "education", "academic background",
        "skills", "technical skills", "proficiencies", "competencies",
        "projects", "personal projects",
        "certifications", "licenses",
        "awards", "honors",
        "publications",
        "references"
    ]
    pattern_parts = []
    for keyword in section_keywords:
        pattern_parts.append(f"^(?:\\s*[-*•]?\\s*)({keyword.replace(' ', r'\\s+')})(?:\\s*:|\\s*\\n)")
    regex_pattern = re.compile("|".join(pattern_parts), re.IGNORECASE | re.MULTILINE)

    last_match_end = 0
    current_section_title_key = None
    
    matches = list(regex_pattern.finditer(text))

    for i, match in enumerate(matches):
        section_title_found = next(s for s in match.groups() if s is not None).lower().strip()
        
        # Normalize common variations
        normalized_title = section_title_found
        if "experience" in section_title_found or "employment" in section_title_found:
            normalized_title = "Experience"
        elif "skill" in section_title_found or "proficienc" in section_title_found or "competen" in section_title_found:
            normalized_title = "Skills"
        elif "education" in section_title_found or "academic" in section_title_found:
            normalized_title = "Education"
        elif "summary" in section_title_found or "profile" in section_title_found or "objective" in section_title_found:
            normalized_title = "Summary"
        elif "project" in section_title_found:
            normalized_title = "Projects"
        else:
            normalized_title = section_title_found.capitalize()

        if current_section_title_key and last_match_end < match.start():
            content = text[last_match_end:match.start()].strip()
            if current_section_title_key in sections:
                 sections[current_section_title_key] += "\n" + content
            else:
                sections[current_section_title_key] = content
        
        current_section_title_key = normalized_title
        last_match_end = match.end()

    if current_section_title_key and last_match_end < len(text):
        content = text[last_match_end:].strip()
        if current_section_title_key in sections:
            sections[current_section_title_key] += "\n" + content
        else:
            sections[current_section_title_key] = content
            
    if not sections and text: # Fallback if no sections detected
        # Try to infer experience block by looking for date patterns or typical job title phrasing
        # This is a very rough fallback.
        sections["Experience"] = text 

    return sections


def extract_job_entries(experience_text):
    """
    Extracts job titles, companies, dates, and descriptions from experience text.
    Returns a list of dictionaries. Assumes reverse chronological order.
    """
    if not experience_text:
        return []

    entries = []
    # Try to split by patterns that might indicate start of a new job entry.
    # e.g., A line that looks like a job title, followed by a line with company/dates.
    # This regex looks for a line that is likely a job title (1-6 words, initial caps, not all caps unless short)
    # and is NOT preceded by a bullet point (to avoid list items within a description).
    # It captures up to the next job title or end of text.
    # This is a simplified block splitter.
    job_block_pattern = re.compile(
        r"(?<!^\s*[-*•])"  # Negative lookbehind for bullet points
        r"^\s*([A-Z][a-zA-Z\s,-/\(\)&']{5,60}[a-zA-Z\)]|[A-Z][A-Z\s'&]{3,60}[A-Z])\s*$" # Potential title line
        r"(?:[\r\n]+^\s*(?:[A-Z][a-zA-Z\s,.'&]+(?:LLC|Inc|Ltd|Corp)?\s*\|?\s*(?:[A-Za-z]+\s+\d{4}|\d{1,2}/\d{4})\s*[\r\n]+)?" # Optional company/date line
        , re.MULTILINE
    )
    
    # Find all potential job title lines
    title_lines_matches = []
    for match in re.finditer(r"^\s*([A-Z][a-zA-Z\s,-/\(\)&']{5,60}[a-zA-Z\)]|[A-Z][A-Z\s'&]{3,60}[A-Z])\s*$", experience_text, re.MULTILINE):
        line_text = match.group(0).strip()
        # Filter out lines that are likely section subheaders or too generic
        if line_text.lower() not in ["responsibilities", "achievements", "key projects"] and \
           not re.search(r"(?i)(inc\.?|llc|ltd\.?|gmbh|corp\.?|solution)", line_text) and \
           len(line_text.split(',')) < 3 and \
           not (len(line_text.split()) > 6 and not any(kw in line_text.lower() for kw in ["manager", "engineer", "developer", "analyst", "specialist"])):
            title_lines_matches.append(match)


    for i, title_match in enumerate(title_lines_matches):
        title = title_match.group(0).strip()
        
        block_start = title_match.end()
        block_end = title_lines_matches[i+1].start() if i + 1 < len(title_lines_matches) else len(experience_text)
        
        content_after_title = experience_text[block_start:block_end].strip()
        
        # First non-empty line after title is often company/date
        # Rest is description. This is very simplified.
        lines = [line.strip() for line in content_after_title.split('\n') if line.strip()]
        
        company_date_info = ""
        description_lines = []

        if lines:
            # Check if first line looks like company/date info
            # Heuristic: contains city names, date patterns, or company suffixes
            date_regex = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current|To\s+Date|\d{1,2}[/-]\d{4}|\d{4})"
            if re.search(date_regex, lines[0], re.IGNORECASE) or \
               re.search(r"(?i)(inc\.?|llc|ltd\.?|gmbh|corp|university|college|institute)", lines[0]) or \
               re.search(r",\s*(?:[A-Z]{2}|[A-Za-z]+)$", lines[0]): # City, ST or City, Country
                company_date_info = lines[0]
                description_lines = lines[1:]
            else:
                description_lines = lines
        
        description = "\n".join(description_lines)
        description = re.sub(r"^\s*[-*•]\s*", "", description, flags=re.MULTILINE)
        description = re.sub(r"\s*\n\s*", "\n", description).strip()

        if title and (description or company_date_info): # Only add if we have a title and some other info
            entries.append({
                "title": title,
                "company_date_info": company_date_info,
                "description": description,
            })
    return entries


def extract_skills(skills_text):
    if not skills_text:
        return []
    
    skills_text = re.sub(r"^\s*[*•-]\s*", "", skills_text, flags=re.MULTILINE)
    raw_skills = []
    for line in skills_text.split('\n'):
        # Split by comma, semicolon, or "and" surrounded by spaces (less aggressive)
        line_skills = re.split(r'[,;/]\s*|\s+and\s+', line, flags=re.IGNORECASE)
        raw_skills.extend(line_skills)

    processed_skills = []
    common_skill_words_to_ignore = {"etc", "various", "other", "strong", "excellent", "proficient", "experience"}
    for skill in raw_skills:
        skill = skill.strip().rstrip('.').strip() # Remove trailing periods
        # Filter: not too long/short, not just numbers, not common fluff, has at least one letter
        if skill and 1 < len(skill) < 35 and re.search(r'[a-zA-Z]', skill) \
           and not skill.isdigit() and skill.lower() not in common_skill_words_to_ignore \
           and len(skill.split()) <= 4: # Max 4 words per skill
            processed_skills.append(skill)
    
    return list(dict.fromkeys(processed_skills)) # Unique skills


def parse_resume_data(uploaded_file_object):
    """
    Main parsing function.
    Returns a dictionary with 'most_recent_job', 'all_jobs', 'skills', 'summary'.
    """
    text = pdf_to_text(uploaded_file_object)
    if not text:
        return {"error": "Could not read text from PDF."}

    sections = extract_sections(text)
    
    parsed_data = {
        "most_recent_job": None,
        "all_jobs": [],
        "skills": [],
        "summary": sections.get("Summary", sections.get("Profile", sections.get("Objective", ""))), # Combine common summary sections
        "full_text": text 
    }

    if "Experience" in sections:
        job_entries = extract_job_entries(sections["Experience"])
        parsed_data["all_jobs"] = job_entries
        if job_entries:
            parsed_data["most_recent_job"] = job_entries[0] # Assumes reverse chronological
    
    if "Skills" in sections:
        parsed_data["skills"].extend(extract_skills(sections["Skills"]))
    
    # Fallback: if no skills section, try to get some from recent job description (very rough)
    if not parsed_data["skills"] and parsed_data["most_recent_job"] and parsed_data["most_recent_job"]["description"]:
        # This is a very basic keyword spotting, not true skill extraction
        potential_skills_from_desc = []
        desc_sentences = re.split(r'[.\n]', parsed_data["most_recent_job"]["description"])
        for sentence in desc_sentences:
            words = sentence.split()
            for i, word in enumerate(words):
                # Look for capitalized words (potential tech/tools) not at sentence start
                if word.istitle() and i > 0 and len(word) > 2 and word.lower() not in ["the", "and", "for", "with"]:
                    potential_skills_from_desc.append(word.strip(',.;:'))
        if potential_skills_from_desc:
             parsed_data["skills"].extend(list(dict.fromkeys(potential_skills_from_desc))[:10]) # Top 10 unique

    parsed_data["skills"] = list(dict.fromkeys(parsed_data["skills"])) # Ensure unique
    return parsed_data