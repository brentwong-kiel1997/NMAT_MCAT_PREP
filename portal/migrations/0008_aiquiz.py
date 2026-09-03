import django
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0007_examresponse_is_field_test"),
    ]

    operations = [
        migrations.CreateModel(
            name="AiQuiz",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("chapter_id", models.CharField(blank=True, max_length=120)),
                ("mode", models.CharField(choices=[("chapter", "chapter-grounded"), ("misses", "miss-grounded")], default="chapter", max_length=12)),
                ("payload", models.JSONField(default=list)),
                ("bad_reports", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(default=timezone.now)),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_quizzes", to="portal.learnerprofile")),
            ],
            options={"ordering": ["-created_at"], "verbose_name": "AI quiz"},
        ),
    ]
