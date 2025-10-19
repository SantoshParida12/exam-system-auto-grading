# Exam System API Documentation

## Overview

This document provides comprehensive API documentation for the Django-based Exam System with Auto-Grading functionality.

## Table of Contents

1. [Authentication](#authentication)
2. [Models](#models)
3. [Views](#views)
4. [API Endpoints](#api-endpoints)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Security](#security)

## Authentication

The system uses Django's built-in authentication system with role-based access control.

### User Roles
- **Professor**: Can create exams, questions, and view results
- **Student**: Can take exams and view their results
- **Admin**: Full system access

### Authentication Flow
1. User submits credentials via POST to `/`
2. System validates credentials
3. Redirects based on user role:
   - Professor → `/prof/`
   - Student → `/student/`
   - Admin → `/admin/`

## Models

### Core Models

#### Question_DB
```python
class Question_DB(models.Model):
    professor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    qno = models.AutoField(primary_key=True)
    question = models.TextField(max_length=1000)
    question_type = models.CharField(max_length=20, choices=[('SUBJECTIVE', 'Subjective')])
    question_image = models.ImageField(upload_to='question_images/', null=True, blank=True)
```

#### Exam_Model
```python
class Exam_Model(models.Model):
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    total_marks = models.IntegerField()
    duration = models.IntegerField()
    question_paper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE)
    student_group = models.ManyToManyField(Special_Students)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
```

#### SubjectiveAnswer
```python
class SubjectiveAnswer(models.Model):
    question = models.ForeignKey(Question_DB, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    image_answer = models.ImageField(upload_to='subjective_answers/', blank=True, null=True)
    ocr_text = models.TextField(blank=True, null=True)
    marks = models.IntegerField(default=0)
    max_marks = models.IntegerField(default=5)
    feedback = models.TextField(blank=True, null=True)
    is_auto_graded = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
```

## Views

### Main Views

#### `index(request)`
**Purpose**: Handle user login and authentication

**Method**: POST/GET

**Parameters**:
- `username` (string): User's username
- `password` (string): User's password

**Response**:
- Success: Redirect to appropriate dashboard
- Failure: Return login page with error message

#### `logoutUser(request)`
**Purpose**: Handle user logout

**Method**: GET

**Response**: Redirect to login page

### Professor Views

#### `add_question(request)`
**Purpose**: Create new questions

**Method**: POST/GET

**Parameters**:
- `question` (string): Question text
- `question_type` (string): Type of question
- `question_image` (file, optional): Image file

**Response**:
- Success: Redirect to questions list
- Failure: Return form with validation errors

#### `view_exams(request)`
**Purpose**: Display and manage exams

**Method**: GET

**Response**: HTML page with exams list

#### `create_exam(request)`
**Purpose**: Create new exam

**Method**: POST

**Parameters**:
- `name` (string): Exam name
- `total_marks` (integer): Total marks
- `duration` (integer): Duration in minutes
- `question_paper` (integer): Question paper ID
- `student_group` (list): Student group IDs
- `start_time` (datetime): Exam start time
- `end_time` (datetime): Exam end time

### Student Views

#### `exams(request)`
**Purpose**: Display available exams for student

**Method**: GET

**Response**: HTML page with available exams

#### `take_exam(request, exam_id)`
**Purpose**: Display exam paper for taking

**Method**: GET

**Parameters**:
- `exam_id` (integer): Exam ID

**Response**: HTML page with exam questions

#### `submit_exam(request)`
**Purpose**: Submit exam answers

**Method**: POST

**Parameters**:
- `question_id` (integer): Question ID
- `text_answer` (string, optional): Text answer
- `image_answer` (file, optional): Image file

## API Endpoints

### OCR API

#### `POST /student/api/ocr/`
**Purpose**: Extract text from uploaded image

**Parameters**:
- `image` (file): Image file to process

**Response**:
```json
{
    "success": true,
    "text": "Extracted text from image",
    "confidence": 0.85
}
```

**Error Response**:
```json
{
    "success": false,
    "error": "Error message",
    "text": ""
}
```

### Results API

#### `GET /student/api/results/<int:student_id>/`
**Purpose**: Get student results

**Parameters**:
- `student_id` (integer): Student ID

**Response**:
```json
{
    "student": {
        "id": 1,
        "username": "student1",
        "email": "student@example.com"
    },
    "results": [
        {
            "exam": "Midterm Exam",
            "score": 85,
            "total_marks": 100,
            "percentage": 85.0,
            "grade": "A",
            "completed_at": "2023-12-01T10:30:00Z"
        }
    ]
}
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
    "error": "Error message",
    "details": "Detailed error information",
    "code": "ERROR_CODE"
}
```

### Common Error Codes

- `INVALID_CREDENTIALS`: Invalid username/password
- `EXAM_NOT_FOUND`: Exam doesn't exist
- `QUESTION_NOT_FOUND`: Question doesn't exist
- `INVALID_FILE_FORMAT`: Unsupported file format
- `FILE_TOO_LARGE`: File exceeds size limit
- `OCR_FAILED`: OCR processing failed

## Rate Limiting

### Current Implementation
- No rate limiting implemented
- **Recommendation**: Implement rate limiting for API endpoints

### Suggested Rate Limits
- Login attempts: 5 per minute per IP
- OCR requests: 10 per minute per user
- File uploads: 20 per hour per user

## Security

### Authentication Security
- Uses Django's built-in authentication
- Passwords are hashed using PBKDF2
- Session-based authentication

### File Upload Security
- File type validation
- File size limits (5MB max)
- Filename sanitization
- Path traversal protection

### CSRF Protection
- CSRF tokens required for all POST requests
- CSRF middleware enabled

### Content Security Policy
```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://stackpath.bootstrapcdn.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")
```

## Performance Considerations

### Database Optimization
- Indexes on frequently queried fields
- Efficient query patterns
- Pagination for large datasets

### File Handling
- Asynchronous OCR processing (planned)
- Image compression and optimization
- Temporary file cleanup

### Caching
- No caching currently implemented
- **Recommendation**: Implement Redis caching for:
  - User sessions
  - Exam data
  - OCR results

## Deployment

### Environment Variables
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Use production database (PostgreSQL/MySQL)
- [ ] Configure static file serving
- [ ] Set up SSL/TLS
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Implement backup strategy

## Testing

### Test Coverage
- Unit tests for models
- Integration tests for views
- API endpoint tests
- Security tests

### Running Tests
```bash
python manage.py test
python manage.py test main.tests
python manage.py test student.tests
```

## Monitoring and Logging

### Log Levels
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about system operation
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical error messages

### Log Files
- `logs/django.log`: Application logs
- Console output for development

## Support and Maintenance

### Common Issues
1. **OCR not working**: Check Tesseract installation
2. **File upload failures**: Check file size and format
3. **Performance issues**: Check database indexes
4. **Login issues**: Verify user groups and permissions

### Maintenance Tasks
- Regular database backups
- Log file rotation
- Security updates
- Performance monitoring
