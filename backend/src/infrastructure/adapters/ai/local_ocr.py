import logging
from PIL import Image
import pytesseract
import os

logger = logging.getLogger(__name__)

def extract_text_from_image(image_path: str) -> str:
    """
    Extracts text from an image file using Tesseract OCR.
    Assumes tesseract is installed on the system.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    try:
        # Load the image
        img = Image.open(image_path)
        
        # Use Tesseract to extract text in Spanish and English (useful for tickets)
        # --psm 4 assumes a single column of text of variable sizes
        text = pytesseract.image_to_string(img, lang='spa+eng', config='--psm 4')
        
        # Basic cleanup
        clean_text = "\n".join([line.strip() for line in text.split('\n') if line.strip()])
        logger.info(f"Successfully extracted {len(clean_text)} characters from image.")
        
        return clean_text
    
    except Exception as e:
        logger.error(f"Error extracting text from image {image_path}: {e}")
        raise
