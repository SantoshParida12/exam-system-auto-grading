# Exam System with Auto-Grading

A comprehensive Django-based exam system with automated grading for subjective answers using OCR and TF-IDF similarity analysis.

## 🚀 Features

### For Professors
- **Create Exams**: Set up exams with multiple questions
- **Reference Answers**: Add reference answers (text or image) for auto-grading
- **View Results**: Monitor student performance with detailed analytics
- **Auto-Grading**: System automatically grades student answers using AI

### For Students
- **Take Exams**: Submit answers via text or image upload
- **Real-time Results**: View graded results immediately after submission
- **OCR Processing**: Handwritten answers are automatically converted to text
- **Detailed Feedback**: Receive encouraging, constructive feedback for each answer

## 🛠️ Technology Stack

- **Backend**: Django 3.x
- **Database**: SQLite (can be configured for PostgreSQL/MySQL)
- **OCR**: Tesseract for image-to-text conversion
- **AI Grading**: TF-IDF similarity analysis
- **Frontend**: Bootstrap, HTML, CSS, JavaScript
- **Image Processing**: PIL/Pillow

## 📋 Prerequisites

- Python 3.7+
- Tesseract OCR
- Django 3.x
- Required Python packages (see requirements.txt)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd new-exam1
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🎯 Quick Start

### 1. Set Up Professors and Students

1. Go to Django admin panel (`http://localhost:8000/admin/`)
2. Create user groups: "Professor" and "Student"
3. Add users to appropriate groups

### 2. Create Reference Answers

1. Navigate to "Reference Answers" in admin
2. Add reference answers for each question:
   - **Text answers**: Direct text input
   - **Image answers**: Upload handwritten reference images
   - **OCR processing**: Automatic text extraction from images

### 3. Create Exams

1. Create questions in "Question_DB"
2. Create question papers with selected questions
3. Create exams with question papers and time limits

### 4. Students Take Exams

1. Students log in and see available exams
2. Submit answers via text or image upload
3. System automatically processes and grades answers
4. Results are displayed immediately

## 🔧 Auto-Grading System

### How It Works

1. **Text Answers**: Direct comparison with reference answers
2. **Image Answers**: 
   - OCR processing extracts text from images
   - Extracted text is compared with reference answers
   - Similarity score calculated using TF-IDF

### Grading Scale

| Similarity Score | Marks | Feedback |
|------------------|-------|----------|
| 0.9 - 1.0 | 5/5 | Outstanding! Your answer matches the reference almost perfectly. |
| 0.8 - 0.9 | 4/5 | Great job! Your answer is very similar to the reference. |
| 0.6 - 0.8 | 3/5 | Good effort! Your answer covers many key points. |
| 0.4 - 0.6 | 2/5 | Some relevant content, but more detail is needed. |
| 0.2 - 0.4 | 1/5 | Some relevant content, but more detail is needed. |
| 0.0 - 0.2 | 0/5 | Your answer needs significant improvement. Please review the topic. |

### Feedback System

- **Encouraging messages** based on performance
- **Color-coded scores** for easy understanding
- **Detailed feedback** for improvement
- **Works for both text and image answers**

## 📁 Project Structure

```
new-exam1/
├── main/                    # Core exam functionality
│   ├── models/             # Database models
│   ├── admin.py            # Admin interface
│   └── views/              # Professor views
├── student/                # Student functionality
│   ├── views/              # Student views
│   ├── templates/          # Student templates
│   └── utils.py            # OCR and grading utilities
├── prof/                   # Professor interface
│   ├── views/              # Professor views
│   └── templates/          # Professor templates
├── media/                  # Uploaded files
│   ├── subjective_answers/ # Student answer images
│   └── reference_answers/  # Reference answer images
└── staticfiles/            # Static files
```

## 🔍 Key Models

### Question_DB
- Stores exam questions
- Supports multiple question types

### ReferenceAnswer
- Reference answers for auto-grading
- Supports text and image answers
- Automatic OCR processing

### SubjectiveAnswer
- Student submitted answers
- Text and image support
- OCR text storage
- Automated marks and feedback

### StuExam_DB
- Student exam attempts
- Completion status
- Calculated scores

## 🧪 Testing

### Run Test Scripts

```bash
# Test auto-grading system
python test_auto_grading.py

# Test feedback levels
python test_feedback_levels.py

# Test image processing
python test_image_grading.py

# Check system status
python check_auto_grading_status.py
```

### Manual Testing

1. **Create test data**:
   ```bash
   python create_reference_answer.py
   ```

2. **Test exam workflow**:
   - Create exam with questions
   - Add reference answers
   - Submit student answers
   - Check auto-grading results

## 🔧 Configuration

### Settings

Key settings in `portal/settings.py`:

```python
# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### OCR Configuration

The system uses Tesseract OCR. Ensure it's properly installed and accessible in your system PATH.

## 🚀 Deployment

### Production Setup

1. **Configure database** (PostgreSQL recommended)
2. **Set up static files**:
   ```bash
   python manage.py collectstatic
   ```
3. **Configure environment variables**
4. **Set up web server** (Nginx + Gunicorn)

### Environment Variables

```bash
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

## 📊 Monitoring and Maintenance

### Regular Tasks

1. **Clean up old files**: Remove old answer images
2. **Monitor OCR accuracy**: Review failed OCR attempts
3. **Update reference answers**: Improve grading accuracy
4. **Backup database**: Regular backups

### Troubleshooting

#### OCR Issues
- Ensure Tesseract is installed correctly
- Check image quality and format
- Verify file permissions

#### Grading Issues
- Check reference answers exist
- Verify question relationships
- Review similarity thresholds

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review test scripts for examples
- Contact the development team

## 🔄 Updates

### Recent Updates
- Enhanced feedback system with encouraging messages
- Improved OCR processing for image answers
- Color-coded result display
- Auto-grading for both text and image answers

### Planned Features
- Multiple reference answers per question
- Advanced similarity algorithms
- Export results to PDF
- Real-time exam monitoring

---

**Happy Grading! 🎓✨**
