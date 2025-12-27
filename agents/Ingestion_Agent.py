import PyPDF2
import os

class IngestionAgent:
    """Agent 1: Handles file parsing & text extraction"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg']
    
    def extract_text(self, filepath: str) -> str:
        """Extract text from PDF or image - ENHANCED VERSION"""
        file_ext = os.path.splitext(filepath)[1].lower()
        filename = os.path.basename(filepath)
        
        print(f"Processing: {filename} ({file_ext})")
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(filepath)
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            return self._process_image(filename, filepath)
        else:
            return f"File: {filename}. Content will be processed."
    
    def _process_image(self, filename: str, filepath: str) -> str:
        """Process image with OCR and intelligent description"""
        
        # Try OCR first - this is the actual content
        ocr_text = self._try_ocr(filepath)
        
        # Create semantic description from filename
        semantic_description = self._analyze_filename(filename)
        
        # Build comprehensive text representation
        result_parts = []
        
        # Add semantic description
        result_parts.append(f"IMAGE FILE: {filename}")
        result_parts.append(f"Description: {semantic_description}")
        
        # Add OCR text if available
        if ocr_text and len(ocr_text.strip()) > 0:
            result_parts.append(f"\nEXTRACTED TEXT FROM IMAGE:")
            result_parts.append(ocr_text)
            result_parts.append(f"\n[OCR Status: Text successfully extracted from image]")
        else:
            result_parts.append(f"\n[OCR Status: No text detected in image]")
        
        # Add searchable keywords
        keywords = self._extract_keywords(filename)
        if keywords:
            result_parts.append(f"\nKeywords: {', '.join(keywords)}")
        
        full_text = "\n".join(result_parts)
        print(f"Image processing result length: {len(full_text)} characters")
        
        return full_text
    
    def _analyze_filename(self, filename: str) -> str:
        """Analyze filename to understand image content"""
        filename_lower = filename.lower()
        
        descriptions = []
        
        # Check for common patterns
        if "genai" in filename_lower or "gen-ai" in filename_lower:
            descriptions.append("Generative AI related content")
        if "ai" in filename_lower and "genai" not in filename_lower:
            descriptions.append("Artificial Intelligence content")
        if "business" in filename_lower and "model" in filename_lower:
            descriptions.append("Business model or strategic planning document")
        if "canvas" in filename_lower:
            descriptions.append("Canvas-style framework or diagram")
        if "polyglot" in filename_lower or "connect" in filename_lower:
            descriptions.append("Multi-language or connectivity platform")
        if "screenshot" in filename_lower:
            descriptions.append("Screenshot of application or interface")
        if "diagram" in filename_lower or "chart" in filename_lower:
            descriptions.append("Visual diagram or chart")
        if "architecture" in filename_lower:
            descriptions.append("System or software architecture diagram")
        if "task" in filename_lower or "technical" in filename_lower:
            descriptions.append("Technical documentation or task specification")
        
        if descriptions:
            return "This image contains: " + "; ".join(descriptions)
        else:
            return "Image file for visual reference"
    
    def _extract_keywords(self, filename: str) -> list:
        """Extract searchable keywords from filename"""
        import re
        
        # Remove file extension
        name_without_ext = os.path.splitext(filename)[0]
        
        # Split on common separators
        words = re.split(r'[_\-\s\.]+', name_without_ext.lower())
        
        # Filter out very short words and common stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if len(w) > 2 and w not in stopwords]
        
        return keywords
    
    def _try_ocr(self, filepath: str) -> str:
        """Try OCR with better error handling and feedback"""
        try:
            import pytesseract
            from PIL import Image
            
            # Set Tesseract path for Windows
            if os.name == 'nt':
                tesseract_paths = [
                    r"D:\Softwares_Downloaded\tesseract.exe",
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                ]
                for path in tesseract_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        print(f"Using Tesseract at: {path}")
                        break
            
            print(f"Attempting OCR on {os.path.basename(filepath)}...")
            image = Image.open(filepath)
            
            # Try OCR with better configuration
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Clean the text
            text = text.strip()
            
            if text and len(text) > 5:  # Meaningful text
                print(f"OCR successful: extracted {len(text)} characters")
                return text
            else:
                print("OCR completed but no meaningful text found")
                return ""
            
        except ImportError:
            print("WARNING: pytesseract not installed. Install with: pip install pytesseract")
            print("Also install Tesseract-OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
            return ""
        except Exception as e:
            print(f"OCR error: {str(e)}")
            return ""
    
    def _extract_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return f"PDF content could not be extracted. Error: {str(e)}"
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        import re
        # Preserve structure but remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 newlines
        text = re.sub(r' +', ' ', text)  # Single spaces
        return text.strip()