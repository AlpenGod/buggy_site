# Generated by Django 3.1.2 on 2020-11-15 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_message_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='name',
        ),
    ]
