# Generated by Django 3.1.7 on 2021-08-29 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catflap", "0011_remove_unused_event_kinds"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="duration",
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]
