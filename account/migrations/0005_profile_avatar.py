# Generated by Django 3.0.7 on 2020-07-06 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_remove_profile_lang'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.IntegerField(default=1),
        ),
    ]
