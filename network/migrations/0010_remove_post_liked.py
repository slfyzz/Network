# Generated by Django 3.0.8 on 2020-07-28 20:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0009_post_liked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='liked',
        ),
    ]
