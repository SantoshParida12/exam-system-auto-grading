from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    if request.method == "POST":
        try:
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "")
            
            if not username or not password:
                messages.error(request, 'Please provide both username and password.')
                return render(request, 'main/login.html')
            
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    if user.is_superuser or user.is_staff:
                        return redirect('/admin')
                    
                    if user.groups.filter(name='Professor').exists():
                        return redirect('prof:index')
                    
                    return redirect('student:index')
                else:
                    messages.error(request, 'Your account is inactive. Please contact an administrator.')
            else:
                messages.error(request, 'Invalid username or password.')

        except Exception as e:
            logger.error(f"Login error: {e}")
            messages.error(request, 'An error occurred during login. Please try again.')

        return render(request, 'main/login.html')

    return render(request, 'main/login.html')


def logoutUser(request):
    try:
        logout(request)
        messages.success(request, "You have been logged out successfully.")
    except Exception as e:
        logger.error(f"Logout error: {e}")
        messages.error(request, "An error occurred during logout.")
    return redirect('main:index')  # Redirects to login page