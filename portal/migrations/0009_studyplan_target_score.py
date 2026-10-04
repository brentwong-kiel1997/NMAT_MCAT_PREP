from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0008_aiquiz"),
    ]

    operations = [
        migrations.AddField(
            model_name="studyplan",
            name="target_score",
            field=models.PositiveIntegerField(
                null=True, blank=True,
                help_text="Target GPS-equivalent score (NMAT 200-800 scale); "
                          "drives the readiness readout on the dashboard",
            ),
        ),
    ]
