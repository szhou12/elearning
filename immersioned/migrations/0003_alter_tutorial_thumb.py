# Generated by Django 4.0.5 on 2022-09-22 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('immersioned', '0002_notes_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='thumb',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
