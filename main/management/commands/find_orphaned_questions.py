from django.core.management.base import BaseCommand
from main.models import Question_DB
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Find, fix, or reassign questions with no professor assigned.'

    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true', help='Assign orphaned questions to the user Ashish (if found)')
        parser.add_argument('--reassign', action='store_true', help='Reassign all questions currently assigned to user "pro" to Ashish')

    def handle(self, *args, **options):
        if options['reassign']:
            pro_user = User.objects.filter(username='pro').first()
            ashish = User.objects.filter(username='Ashish').first()
            if not pro_user:
                self.stdout.write(self.style.ERROR("No user with username 'pro' found! Cannot reassign questions.")) # type: ignore
                return
            if not ashish:
                self.stdout.write(self.style.ERROR("No user with username 'Ashish' found! Cannot reassign questions.")) # type: ignore
                return
            reassigned = Question_DB.objects.filter(professor=pro_user).update(professor=ashish) # type: ignore
            self.stdout.write(self.style.SUCCESS(f'Reassigned {reassigned} questions from user pro to Ashish.')) # type: ignore
            return

        orphaned = Question_DB.objects.filter(professor=None) # type: ignore
        count = orphaned.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No orphaned questions found!')) # type: ignore
            return
        self.stdout.write(self.style.WARNING(f'Found {count} orphaned questions:')) # type: ignore
        for q in orphaned:
            self.stdout.write(f'  - Q{q.qno}: {q.question[:60]}')
        if options['fix']:
            ashish = User.objects.filter(username='Ashish').first()
            if not ashish:
                self.stdout.write(self.style.ERROR("No user with username 'Ashish' found! Cannot assign orphaned questions.")) # type: ignore
                return
            orphaned.update(professor=ashish) # type: ignore
            self.stdout.write(self.style.SUCCESS(f'Assigned {count} orphaned questions to user Ashish')) # type: ignore
        else:
            self.stdout.write(self.style.WARNING("Run with --fix to assign them to Ashish (if user exists).")) # type: ignore