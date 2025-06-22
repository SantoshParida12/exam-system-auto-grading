from django.core.management.base import BaseCommand
import subprocess
import sys
import platform

class Command(BaseCommand):
    help = 'Setup OCR dependencies for image-to-text conversion'

    def handle(self, *args, **options):
        self.stdout.write('Setting up OCR dependencies...')
        
        system = platform.system().lower()
        
        if system == 'windows':
            self.setup_windows()
        elif system == 'linux':
            self.setup_linux()
        elif system == 'darwin':  # macOS
            self.setup_macos()
        else:
            self.stdout.write(f'Unsupported operating system: {system}')
    
    def setup_windows(self):
        self.stdout.write('Windows detected. Please install Tesseract OCR manually:')
        self.stdout.write('1. Download from: https://github.com/UB-Mannheim/tesseract/wiki')
        self.stdout.write('2. Install to default location (C:\\Program Files\\Tesseract-OCR)')
        self.stdout.write('3. Add to PATH environment variable')
        self.stdout.write('4. Restart your terminal/IDE')
        
        # Try to install Python packages
        self.install_python_packages()
    
    def setup_linux(self):
        self.stdout.write('Linux detected. Installing Tesseract OCR...')
        try:
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr'], check=True)
            self.stdout.write('Tesseract OCR installed successfully!')
        except subprocess.CalledProcessError as e:
            self.stdout.write(f'Failed to install Tesseract: {e}')
        
        self.install_python_packages()
    
    def setup_macos(self):
        self.stdout.write('macOS detected. Installing Tesseract OCR...')
        try:
            subprocess.run(['brew', 'install', 'tesseract'], check=True)
            self.stdout.write('Tesseract OCR installed successfully!')
        except subprocess.CalledProcessError as e:
            self.stdout.write(f'Failed to install Tesseract: {e}')
            self.stdout.write('Please install Homebrew first: https://brew.sh/')
        
        self.install_python_packages()
    
    def install_python_packages(self):
        self.stdout.write('Installing Python packages...')
        packages = [
            'Pillow==9.5.0',
            'pytesseract==0.3.10',
            'opencv-python==4.8.0.76',
            'numpy==1.24.3'
        ]
        
        for package in packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
                self.stdout.write(f'Installed {package}')
            except subprocess.CalledProcessError as e:
                self.stdout.write(f'Failed to install {package}: {e}')
        
        self.stdout.write('OCR setup completed! You can now use image upload with OCR.') 