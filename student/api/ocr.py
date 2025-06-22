from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ..utils import extract_text_from_image, validate_image_file
import json

@method_decorator(csrf_exempt, name='dispatch')
class OCRView(APIView):
    """
    API endpoint for OCR processing of uploaded images
    """
    
    def post(self, request):
        try:
            if 'image' not in request.FILES:
                return Response({
                    'error': 'No image file provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            image_file = request.FILES['image']
            
            # Validate image file
            is_valid, error_msg = validate_image_file(image_file)
            if not is_valid:
                return Response({
                    'error': error_msg
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract text using OCR
            ocr_text, ocr_error = extract_text_from_image(image_file)
            
            if ocr_error:
                return Response({
                    'error': f'OCR processing failed: {ocr_error}',
                    'text': ''
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'text': ocr_text,
                'success': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Unexpected error: {str(e)}',
                'text': ''
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 