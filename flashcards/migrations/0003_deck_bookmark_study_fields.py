from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("flashcards", "0002_deck_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="deck",
            name="is_bookmarked",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="deck",
            name="last_studied_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
