# Generated by Django 3.0.1 on 2020-04-14 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_auto_20200414_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='code',
            name='activate',
            field=models.BooleanField(default=0),
        ),
    ]
