# Generated by Django 3.0.7 on 2020-07-13 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20200706_2148'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='public',
            field=models.BooleanField(default=True),
        ),
    ]