# Generated by Django 4.0.6 on 2022-09-05 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('immersioned', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notes',
            name='data',
            field=models.TextField(blank=True, null=True),
        ),
    ]
