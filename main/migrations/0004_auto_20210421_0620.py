# Generated by Django 3.1 on 2021-04-21 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20210421_0612'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='average_rating',
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
    ]
