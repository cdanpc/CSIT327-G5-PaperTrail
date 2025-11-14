from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_user_deletion_requested_user_deletion_requested_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudyReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='study_reminders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['completed', 'due_date', '-created_at'],
            },
        ),
    ]
