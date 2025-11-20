import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')
django.setup()

from forum.models import ForumTopic

# Define initial CS/IT topics
topics = [
    {
        'name': 'Data Structures & Algorithms',
        'description': 'Discuss algorithms, complexity analysis, sorting, searching, trees, graphs, and optimization techniques.'
    },
    {
        'name': 'Web Development',
        'description': 'Share knowledge about HTML, CSS, JavaScript, frameworks (React, Vue, Django, Node.js), and web design.'
    },
    {
        'name': 'Database Systems',
        'description': 'Explore SQL, NoSQL, database design, normalization, indexing, and query optimization.'
    },
    {
        'name': 'Operating Systems',
        'description': 'Discuss process management, memory management, file systems, scheduling, and system programming.'
    },
    {
        'name': 'Software Engineering',
        'description': 'Topics on SDLC, design patterns, testing, version control, agile methodologies, and project management.'
    },
    {
        'name': 'Artificial Intelligence & Machine Learning',
        'description': 'Explore neural networks, deep learning, natural language processing, computer vision, and ML algorithms.'
    },
    {
        'name': 'Cybersecurity',
        'description': 'Discuss network security, cryptography, ethical hacking, vulnerabilities, and security best practices.'
    },
    {
        'name': 'Mobile App Development',
        'description': 'Share insights on Android, iOS, React Native, Flutter, and cross-platform mobile development.'
    },
    {
        'name': 'Computer Networks',
        'description': 'Discuss protocols (TCP/IP, HTTP, DNS), routing, network architecture, and internet technologies.'
    },
    {
        'name': 'Programming Languages',
        'description': 'Explore Python, Java, C++, JavaScript, and language-specific features, syntax, and best practices.'
    }
]

print("Creating forum topics...")
created_count = 0

for topic_data in topics:
    topic, created = ForumTopic.objects.get_or_create(
        name=topic_data['name'],
        defaults={'description': topic_data['description']}
    )
    if created:
        created_count += 1
        print(f"✅ Created: {topic.name}")
    else:
        print(f"ℹ️  Already exists: {topic.name}")

print(f"\n✅ Done! {created_count} new topics created, {len(topics) - created_count} already existed.")
print(f"Total topics in database: {ForumTopic.objects.count()}")
