import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import os
from django.conf import settings
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import json
import re
from main.models.reference_answer import ReferenceAnswer
from student.models import SubjectiveAnswer

logger = logging.getLogger(__name__)

# Configure pytesseract to use the correct Tesseract path on Windows
if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    """
    Preprocess image for better OCR results
    """
    try:
        # Read image using opencv
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply dilation to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        gray = cv2.dilate(gray, kernel, iterations=1)
        
        # Apply median blur to remove noise
        gray = cv2.medianBlur(gray, 3)
        
        return gray
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return None

def preprocess_camscanner_image(image_path):
    """
    Preprocess CamScanner images for better OCR results
    """
    try:
        # Read image using opencv
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding (better for CamScanner images)
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Apply morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        
        # Apply slight blur to reduce noise
        gray = cv2.GaussianBlur(gray, (1, 1), 0)
        
        return gray
    except Exception as e:
        logger.error(f"Error preprocessing CamScanner image: {e}")
        return None

def extract_text_from_image(image_file):
    """
    Extract text from uploaded image using OCR
    """
    try:
        print(f"extract_text_from_image called with: {image_file}")
        print(f"  - File name: {image_file.name}")
        print(f"  - File size: {image_file.size}")
        
        # Save uploaded file temporarily
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_ocr_image.jpg')
        print(f"  - Temp path: {temp_path}")
        
        # Convert uploaded file to PIL Image
        pil_image = Image.open(image_file)
        print(f"  - PIL Image mode: {pil_image.mode}")
        print(f"  - PIL Image size: {pil_image.size}")
        
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
            print(f"  - Converted to RGB")
        
        # Save temporarily
        pil_image.save(temp_path)
        print(f"  - Saved to temp file")
        
        # Try multiple OCR configurations for better results
        ocr_configs = [
            '--psm 6',  # Assume uniform block of text
            '--psm 8',  # Single word
            '--psm 13', # Raw line
            '--psm 6 --oem 3',  # Default OCR Engine Mode
            '--psm 8 --oem 3',  # Single word with default engine
        ]
        
        best_text = ""
        best_config = ""
        
        for config in ocr_configs:
            try:
                print(f"  - Trying OCR config: {config}")
                text = pytesseract.image_to_string(pil_image, config=config)
                text = text.strip()
                
                print(f"  - OCR result with {config}: '{text[:100]}...'")
                
                # Choose the result with the most text (likely the best)
                if len(text) > len(best_text):
                    best_text = text
                    best_config = config
                    
            except Exception as e:
                print(f"  - OCR failed with {config}: {e}")
                continue
        
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"  - Temp file cleaned up")
        
        if best_text:
            # Clean extracted text
            best_text = '\n'.join([line.strip() for line in best_text.split('\n') if line.strip()])
            print(f"  - Best OCR result (config: {best_config}): '{best_text[:100]}...'")
            return best_text, None
        else:
            print(f"  - No text extracted with regular OCR, trying CamScanner preprocessing...")
            # Try with CamScanner preprocessing
            processed_img = preprocess_camscanner_image(temp_path)
            
            if processed_img is not None:
                print(f"  - CamScanner preprocessing successful")
                # Try OCR with preprocessed image
                for config in ocr_configs:
                    try:
                        print(f"  - Trying preprocessed OCR config: {config}")
                        text = pytesseract.image_to_string(processed_img, config=config)
                        text = text.strip()
                        
                        print(f"  - Preprocessed OCR result with {config}: '{text[:100]}...'")
                        
                        if len(text) > len(best_text):
                            best_text = text
                            best_config = f"preprocessed_{config}"
                            
                    except Exception as e:
                        print(f"  - Preprocessed OCR failed with {config}: {e}")
                        continue
                
                if best_text:
                    best_text = '\n'.join([line.strip() for line in best_text.split('\n') if line.strip()])
                    print(f"  - Best preprocessed OCR result (config: {best_config}): '{best_text[:100]}...'")
                    return best_text, None
            
            print(f"  - No text extracted with any OCR configuration")
            return None, "OCR failed to extract any text from the image"
        
    except Exception as e:
        print(f"  - Exception in extract_text_from_image: {e}")
        logger.error(f"Error extracting text from image: {e}")
        # Clean up temporary file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return None, str(e)

def validate_image_file(image_file):
    """
    Validate uploaded image file
    """
    try:
        # Check file size (max 10MB)
        if image_file.size > 10 * 1024 * 1024:
            return False, "Image file size must be less than 10MB"
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp']
        if image_file.content_type not in allowed_types:
            return False, "Only JPEG, PNG, and BMP images are allowed"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Error validating image file: {e}")
        return False, "Error validating image file"

def preprocess_text_for_tfidf(text):
    """
    Preprocess text for TF-IDF analysis
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep spaces and basic punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\!\?]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def generate_tfidf_vector(text):
    """
    Generate TF-IDF vector for given text
    """
    try:
        print(f"generate_tfidf_vector called with: '{text[:100]}...'")
        
        if not text:
            print("  - No text provided")
            return None
        
        # Preprocess text
        processed_text = preprocess_text_for_tfidf(text)
        print(f"  - Preprocessed text: '{processed_text[:100]}...'")
        
        if not processed_text:
            print("  - No processed text")
            return None
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=1.0  # Changed from 0.95 to 1.0 for single document
        )
        
        # Fit and transform the text
        tfidf_matrix = vectorizer.fit_transform([processed_text])
        print(f"  - TF-IDF matrix shape: {tfidf_matrix.shape}") # type: ignore
        
        # Convert to dense array and then to list for JSON serialization
        tfidf_vector = tfidf_matrix.toarray()[0].tolist()  # type: ignore
        
        # Store feature names for later use
        feature_names = vectorizer.get_feature_names_out().tolist()
        
        result = {
            'vector': tfidf_vector,
            'feature_names': feature_names,
            'text': processed_text
        }
        
        print(f"  - TF-IDF vector generated successfully")
        print(f"  - Vector length: {len(tfidf_vector)}")
        print(f"  - Feature count: {len(feature_names)}")
        
        return result
        
    except Exception as e:
        print(f"  - Error generating TF-IDF vector: {e}")
        logger.error(f"Error generating TF-IDF vector: {e}")
        return None

def calculate_similarity_score(student_text, reference_text):
    """
    Calculate similarity score between student answer and reference answer using TF-IDF
    """
    try:
        if not student_text or not reference_text:
            return 0.0
        
        # Preprocess both texts
        student_processed = preprocess_text_for_tfidf(student_text)
        reference_processed = preprocess_text_for_tfidf(reference_text)
        
        if not student_processed or not reference_processed:
            return 0.0
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=1.0  # Changed from 0.95 to 1.0 for single document
        )
        
        # Fit and transform both texts
        tfidf_matrix = vectorizer.fit_transform([student_processed, reference_processed])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
        
    except Exception as e:
        logger.error(f"Error calculating similarity score: {e}")
        return 0.0

def grade_answer(student_answer, reference_answers):
    """
    Grade student answer against reference answers using TF-IDF similarity
    Returns: (marks, feedback, best_match_reference) where marks is 0-5
    """
    try:
        if not student_answer:
            return 0, "No answer provided", None
        
        # Get student text (either direct text or OCR text)
        student_text = ""
        if hasattr(student_answer, 'text_answer') and student_answer.text_answer:
            student_text = student_answer.text_answer
        elif hasattr(student_answer, 'ocr_text') and student_answer.ocr_text:
            student_text = student_answer.ocr_text
        else:
            return 0, "No text content found in answer", None
        
        if not student_text.strip():
            return 0, "No text content found in answer", None
        
        best_score = 0.0
        best_feedback = ""
        best_reference = None
        
        # Compare with each reference answer
        for ref_answer in reference_answers:
            ref_text = ""
            
            # Get reference text (either direct text or OCR text)
            if ref_answer.text_answer:
                ref_text = ref_answer.text_answer
            elif ref_answer.ocr_text:
                ref_text = ref_answer.ocr_text
            
            if not ref_text.strip():
                continue
            
            # Calculate similarity score
            similarity_score = calculate_similarity_score(student_text, ref_text)
            
            if similarity_score > best_score:
                best_score = similarity_score
                best_reference = ref_answer
                
                # Generate feedback based on score
                if similarity_score >= 0.9:
                    best_feedback = "Outstanding! Your answer matches the reference almost perfectly."
                elif similarity_score >= 0.7:
                    best_feedback = "Great job! Your answer is very similar to the reference."
                elif similarity_score >= 0.5:
                    best_feedback = "Good effort! Your answer covers many key points."
                elif similarity_score >= 0.3:
                    best_feedback = "Some relevant content, but more detail is needed."
                else:
                    best_feedback = "Your answer needs significant improvement. Please review the topic."
        
        # Convert similarity score to marks (0-5)
        # 0.0-0.2 = 0 marks (Very poor)
        # 0.2-0.4 = 1 mark (Poor)
        # 0.4-0.6 = 2 marks (Below average)
        # 0.6-0.8 = 3 marks (Fair)
        # 0.8-0.9 = 4 marks (Good)
        # 0.9-1.0 = 5 marks (Excellent)
        
        if best_score >= 0.9:
            marks = 5
        elif best_score >= 0.8:
            marks = 4
        elif best_score >= 0.6:
            marks = 3
        elif best_score >= 0.4:
            marks = 2
        elif best_score >= 0.2:
            marks = 1
        else:
            marks = 0
        
        # Ensure feedback is always provided
        if not best_feedback:
            if best_score == 0.0:
                best_feedback = "No reference answers available for comparison, or answer content does not match expected format."
            else:
                best_feedback = "Answer has been processed and graded based on available reference material."
        
        return marks, best_feedback, best_reference
        
    except Exception as e:
        logger.error(f"Error grading answer: {e}")
        return 0, f"Error during grading: {str(e)}", None

def calculate_total_marks(student, exam):
    """
    Calculate total marks for all subjective answers in an exam
    """
    try:
        # Get all subjective answers for this student and exam
        subjective_answers = SubjectiveAnswer.objects.filter( # type: ignore    
            student=student,
            question__in=exam.questions.all()
        )
        
        total_marks = 0
        total_questions = 0
        
        for answer in subjective_answers:
            total_marks += answer.marks
            total_questions += 1
        
        return total_marks, total_questions
        
    except Exception as e:
        logger.error(f"Error calculating total marks: {e}")
        return 0, 0

def get_reference_answers_for_question(question):
    """
    Get all reference answers for a given question
    """
    try:
        return ReferenceAnswer.objects.filter(question=question) # type: ignore
    except Exception as e:
        logger.error(f"Error getting reference answers: {e}")
        return [] 