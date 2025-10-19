"""
Management command to clean up old uploaded files
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up old uploaded files and temporary files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep files (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        self.stdout.write(f"Cleaning up files older than {days} days...")
        if dry_run:
            self.stdout.write("DRY RUN MODE - No files will be deleted")
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        total_size = 0
        
        # Define directories to clean
        media_dirs = [
            'subjective_answers',
            'reference_answers',
            'question_images',
        ]
        
        for media_dir in media_dirs:
            dir_path = os.path.join(settings.MEDIA_ROOT, media_dir)
            if not os.path.exists(dir_path):
                continue
                
            self.stdout.write(f"Processing {media_dir}...")
            
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                
                if os.path.isfile(file_path):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_mtime < cutoff_date:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        
                        if dry_run:
                            self.stdout.write(f"Would delete: {file_path} ({file_size} bytes)")
                        else:
                            try:
                                os.remove(file_path)
                                deleted_count += 1
                                logger.info(f"Deleted old file: {file_path}")
                            except OSError as e:
                                logger.error(f"Error deleting {file_path}: {e}")
                                self.stdout.write(
                                    self.style.ERROR(f"Error deleting {file_path}: {e}")
                                )
        
        # Clean up logs directory
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        if os.path.exists(logs_dir):
            self.stdout.write("Processing logs...")
            
            for filename in os.listdir(logs_dir):
                if filename.endswith('.log'):
                    log_path = os.path.join(logs_dir, filename)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(log_path))
                    
                    if file_mtime < cutoff_date:
                        file_size = os.path.getsize(log_path)
                        total_size += file_size
                        
                        if dry_run:
                            self.stdout.write(f"Would delete: {log_path} ({file_size} bytes)")
                        else:
                            try:
                                os.remove(log_path)
                                deleted_count += 1
                                logger.info(f"Deleted old log file: {log_path}")
                            except OSError as e:
                                logger.error(f"Error deleting {log_path}: {e}")
        
        # Summary
        size_mb = total_size / (1024 * 1024)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would delete {deleted_count} files ({size_mb:.2f} MB)")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {deleted_count} files ({size_mb:.2f} MB)")
            )
