# Generated by Django 3.2.5 on 2022-06-07 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0011_alter_worker_sal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='id',
            field=models.CharField(max_length=200, primary_key=True, serialize=False),
        ),
    ]
