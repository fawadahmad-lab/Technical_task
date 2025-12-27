import re

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters (keep basic punctuation)
    text = re.sub(r'[^\w\s.,!?\-]', ' ', text)
    
    # Normalize line breaks
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Trim
    text = text.strip()
    
    return text

def validate_file_type(filename: str, allowed_types: list) -> bool:
    """Validate file type"""
    return any(filename.lower().endswith(ext) for ext in allowed_types)