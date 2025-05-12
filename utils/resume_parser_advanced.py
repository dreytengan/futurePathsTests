# resume_parser_advanced.py
import fitz  # PyMuPDF
import re
from collections import Counter

def pdf_to_text(uploaded_file_object):
    """Converts a PDF file object to text."""
    try:
        pdf_document = fitz.open(stream=uploaded_file_object.read(), filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text("text") # "text" for better layout preservation if needed
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
    # Common section headers - case insensitive, allowing for colon or newline
    # Order matters for some heuristics (e.g. experience before education for most recent job)
    section_keywords = [
        "summary", "objective", "profile", # Often at the top
        "experience", "work experience", "professional experience", "employment history", # Core
        "education", "academic background",
        "skills", "technical skills", "proficiencies",
        "projects", "personal projects",
        "certifications", "licenses",
        "awards", "honors",
        "publications",
        "references" # Usually last
    ]

    # Create a regex pattern for section headers
    # Looks for keyword at start of line (possibly with some leading whitespace/bullets)
    # followed by a newline or colon
    pattern_parts = []
    for keyword in section_keywords:
        # Allow for keyword to be followed by a colon, or just a newline.
        # Capture the keyword itself to use as dict key.
        pattern_parts.append(f"^(?:\\s*[-*•]?\\s*)({keyword.replace(' ', r'\\s+')})(?:\\s*:|\\s*\\n)")
    
    regex_pattern = re.compile("|".join(pattern_parts), re.IGNORECASE | re.MULTILINE)

    last_match_end = 0
    current_section_title = None
    
    # First, find all matches and their positions
    matches = list(regex_pattern.finditer(text))

    for i, match in enumerate(matches):
        # The first group that matched is the keyword
        section_title_found = next(s for s in match.groups() if s is not None).lower().strip()
        
        # Normalize common variations
        if "experience" in section_title_found or "employment" in section_title_found:
            section_title_key = "Experience"
        elif "skill" in section_title_found or "proficienc" in section_title_found:
            section_title_key = "Skills"
        elif "education" in section_title_found or "academic" in section_title_found:
            section_title_key = "Education"
        elif "summary" in section_title_found or "profile" in section_title_found or "objective" in section_title_found:
            section_title_key = "Summary"
        elif "project" in section_title_found:
            section_title_key = "Projects"
        else:
            section_title_key = section_title_found.capitalize()

        if current_section_title and last_match_end < match.start():
            # Content for the previous section
            content = text[last_match_end:match.start()].strip()
            if current_section_title in sections: # append if section appears multiple times (unlikely but possible)
                 sections[current_section_title] += "\n" + content
            else:
                sections[current_section_title] = content
        
        current_section_title = section_title_key
        last_match_end = match.end()

    # Add content for the last section found
    if current_section_title and last_match_end < len(text):
        content = text[last_match_end:].strip()
        if current_section_title in sections:
            sections[current_section_title] += "\n" + content
        else:
            sections[current_section_title] = content
            
    # If no sections detected (e.g., plain text resume), treat whole text as "Experience" for job title search
    if not sections and text:
        sections["Experience"] = text # Fallback

    return sections


def extract_job_entries(experience_text):
    """
    Extracts job titles, companies, dates, and descriptions from experience text.
    This is highly heuristic. A job entry is often:
    Title
    Company | Location | Dates
    - Responsibility
    - Responsibility
    Returns a list of dictionaries.
    """
    if not experience_text:
        return []

    entries = []
    # Split by common delimiters for job entries, often a blank line or a line with just a date range
    # This is very tricky. Let's try to find blocks that start with a likely title.
    # A line with 1-5 words, mostly capitalized or Title Case, not ending in a punctuation like '.'
    # And followed by something that looks like a company/date line OR bullet points.

    # Regex for a potential job title line:
    # Starts with capital, 1-6 words, doesn't look like a date or common list item prefix.
    # Allows for things like "Senior Software Engineer (Contract)"
    title_regex = re.compile(
        r"^\s*([A-Z][a-zA-Z\s,-/\(\)]+[a-zA-Z\)]|[A-Z]+(?: [A-Z&]+)*)\s*$",
        re.MULTILINE
    )
    # Regex for a date range (very broad)
    date_regex = re.compile(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current|\d{1,2}/\d{4}|\d{4})", re.IGNORECASE)

    # A simpler approach: look for lines that look like titles, then grab text until next title-like line or end of section
    potential_title_matches = list(title_regex.finditer(experience_text))
    
    for i, title_match in enumerate(potential_title_matches):
        title_line = title_match.group(1).strip()
        
        # Heuristic checks for a title:
        # - Not too long, not too short
        # - Not just "Company Inc." (contains common company suffixes)
        # - Doesn't look like a list of skills
        # - Doesn't contain too many numbers (unless part of a common title like "Developer I")
        if not (3 < len(title_line) < 70 and \
                not re.search(r"(?i)(inc\.?|llc|ltd\.?|gmbh|corp\.?|solution)", title_line) and \
                not "," in title_line and len(title_line.split(",")) > 3 and \
                not re.search(r"\d{2,}", title_line.replace("3D","").replace("2D",""))): # avoid lines that are mostly dates or numbers
            continue

        # If it's potentially a title, check if the *next* line has a date, or if it's a bullet point start.
        # This helps confirm it's not just a random capitalized line.
        start_block = title_match.end()
        end_block = potential_title_matches[i+1].start() if i + 1 < len(potential_title_matches) else len(experience_text)
        
        block_text = experience_text[start_block:end_block].strip()
        lines_in_block = block_text.split('\n')

        # Check first few lines of the block for company/date or start of description
        company_date_line = ""
        description_start_index = 0
        if lines_in_block:
            # Often company/date is on the next line or line after
            for k in range(min(2, len(lines_in_block))):
                if date_regex.search(lines_in_block[k]) or \
                   re.search(r"(?i)(company|inc|llc|ltd|gmbh|corp)", lines_in_block[k]):
                    company_date_line += lines_in_block[k].strip() + " "
                    description_start_index = k + 1
                # If first line of block starts with bullet, it's likely description
                elif re.match(r"^\s*[-*•]", lines_in_block[k]):
                    break 
        
        description = "\n".join(lines_in_block[description_start_index:]).strip()
        # Basic cleaning of description
        description = re.sub(r"^\s*[-*•]\s*", "", description, flags=re.MULTILINE) # Remove bullets for easier processing later
        description = re.sub(r"\n+", "\n", description).strip() # Normalize newlines

        # Heuristic: If description is very short and title is generic, might be a sub-heading not a job.
        if len(description.split()) < 5 and title_line.lower() in ["responsibilities", "achievements"]:
            continue
            
        # We need to infer which job is most recent. This usually relies on dates.
        # For simplicity, we assume jobs are listed in reverse chronological order (most recent first).
        # A full date parser is complex. We'll just store the text.
        entries.append({
            "title": title_line,
            "company_date_info": company_date_line.strip(),
            "description": description,
        })

    # If we found multiple entries, the first one is usually the most recent.
    return entries


def extract_skills(skills_text):
    """Extracts skills from a block of text, often comma or newline separated."""
    if not skills_text:
        return []
    
    # Split by common delimiters: newline, comma, semicolon, bullet points
    # Normalize by removing bullet points first
    skills_text = re.sub(r"^\s*[*•-]\s*", "", skills_text, flags=re.MULTILINE)
    # Split by newline, then by comma/semicolon for each line
    raw_skills = []
    for line in skills_text.split('\n'):
        raw_skills.extend(re.split(r'[,;/]\s*', line)) # also allow slash as delimiter for things like "HTML/CSS"

    processed_skills = []
    for skill in raw_skills:
        skill = skill.strip()
        # Basic filter: not too long, not too short, not just numbers, not common stop words
        if skill and 2 <= len(skill) <= 50 and not skill.isdigit() \
           and skill.lower() not in ["and", "or", "the", "of", "in", "at", "with", "for"]:
            processed_skills.append(skill)
    
    # Count frequencies and return unique skills, perhaps most frequent ones if list is too long
    # For now, just unique sorted by typical appearance (which is somewhat preserved)
    return list(dict.fromkeys(processed_skills))


def parse_resume(uploaded_file_object):
    """
    Main parsing function.
    Returns a dictionary with 'most_recent_job', 'all_jobs', 'skills', 'summary'.
    """
    text = pdf_to_text(uploaded_file_object)
    if not text:
        return None

    sections = extract_sections(text)
    # print("DEBUG: Detected Sections:", sections.keys()) # For debugging

    parsed_data = {
        "most_recent_job": None,
        "all_jobs": [],
        "skills": [],
        "summary": sections.get("Summary", ""),
        "full_text": text # For fallback or advanced use
    }

    if "Experience" in sections:
        job_entries = extract_job_entries(sections["Experience"])
        parsed_data["all_jobs"] = job_entries
        if job_entries:
            # Assuming the first entry is the most recent one
            parsed_data["most_recent_job"] = job_entries[0]
    
    if "Skills" in sections:
        parsed_data["skills"] = extract_skills(sections["Skills"])
    elif parsed_data["most_recent_job"] and parsed_data["most_recent_job"]["description"]:
        # Fallback: try to extract some skills from recent job description if no skill section
        # This is less reliable. We can try a keyword approach or just use the description text.
        # For now, we won't do this to keep it simpler. User can rely on description text.
        pass

    return parsed_data