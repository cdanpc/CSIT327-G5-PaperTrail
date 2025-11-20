from django.core.management.base import BaseCommand
from forum.models import ForumTopic


class Command(BaseCommand):
    help = 'Populate forum with predefined CS/IT topics'

    def handle(self, *args, **options):
        topics_data = [
            {
                'name': 'Programming Languages',
                'description': 'Discuss Python, Java, JavaScript, C++, and other programming languages'
            },
            {
                'name': 'Web Development',
                'description': 'Frontend, backend, full-stack development, frameworks, and best practices'
            },
            {
                'name': 'Database & SQL',
                'description': 'Database design, SQL queries, NoSQL, optimization, and data modeling'
            },
            {
                'name': 'Algorithms & Data Structures',
                'description': 'Algorithm design, complexity analysis, trees, graphs, sorting, searching'
            },
            {
                'name': 'Software Engineering',
                'description': 'Design patterns, SDLC, Agile, testing, version control, and best practices'
            },
            {
                'name': 'Computer Networks',
                'description': 'TCP/IP, HTTP, network security, protocols, and network architecture'
            },
            {
                'name': 'Operating Systems',
                'description': 'OS concepts, processes, threads, memory management, file systems'
            },
            {
                'name': 'Cybersecurity',
                'description': 'Security principles, cryptography, ethical hacking, and vulnerability assessment'
            },
            {
                'name': 'Artificial Intelligence & Machine Learning',
                'description': 'ML algorithms, deep learning, neural networks, AI applications'
            },
            {
                'name': 'Career & Learning Resources',
                'description': 'Job hunting tips, study resources, certifications, and career advice'
            },
        ]

        created_count = 0
        for topic_data in topics_data:
            topic, created = ForumTopic.objects.get_or_create(
                name=topic_data['name'],
                defaults={'description': topic_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created topic: {topic.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Topic already exists: {topic.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Done! Created {created_count} new topics.')
        )
