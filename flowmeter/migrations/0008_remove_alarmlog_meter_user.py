# Generated by Django 2.2 on 2020-02-16 21:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flowmeter', '0007_remove_alarmlog_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alarmlog',
            name='meter_user',
        ),
    ]