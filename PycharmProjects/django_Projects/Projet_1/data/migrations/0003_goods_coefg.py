# Generated by Django 4.0.4 on 2022-06-09 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_customuser_fixed_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods',
            name='coefG',
            field=models.FloatField(default=1),
        ),
    ]
