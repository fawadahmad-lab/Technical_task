import PyPDF2
import os
import re

class IngestionAgent:
    """
    Agent 1: File Ingestion & Text Extraction
    
    Purpose:
        Handles the first stage of the RAG pipeline by processing various file formats
        and extracting their textual content for downstream indexing and retrieval.
    
    What it does:
        - Accepts PDF and image files (.pdf, .png, .jpg, .jpeg)
        - Extracts text from PDFs using PyPDF2
        - Performs OCR (Optical Character Recognition) on images using Tesseract
        - Analyzes image filenames to infer content and extract metadata
        - Generates searchable keywords from filenames
        - Cleans and normalizes extracted text
        - Returns structured text representation with metadata for images
    
    Key Features:
        - Multi-format support (PDF + images)
        - Intelligent filename analysis for context inference
        - Graceful fallback when OCR is unavailable
        - Text cleaning and normalization
        - Metadata extraction for better searchability
    
    Output:
        Clean, structured text ready for chunking and embedding in the indexing stage.
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg']
    
    def extract_text(self, filepath: str) -> str:
        """Extract text from PDF or image"""
        ext = os.path.splitext(filepath)[1].lower()
        filename = os.path.basename(filepath)
        print(f"Processing: {filename}")
        
        if ext == '.pdf':
            return self._extract_pdf(filepath)
        elif ext in ['.png', '.jpg', '.jpeg']:
            return self._process_image(filename, filepath)
        return f"File: {filename}. Content will be processed."
    
    def _process_image(self, filename: str, filepath: str) -> str:
        """Process image with OCR and metadata"""
        ocr_text = self._ocr(filepath)
        description = self._analyze_filename(filename)
        keywords = self._extract_keywords(filename)
        
        parts = [
            f"IMAGE FILE: {filename}",
            f"Description: {description}",
            f"\nEXTRACTED TEXT:" if ocr_text else "\n[No text detected]",
            ocr_text if ocr_text else "",
            f"\nKeywords: {', '.join(keywords)}" if keywords else ""
        ]
        
        return "\n".join(filter(None, parts))
    
    def _analyze_filename(self, filename: str) -> str:
        """Extract content hints from filename"""
        lower = filename.lower()
        tags = {
            "genai|gen-ai": "Generative AI content",
            "business.*model": "Business model document",
            "canvas": "Canvas framework",
            "polyglot|connect": "Multi-language platform",
            "screenshot": "Application screenshot",
            "diagram|chart": "Visual diagram",
            "architecture": "Architecture diagram",
            "task|technical": "Technical documentation"
        }
        
        matches = [desc for pattern, desc in tags.items() if re.search(pattern, lower)]
        return "This image contains: " + "; ".join(matches) if matches else "Image file"
    
    def _extract_keywords(self, filename: str) -> list:
        """Extract keywords from filename"""
        name = os.path.splitext(filename)[0]
        words = re.split(r'[_\-\s\.]+', name.lower())
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        return [w for w in words if len(w) > 2 and w not in stopwords]
    
    def _ocr(self, filepath: str) -> str:
        """Attempt OCR with graceful fallback"""
        try:
            import pytesseract
            from PIL import Image
            
            if os.name == 'nt':
                paths = [r"D:\Softwares_Downloaded\tesseract.exe",
                        r"C:\Program Files\Tesseract-OCR\tesseract.exe"]
                for path in paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
            
            text = pytesseract.image_to_string(Image.open(filepath), 
                                              config='--oem 3 --psm 6').strip()
            return text if len(text) > 5 else ""
        except Exception as e:
            print(f"OCR unavailable: {e}")
            return ""
    
    def _extract_pdf(self, filepath: str) -> str:
        """Extract text from PDF"""
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(page.extract_text() for page in reader.pages)
        except Exception as e:
            return f"PDF extraction failed: {e}"
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()