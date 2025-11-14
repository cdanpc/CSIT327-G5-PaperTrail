from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("flashcards", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="deck",
            name="category",
            field=models.CharField(
                choices=[
                    ("general", "General"),
                    ("definitions", "Definitions"),
                    ("formulas", "Formulas"),
                    ("concepts", "Concepts"),
                    ("language", "Language"),
                ],
                default="general",
                max_length=40,
            ),
        ),
    ]
