from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0006_aiprovider_api_key_enc"),
    ]

    operations = [
        migrations.AddField(
            model_name="examresponse",
            name="is_field_test",
            field=models.BooleanField(default=False),
        ),
    ]
