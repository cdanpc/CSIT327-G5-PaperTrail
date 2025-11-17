from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0002_quiz_is_public'),
        ('quizzes', '0002_quizbookmark'),
    ]

    operations = [
        # This merge migration resolves parallel 0002 branches.
    ]
