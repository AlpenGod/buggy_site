# Generated by Django 3.1.5 on 2021-01-27 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0006_message_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='file',
            field=models.FileField(upload_to='saved_uploads/'),
        ),
    ]