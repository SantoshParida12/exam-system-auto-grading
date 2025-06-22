from django.core.management.base import BaseCommand
from main.models.reference_answer import ReferenceAnswer

class Command(BaseCommand):
    help = 'Process OCR for all reference answers that have images but no OCR text'

    def handle(self, *args, **options):
        self.stdout.write('Processing OCR for reference answers...')
        
        # Get all reference answers with images but no OCR text
        reference_answers = ReferenceAnswer.objects.filter( # type: ignore
            image_answer__isnull=False,
            ocr_text__isnull=True
        )
        
        self.stdout.write(f'Found {reference_answers.count()} reference answers to process')
        
        processed_count = 0
        failed_count = 0
        
        for ref_answer in reference_answers:
            self.stdout.write(f'Processing reference answer {ref_answer.pk}...')
            
            if ref_answer.process_ocr():
                ref_answer.save()
                processed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully processed OCR for reference answer {ref_answer.pk}') # type: ignore # type: ignore
                )
            else:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Failed to process OCR for reference answer {ref_answer.pk}') # type: ignore
                )
        
        self.stdout.write(
            self.style.SUCCESS( # type: ignore
                f'OCR processing complete! Processed: {processed_count}, Failed: {failed_count}' # type: ignore
            )
        ) 