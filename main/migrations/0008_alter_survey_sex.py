# Generated by Django 3.2.8 on 2023-12-18 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_survey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='sex',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='female', max_length=50),
        ),
    ]
