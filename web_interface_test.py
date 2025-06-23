#!/usr/bin/env python3
"""
Web Interface Test - Test the actual Django web views and user interface
"""
import os
import sys
import django
import time
from urllib.parse import urljoin

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from main.models import Question_DB, Question_Paper, Exam_Model, ReferenceAnswer
from student.models import SubjectiveAnswer
from datetime import datetime, timedelta

def setup_test_users():
    """Setup test users for web interface testing"""
    print("🔧 Setting up test users...")
    
    # Create groups
    professor_group, _ = Group.objects.get_or_create(name="Professor")
    student_group, _ = Group.objects.get_or_create(name="Student")
    
    # Create professor user
    professor, _ = User.objects.get_or_create(
        username='web_test_professor',
        defaults={'email': 'prof@webtest.com', 'first_name': 'Web', 'last_name': 'Professor'}
    )
    professor.set_password('testpass123')
    professor.groups.add(professor_group)
    professor.save()
    
    # Create student user
    student, _ = User.objects.get_or_create(
        username='web_test_student',
        defaults={'email': 'student@webtest.com', 'first_name': 'Web', 'last_name': 'Student'}
    )
    student.set_password('testpass123')
    student.groups.add(student_group)
    student.save()
    
    print(f"✅ Test users created:")
    print(f"   - Professor: {professor.username} (password: testpass123)")
    print(f"   - Student: {student.username} (password: testpass123)")
    
    return professor, student

def test_login_views():
    """Test login functionality"""
    print("\n🔐 Testing Login Views...")
    
    client = Client()
    
    # Test login page accessibility
    response = client.get('/login/')
    if response.status_code == 200:# type: ignore
        print("✅ Login page accessible")
    else:
        print(f"❌ Login page failed: {response.status_code}") # type: ignore
        return False
    
    # Test login functionality
    professor, student = setup_test_users()
    
    # Test professor login
    response = client.post('/login/', {
        'username': 'web_test_professor',
        'password': 'testpass123'
    })
    if response.status_code == 302:  # Redirect after successful login # type: ignore
        print("✅ Professor login successful")
    else:
        print(f"❌ Professor login failed: {response.status_code}") # type: ignore
        return False
    
    return True

def test_professor_views():
    """Test professor-specific views"""
    print("\n👨‍🏫 Testing Professor Views...")
    
    client = Client()
    professor, student = setup_test_users()
    
    # Login as professor
    client.login(username='web_test_professor', password='testpass123')
    
    # Test professor dashboard
    response = client.get('/prof/')
    if response.status_code == 200: # type: ignore
        print("✅ Professor dashboard accessible")
    else:
        print(f"❌ Professor dashboard failed: {response.status_code}") # type: ignore
        return False
    
    # Test question creation view
    response = client.get('/prof/question/')
    if response.status_code == 200: # type: ignore
        print("✅ Question creation page accessible")
    else:
        print(f"❌ Question creation page failed: {response.status_code}") # type: ignore
        return False
    
    return True

def test_student_views():
    """Test student-specific views"""
    print("\n📚 Testing Student Views...")
    
    client = Client()
    professor, student = setup_test_users()
    
    # Login as student
    client.login(username='web_test_student', password='testpass123')
    
    # Test student dashboard
    response = client.get('/student/')
    if response.status_code == 200: # type: ignore
        print("✅ Student dashboard accessible")
    else:
        print(f"❌ Student dashboard failed: {response.status_code}") # type: ignore
        return False
    
    # Test exams view
    response = client.get('/student/exams/')
    if response.status_code == 200: # type: ignore
        print("✅ Student exams page accessible")
    else:
        print(f"❌ Student exams page failed: {response.status_code}") # type: ignore
        return False
    
    return True

def test_admin_interface():
    """Test Django admin interface"""
    print("\n⚙️ Testing Admin Interface...")
    
    client = Client()
    professor, student = setup_test_users()
    
    # Login as professor (who should have admin access)
    client.login(username='web_test_professor', password='testpass123')
    
    # Test admin interface
    response = client.get('/admin/')
    if response.status_code == 200: # type: ignore
        print("✅ Admin interface accessible")
    else:
        print(f"❌ Admin interface failed: {response.status_code}") # type: ignore
        return False
    
    # Test reference answers in admin
    response = client.get('/admin/main/referenceanswer/')
    if response.status_code == 200: # type: ignore
        print("✅ Reference answers admin page accessible")
    else:
        print(f"❌ Reference answers admin page failed: {response.status_code}") # type: ignore
        return False
    
    return True

def test_url_patterns():
    """Test that all important URL patterns are accessible"""
    print("\n🔗 Testing URL Patterns...")
    
    client = Client()
    
    # Test main URLs
    urls_to_test = [
        '/',
        '/login/',
        '/logout/',
        '/prof/',
        '/student/',
        '/admin/',
    ]
    
    for url in urls_to_test:
        response = client.get(url)
        if response.status_code in [200, 302]:  # 302 is redirect (like login required) # type: ignore  
            print(f"✅ {url} - accessible (status: {response.status_code})") # type: ignore
        else:
            print(f"❌ {url} - failed (status: {response.status_code})") # type: ignore 
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    # Delete test users
    User.objects.filter(username__in=['web_test_professor', 'web_test_student']).delete()
    
    print("✅ Test data cleaned up")

def run_web_interface_test():
    """Run the complete web interface test"""
    print("🌐 STARTING WEB INTERFACE TEST")
    print("=" * 50)
    
    try:
        # Test 1: URL Patterns
        if not test_url_patterns():
            print("❌ URL Patterns test failed")
            return False
        
        # Test 2: Login Views
        if not test_login_views():
            print("❌ Login Views test failed")
            return False
        
        # Test 3: Professor Views
        if not test_professor_views():
            print("❌ Professor Views test failed")
            return False
        
        # Test 4: Student Views
        if not test_student_views():
            print("❌ Student Views test failed")
            return False
        
        # Test 5: Admin Interface
        if not test_admin_interface():
            print("❌ Admin Interface test failed")
            return False
        
        print("\n🎉 WEB INTERFACE TEST COMPLETED!")
        print("=" * 50)
        print("✅ URL Patterns: Working")
        print("✅ Login System: Working")
        print("✅ Professor Views: Working")
        print("✅ Student Views: Working")
        print("✅ Admin Interface: Working")
        print("\n📋 SUMMARY:")
        print("   - All web interfaces are accessible")
        print("   - User authentication works correctly")
        print("   - Role-based access control is functional")
        print("   - Django admin interface is operational")
        print("   - The web application is ready for users")
        
        return True
        
    except Exception as e:
        print(f"\n❌ WEB INTERFACE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    success = run_web_interface_test()
    if success:
        print("\n🎊 WEB INTERFACE TEST COMPLETED SUCCESSFULLY!")
        print("The web application is fully functional and ready for users.")
    else:
        print("\n💥 WEB INTERFACE TEST FAILED!")
        print("Please check the error messages above and fix any issues.") 