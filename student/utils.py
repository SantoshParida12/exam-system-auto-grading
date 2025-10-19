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
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk.stem import PorterStemmer
import math
from collections import Counter

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
    Validate uploaded image file for security and format
    """
    try:
        # Check file size (5MB limit)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if image_file.size > max_size:
            return False, "File size too large. Maximum size is 5MB."
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        file_extension = os.path.splitext(image_file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return False, "Invalid file type. Only JPG, JPEG, PNG, GIF, and BMP files are allowed."
        
        # Check filename for security (no path traversal)
        if '..' in image_file.name or '/' in image_file.name or '\\' in image_file.name:
            return False, "Invalid filename. Please use a simple filename without special characters."
        
        # Try to open the image with PIL to validate it's a real image
        try:
            from PIL import Image
            image = Image.open(image_file)
            image.verify()  # Verify it's a valid image
            
            # Reset file pointer after verification
            image_file.seek(0)
            
            # Check image dimensions (prevent extremely large images)
            image_file.seek(0)
            img = Image.open(image_file)
            if img.width > 4000 or img.height > 4000:
                return False, "Image dimensions too large. Maximum dimensions are 4000x4000 pixels."
            
            # Reset file pointer again
            image_file.seek(0)
            
        except Exception as e:
            return False, "Invalid image file. Please upload a valid image."
        
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

def preprocess_text(text, ngram_range=(1,2)):
    # Lowercase, remove punctuation, split into words, remove stopwords, apply stemming
    ps = PorterStemmer()
    tokens = re.findall(r'\b\w+\b', text.lower())
    tokens = [ps.stem(t) for t in tokens if t not in ENGLISH_STOP_WORDS]
    ngrams = []
    min_n, max_n = ngram_range
    for n in range(min_n, max_n+1):
        ngrams += [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
    return ngrams

def manual_tfidf_vectorizer(texts, ngram_range=(1,2)):
    N = len(texts)
    all_tokens = [set(preprocess_text(text, ngram_range)) for text in texts]
    vocab = set.union(*all_tokens) if all_tokens else set()
    vocab = list(vocab)
    idf = {}
    for word in vocab:
        df = sum(1 for tokens in all_tokens if word in tokens)
        idf[word] = math.log((N + 1) / (df + 1)) + 1
    tfidf_vectors = []
    for text in texts:
        tokens = preprocess_text(text, ngram_range)
        tf = Counter(tokens)
        tfidf = {word: (tf[word] / len(tokens) if len(tokens) > 0 else 0) * idf[word] for word in vocab}
        tfidf_vectors.append(tfidf)
    return tfidf_vectors, vocab

def manual_cosine_similarity(vec1, vec2, vocab):
    dot = sum(vec1[w] * vec2[w] for w in vocab)
    norm1 = math.sqrt(sum(vec1[w] ** 2 for w in vocab))
    norm2 = math.sqrt(sum(vec2[w] ** 2 for w in vocab))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def calculate_similarity_score(student_text, reference_text):
    """
    Calculate similarity score between student answer and reference answer using manual TF-IDF with n-grams
    """
    try:
        if not student_text or not reference_text:
            return 0.0
        tfidf_vectors, vocab = manual_tfidf_vectorizer([student_text, reference_text], ngram_range=(1,2))
        similarity = manual_cosine_similarity(tfidf_vectors[0], tfidf_vectors[1], vocab)
        return float(similarity)
    except Exception as e:
        logger.error(f"Error calculating similarity score: {e}")
        return 0.0

def extract_keywords(text):
    """
    Extract keywords from a text for keyword matching.
    Uses simple tokenization and removes stopwords.
    """
    ps = PorterStemmer()
    tokens = re.findall(r'\b\w+\b', text.lower())
    # Only remove short words, not stopwords
    keywords = [ps.stem(t) for t in tokens if len(t) > 2]
    print(f"[DEBUG] Extracted (stemmed, no stopwords) keywords from: '{text[:60]}...': {set(keywords)}")
    return set(keywords)

def grade_answer(student_answer, reference_answers):
    """
    Grade student answer against reference answers using TF-IDF similarity and keyword matching
    Returns: (marks, feedback, best_match_reference) where marks is 0-5
    """
    try:
        if not student_answer:
            return 0, "No answer provided", None
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
        best_keywords = set()
        for ref_answer in reference_answers:
            ref_text = ""
            if ref_answer.text_answer:
                ref_text = ref_answer.text_answer
            elif ref_answer.ocr_text:
                ref_text = ref_answer.ocr_text
            if not ref_text.strip():
                continue
            similarity_score = calculate_similarity_score(student_text, ref_text)
            ref_keywords = extract_keywords(ref_text)
            if similarity_score > best_score:
                best_score = similarity_score
                best_reference = ref_answer
                best_keywords = ref_keywords
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
        # TF-IDF based marks
        if best_score >= 0.85:
            tfidf_marks = 5
        elif best_score >= 0.7:
            tfidf_marks = 4
        elif best_score >= 0.6:
            tfidf_marks = 3
        elif best_score >= 0.4:
            tfidf_marks = 2
        elif best_score >= 0.2:
            tfidf_marks = 1
        else:
            tfidf_marks = 0
        # Cap TF-IDF score if answer is too short
        if len(student_text.split()) < 8:
            tfidf_marks = min(tfidf_marks, 2)
        
        # Absolute matched keyword based marks
        student_keywords = extract_keywords(student_text)
        matched_keywords = set()
        keyword_marks = 0
        if best_keywords:
            matched_keywords = best_keywords & student_keywords
            print(f"[DEBUG] Reference keywords: {best_keywords}")
            print(f"[DEBUG] Student keywords: {student_keywords}")
            print(f"[DEBUG] Matched keywords: {matched_keywords}")
            print(f"[DEBUG] Matched keyword count: {len(matched_keywords)}")
            if len(matched_keywords) >= 10:
                keyword_marks = 5
            elif len(matched_keywords) >= 7:
                keyword_marks = 4
            elif len(matched_keywords) >= 5:
                keyword_marks = 3
            elif len(matched_keywords) >= 3:
                keyword_marks = 2
            elif len(matched_keywords) >= 1:
                keyword_marks = 1
            else:
                keyword_marks = 0
        if len(student_text.split()) < 10:
            tfidf_marks = min(tfidf_marks, 2)
            keyword_marks = min(keyword_marks, 2)
        # Use the higher of the two
        marks = max(tfidf_marks, keyword_marks)
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