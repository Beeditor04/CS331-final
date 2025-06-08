from typing import Optional, List, Dict, Union
import re


async def extract_sections_from_text(text: str, sections: List[str], document_type: str = "career") -> Dict[str, str]:
    """
    Args:
        text (str): The text containing markdown-style sections.
        sections (List[str]): List of section names to extract.
        document_type (str): Type of document ("career", "funding", or "school").
    Returns:
        Dict[str, str]: A dictionary mapping section names to their extracted content.
    """
    result = {}
    
    text = text.replace('\r\n', '\n')
    
    # Create a pattern to match section headers at different levels (# or ## or ###)
    section_pattern = r'(^|\n)\s*(#+)\s*(.+?)(?=\n)'
    
    section_matches = re.finditer(section_pattern, text)
    
    # Convert matches to a list of (header_name, header_level, start_position) tuples
    headers = []
    for match in section_matches:
        header_level = len(match.group(2))
        header_name = match.group(3).strip()
        # The position right after the header line
        start_pos = match.end() + 1
        headers.append((header_name, header_level, start_pos))
    
    # Handle funding and school
    if document_type in ["school"] and headers:
        # First header is the name of the organization
        org_name = headers[0][0]
        result["Tên trường"] = org_name
    elif document_type == "funding" and headers:
        # First header is the name of the funding organization
        org_name = headers[0][0]
        result["Tên tổ chức"] = org_name
    
    for i, (header_name, header_level, start_pos) in enumerate(headers):
        for section in sections:
            # "Tên nghề:" format
            if document_type == "career" and section == "Tên nghề" and ":" in header_name and section in header_name:
                result[section] = header_name.split(":", 1)[1].strip()
                break
                
            elif section in header_name:
                end_pos = len(text)
                for j in range(i + 1, len(headers)):
                    if headers[j][1] <= header_level:  # Same or higher level header
                        end_pos = headers[j][2] - len(headers[j][0]) - headers[j][1] - 2  # Adjust for header markup
                        break
                
                content = text[start_pos:end_pos].strip()
                
                content = re.sub(r'\n+', ' ', content)
                result[section] = content
                break
    
    return result
