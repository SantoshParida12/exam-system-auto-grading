"""
Unit tests for main app views
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.contrib.messages import get_messages
from main.models import Question_DB
import logging

logger = logging.getLogger(__name__)


class MainViewsTest(TestCase):
    """Test cases for main app views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create groups
        self.professor_group = Group.objects.create(name="Professor")
        self.student_group = Group.objects.create(name="Student")
        
        # Create test users
        self.professor = User.objects.create_user(
            username='test_professor',
            email='prof@test.com',
            password='testpass123'
        )
        self.professor.groups.add(self.professor_group)
        
        self.student = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='testpass123'
        )
        self.student.groups.add(self.student_group)
        
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
    
    def test_login_page_get(self):
        """Test GET request to login page"""
        response = self.client.get(reverse('main:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')
        self.assertContains(response, 'Sign in to your Exam Portal account')
    
    def test_login_success_professor(self):
        """Test successful login for professor"""
        response = self.client.post(reverse('main:index'), {
            'username': 'test_professor',
            'password': 'testpass123'
        })
        
        self.assertRedirects(response, reverse('prof:index'))
    
    def test_login_success_student(self):
        """Test successful login for student"""
        response = self.client.post(reverse('main:index'), {
            'username': 'test_student',
            'password': 'testpass123'
        })
        
        self.assertRedirects(response, reverse('student:index'))
    
    def test_login_success_admin(self):
        """Test successful login for admin"""
        response = self.client.post(reverse('main:index'), {
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        self.assertRedirects(response, '/admin')
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('main:index'), {
            'username': 'test_professor',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
    
    def test_login_empty_credentials(self):
        """Test login with empty credentials"""
        response = self.client.post(reverse('main:index'), {
            'username': '',
            'password': ''
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please provide both username and password')
    
    def test_login_inactive_user(self):
        """Test login with inactive user"""
        self.professor.is_active = False
        self.professor.save()
        
        response = self.client.post(reverse('main:index'), {
            'username': 'test_professor',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your account is inactive')
    
    def test_logout_functionality(self):
        """Test logout functionality"""
        # Login first
        self.client.login(username='test_professor', password='testpass123')
        
        # Test logout
        response = self.client.get(reverse('main:logoutUser'))
        
        self.assertRedirects(response, reverse('main:index'))
    
    def test_logout_not_logged_in(self):
        """Test logout when not logged in"""
        response = self.client.get(reverse('main:logoutUser'))
        
        self.assertRedirects(response, reverse('main:index'))
    
    def test_login_csrf_protection(self):
        """Test CSRF protection on login form"""
        # Create a client without CSRF tokens
        client = Client(enforce_csrf_checks=True)
        
        response = client.post(reverse('main:index'), {
            'username': 'test_professor',
            'password': 'testpass123'
        })
        
        # Should get CSRF error (403)
        self.assertEqual(response.status_code, 403)


class MainViewsSecurityTest(TestCase):
    """Test security aspects of main views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create groups and users
        self.professor_group = Group.objects.create(name="Professor")
        self.professor = User.objects.create_user(
            username='test_professor',
            email='prof@test.com',
            password='testpass123'
        )
        self.professor.groups.add(self.professor_group)
    
    def test_sql_injection_attempt(self):
        """Test SQL injection protection"""
        malicious_input = "'; DROP TABLE auth_user; --"
        
        response = self.client.post(reverse('main:index'), {
            'username': malicious_input,
            'password': 'testpass123'
        })
        
        # Should not crash and should return login page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
    
    def test_xss_protection(self):
        """Test XSS protection in login form"""
        xss_payload = "<script>alert('XSS')</script>"
        
        response = self.client.post(reverse('main:index'), {
            'username': xss_payload,
            'password': 'testpass123'
        })
        
        # Should not execute script and should return login page
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<script>')
    
    def test_brute_force_protection(self):
        """Test basic brute force protection"""
        # Attempt multiple failed logins
        for i in range(5):
            response = self.client.post(reverse('main:index'), {
                'username': 'test_professor',
                'password': f'wrongpassword{i}'
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Invalid username or password')


class MainViewsPerformanceTest(TestCase):
    """Test performance aspects of main views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create many users for performance testing
        self.professor_group = Group.objects.create(name="Professor")
        for i in range(100):
            user = User.objects.create_user(
                username=f'prof{i}',
                email=f'prof{i}@test.com',
                password='testpass123'
            )
            user.groups.add(self.professor_group)
    
    def test_login_performance_with_many_users(self):
        """Test login performance with many users in database"""
        import time
        
        start_time = time.time()
        
        response = self.client.post(reverse('main:index'), {
            'username': 'prof50',
            'password': 'testpass123'
        })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (less than 1 second)
        self.assertLess(execution_time, 1.0)
        self.assertRedirects(response, reverse('prof:index'))
