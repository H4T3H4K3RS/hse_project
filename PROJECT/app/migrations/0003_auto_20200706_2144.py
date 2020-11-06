# Generated by Django 3.0.7 on 2020-07-06 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_botkey_lang'),
    ]

    operations = [
        migrations.CreateModel(
            name='BotKeyLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(default='', max_length=64)),
                ('lang', models.CharField(max_length=4)),
            ],
        ),
        migrations.RemoveField(
            model_name='botkey',
            name='lang',
        ),
    ]