# Generated by Django 3.0.7 on 2020-07-06 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20200630_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='lang',
            field=models.CharField(default='ru', max_length=4),
            preserve_default=False,
        ),
    ]
