# Generated by Django 3.0.7 on 2020-07-06 17:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_profile_lang'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='lang',
        ),
    ]