# Generated by Django 3.0.2 on 2020-02-05 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flowmeter', '0002_auto_20200205_0043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auth',
            name='remark',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='authcategory',
            name='remark',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='remark',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='remark',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
