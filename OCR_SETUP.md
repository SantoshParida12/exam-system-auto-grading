# OCR (Optical Character Recognition) Setup Guide

This guide will help you set up the OCR functionality for image-to-text conversion in the exam system.

## Features Added

1. **Image Upload**: Students can upload images of handwritten answers
2. **OCR Processing**: Automatic text extraction from uploaded images
3. **Real-time Preview**: Image preview with OCR results
4. **Professor View**: Professors can see both original images and extracted text
5. **API Endpoint**: REST API for OCR processing

## Prerequisites

### 1. Install Tesseract OCR

#### Windows:
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR`
3. Add to PATH environment variable
4. Restart your terminal/IDE

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS:
```bash
brew install tesseract
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

The following packages will be installed:
- `Pillow==9.5.0` - Image processing
- `pytesseract==0.3.10` - Python wrapper for Tesseract
- `opencv-python==4.8.0.76` - Computer vision library
- `numpy==1.24.3` - Numerical computing

## Configuration

### 1. Media Settings

Ensure your Django settings include proper media configuration:

```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 2. URL Configuration

Add media URLs to your main URLs file:

```python
# urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your existing URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Usage

### For Students

1. **During Exam**: 
   - Students can type text answers OR upload image files
   - Supported formats: JPEG, PNG, BMP (Max 10MB)
   - Images are automatically processed with OCR

2. **Image Upload Tips**:
   - Ensure good lighting
   - Use clear handwriting
   - Avoid shadows and glare
   - Keep the image focused and readable

### For Professors

1. **Grading**: 
   - View both original images and OCR-extracted text
   - OCR text helps with quick reading and searching
   - Original images are preserved for verification

2. **Evaluation Interface**:
   - Navigate to Exam → Evaluate Exam
   - See student answers with OCR text highlighted

## API Usage

### OCR Endpoint

```
POST /student/api/ocr/
Content-Type: multipart/form-data

Parameters:
- image: Image file (JPEG, PNG, BMP)

Response:
{
    "text": "Extracted text from image",
    "success": true
}
```

### Example Usage

```javascript
// JavaScript example for real-time OCR
const formData = new FormData();
formData.append('image', imageFile);

fetch('/student/api/ocr/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('OCR Text:', data.text);
    } else {
        console.error('OCR Error:', data.error);
    }
});
```

## Troubleshooting

### Common Issues

1. **Tesseract not found**:
   - Ensure Tesseract is installed and in PATH
   - Restart your terminal/IDE after installation

2. **Poor OCR results**:
   - Check image quality (resolution, lighting, focus)
   - Ensure handwriting is clear and legible
   - Try different image formats

3. **Import errors**:
   - Verify all Python packages are installed
   - Check Python environment and virtual environment

4. **File upload issues**:
   - Check file size limits (10MB max)
   - Verify supported file formats
   - Ensure proper media directory permissions

### Testing OCR

You can test the OCR functionality using the management command:

```bash
python manage.py shell
```

```python
from student.utils import extract_text_from_image
from django.core.files.uploadedfile import SimpleUploadedFile

# Test with a sample image
with open('test_image.jpg', 'rb') as f:
    image_file = SimpleUploadedFile('test.jpg', f.read())
    text, error = extract_text_from_image(image_file)
    print(f"Extracted text: {text}")
    print(f"Error: {error}")
```

## Security Considerations

1. **File Validation**: All uploaded files are validated for type and size
2. **Path Traversal**: File paths are sanitized to prevent directory traversal
3. **Temporary Files**: OCR processing uses temporary files that are cleaned up
4. **User Permissions**: Only authenticated students can upload answers

## Performance Notes

1. **Image Processing**: Large images may take longer to process
2. **OCR Accuracy**: Depends on image quality and handwriting clarity
3. **Storage**: Images are stored in the media directory
4. **Caching**: Consider implementing caching for frequently accessed OCR results

## Future Enhancements

1. **Language Support**: Add support for multiple languages
2. **Batch Processing**: Process multiple images simultaneously
3. **Machine Learning**: Improve OCR accuracy with custom training
4. **Real-time Processing**: Client-side OCR for immediate feedback
5. **Cloud OCR**: Integration with cloud-based OCR services

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all dependencies are properly installed
3. Test with a simple, clear image first
4. Check Django logs for detailed error messages
5. Ensure proper file permissions on media directory 