from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("flashcards", "0003_deck_bookmark_study_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="deck",
            name="tags",
            field=models.CharField(blank=True, max_length=255, help_text="Comma separated tags e.g. Math, Science"),
        ),
        migrations.AddField(
            model_name="deck",
            name="visibility",
            field=models.CharField(choices=[("public", "Public"), ("private", "Private")], default="public", max_length=10),
        ),
    ]
