# Generated by Django 3.0.2 on 2020-02-07 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flowmeter', '0006_auto_20200207_1943'),
    ]

    operations = [
        migrations.AddField(
            model_name='navigationbar',
            name='url',
            field=models.CharField(default='', max_length=128),
        ),
    ]
