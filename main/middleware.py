"""
Custom middleware for error handling and logging
"""
import logging
import traceback
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import DatabaseError
import json

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to handle exceptions and provide consistent error responses
    """
    
    def process_exception(self, request, exception):
        """
        Handle exceptions and return appropriate responses
        """
        logger.error(f"Exception in {request.path}: {str(exception)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Handle specific exception types
        if isinstance(exception, PermissionDenied):
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Permission denied',
                    'message': 'You do not have permission to access this resource',
                    'code': 'PERMISSION_DENIED'
                }, status=403)
            else:
                # For non-API requests, let Django handle it normally
                return None
        
        elif isinstance(exception, ValidationError):
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Validation error',
                    'message': str(exception),
                    'code': 'VALIDATION_ERROR'
                }, status=400)
            else:
                return None
        
        elif isinstance(exception, DatabaseError):
            logger.critical(f"Database error in {request.path}: {str(exception)}")
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Database error',
                    'message': 'An internal error occurred. Please try again later.',
                    'code': 'DATABASE_ERROR'
                }, status=500)
            else:
                return None
        
        # For other exceptions in API endpoints
        elif request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred. Please try again later.',
                'code': 'INTERNAL_ERROR'
            }, status=500)
        
        # For non-API requests, let Django handle exceptions normally
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers
    """
    
    def process_response(self, request, response):
        """
        Add security headers to response
        """
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy - Use settings or default
        from django.conf import settings
        
        if hasattr(settings, 'CSP_DEFAULT_SRC'):
            if settings.DEBUG:
                # Relaxed CSP for development
                csp = "default-src 'self' *; script-src 'self' 'unsafe-inline' *; style-src 'self' 'unsafe-inline' *; img-src 'self' data: *; font-src 'self' *; connect-src 'self' *; frame-ancestors 'none';"
            else:
                # Production CSP
                default_src = ' '.join(settings.CSP_DEFAULT_SRC)
                script_src = ' '.join(settings.CSP_SCRIPT_SRC)
                style_src = ' '.join(settings.CSP_STYLE_SRC)
                img_src = ' '.join(settings.CSP_IMG_SRC)
                font_src = ' '.join(settings.CSP_FONT_SRC)
                
                csp = f"default-src {default_src}; script-src {script_src}; style-src {style_src}; img-src {img_src}; font-src {font_src}; connect-src 'self'; frame-ancestors 'none';"
            
            response['Content-Security-Policy'] = csp
        else:
            # Fallback CSP
            csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';"
            response['Content-Security-Policy'] = csp
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log requests and responses
    """
    
    def process_request(self, request):
        """
        Log incoming request
        """
        logger.info(f"Request: {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}")
        
        # Log request data for POST requests (excluding sensitive data)
        if request.method == 'POST' and request.path != '/':
            try:
                # Get POST data excluding passwords
                post_data = dict(request.POST)
                if 'password' in post_data:
                    post_data['password'] = '***HIDDEN***'
                logger.debug(f"POST data: {json.dumps(post_data, default=str)}")
            except Exception as e:
                logger.warning(f"Could not log POST data: {e}")
    
    def process_response(self, request, response):
        """
        Log response
        """
        logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
        return response
