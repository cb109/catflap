# Generated by Django 3.1.7 on 2021-04-25 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catflap", "0010_add_catflap_related_name_events"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="kind",
            field=models.CharField(choices=[("OC", "Opened Closed")], max_length=2),
        ),
    ]
