# Generated by Django 4.2.2 on 2023-07-03 05:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Logger',
        ),
        migrations.DeleteModel(
            name='UserComments',
        ),
    ]
