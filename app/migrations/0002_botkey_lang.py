# Generated by Django 3.0.7 on 2020-07-06 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='botkey',
            name='lang',
            field=models.CharField(default='ru', max_length=4),
            preserve_default=False,
        ),
    ]