# Generated by Django 3.2.5 on 2022-06-07 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0012_alter_worker_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='eff',
            field=models.FloatField(default=6),
        ),
        migrations.AlterField(
            model_name='worker',
            name='id',
            field=models.CharField(default=0, max_length=200, primary_key=True, serialize=False),
        ),
    ]