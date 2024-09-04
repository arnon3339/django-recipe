# Generated by Django 3.2.25 on 2024-09-04 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(fields=('user', 'title'), name='by_user_title'),
        ),
    ]
