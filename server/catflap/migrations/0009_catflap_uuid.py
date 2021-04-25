# Generated by Django 3.1.7 on 2021-04-23 19:15

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catflap", "0008_manualstatusupdate_cat_inside"),
    ]

    operations = [
        migrations.AddField(
            model_name="catflap",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]