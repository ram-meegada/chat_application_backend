# Generated by Django 5.1.2 on 2024-11-04 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_remove_chatstoragemodel_message_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatstoragemodel',
            name='message',
            field=models.JSONField(default=dict),
        ),
    ]
