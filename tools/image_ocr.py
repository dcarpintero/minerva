from PIL import Image
import pytesseract

class ImageOCR:
    """A class to handle OCR (Optical Character Recognition) operations."""
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from image using OCR.
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"Error in text extraction: {str(e)}"