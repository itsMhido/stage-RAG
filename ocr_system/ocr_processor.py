import pytesseract
from PIL import Image
import cv2
import numpy as np
import os

class OCRProcessor:
    def __init__(self):
        # Configure for French and Arabic languages
        self.languages = 'fra+ara+eng'
        
    def preprocess_image(self, image_path):
        """Preprocess image for better OCR accuracy"""
        try:
            img = cv2.imread(image_path)
            
            if img is None:
                # Try with PIL if OpenCV fails
                pil_img = Image.open(image_path)
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Remove noise
            denoised = cv2.medianBlur(gray, 3)
            
            # Apply threshold to get image with only black and white
            thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Morphological operations to remove noise
            kernel = np.ones((1,1), np.uint8)
            # Use the numerical value for MORPH_OPENING for compatibility
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            return opening
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def extract_text_from_image(self, image_path):
        """Extract text from image file with French/Arabic support"""
        try:
            # Try preprocessing first
            processed_img = self.preprocess_image(image_path)
            
            if processed_img is not None:
                # OCR configuration for better accuracy
                custom_config = f'--oem 3 --psm 6 -l {self.languages}'
                text = pytesseract.image_to_string(processed_img, config=custom_config)
            else:
                # Fallback to direct OCR without preprocessing
                custom_config = f'--oem 3 --psm 6 -l {self.languages}'
                text = pytesseract.image_to_string(Image.open(image_path), config=custom_config)
            
            # Clean up the text
            cleaned_text = self.clean_extracted_text(text)
            return cleaned_text
            
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return ""
    
    def clean_extracted_text(self, text):
        """Clean and format extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace and empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Join lines with proper spacing
        cleaned_text = '\n'.join(lines)
        
        # Remove multiple consecutive spaces
        import re
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        
        return cleaned_text.strip()
