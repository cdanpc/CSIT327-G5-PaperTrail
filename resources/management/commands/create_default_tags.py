from django.core.management.base import BaseCommand
from resources.models import Tag


class Command(BaseCommand):
    help = 'Create default tags for the resource system'

    def handle(self, *args, **options):
        default_tags = [
            # Academic Subjects
            'Mathematics',
            'Physics',
            'Chemistry',
            'Biology',
            'Computer Science',
            'Engineering',
            'Economics',
            'Business',
            'Psychology',
            'History',
            'Literature',
            'Philosophy',
            
            # Resource Types
            'Tutorial',
            'Lecture Notes',
            'Study Guide',
            'Practice Problems',
            'Solutions',
            'Cheat Sheet',
            'Reference',
            'Lab Report',
            'Research Paper',
            'Presentation',
            
            # Difficulty Levels
            'Beginner',
            'Intermediate',
            'Advanced',
            
            # Other Categories
            'Exam Prep',
            'Final Review',
            'Midterm',
            'Assignment Help',
            'Project',
            'Code Examples',
            'Video Resource',
            'Interactive',
        ]
        
        created_count = 0
        existing_count = 0
        
        for tag_name in default_tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'[+] Created tag: {tag_name}'))
            else:
                existing_count += 1
                self.stdout.write(self.style.WARNING(f'[-] Tag already exists: {tag_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} tags'))
        self.stdout.write(self.style.WARNING(f'Already existed: {existing_count} tags'))
        self.stdout.write(self.style.SUCCESS(f'Total tags in database: {Tag.objects.count()}'))

