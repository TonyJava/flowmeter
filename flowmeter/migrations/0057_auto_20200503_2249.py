# Generated by Django 3.0.2 on 2020-05-03 22:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flowmeter', '0056_auto_20200503_2249'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='unexecutedopr',
            options={'ordering': ['-opr_time']},
        ),
        migrations.AlterIndexTogether(
            name='unexecutedopr',
            index_together={('dtu_no', 'address', 'opr_type')},
        ),
    ]
