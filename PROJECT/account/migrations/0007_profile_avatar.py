# Generated by Django 3.0.7 on 2020-07-07 20:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_auto_20200707_2311'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='account.Avatar'),
            preserve_default=False,
        ),
    ]
