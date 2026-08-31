"""Rename AIProvider.api_key → api_key_enc (encrypted at rest via portal.fieldcrypto).

Existing plaintext values carry over untouched; the .api_key property falls
back to plaintext until the row is next saved, which re-encrypts it.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0005_examresponse_time_spent_reviewnote"),
    ]

    operations = [
        migrations.RenameField(
            model_name="aiprovider",
            old_name="api_key",
            new_name="api_key_enc",
        ),
        migrations.AlterField(
            model_name="aiprovider",
            name="api_key_enc",
            field=models.CharField(
                blank=True,
                help_text="Encrypted at rest; masked in UI",
                max_length=500,
            ),
        ),
    ]
