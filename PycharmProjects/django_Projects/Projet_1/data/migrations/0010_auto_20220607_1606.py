# Generated by Django 3.2.5 on 2022-06-07 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0009_rename_idt_worker_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='eff',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='worker',
            name='id',
            field=models.CharField(default='0', max_length=200, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='worker',
            name='sal',
            field=models.FloatField(),
        ),
    ]
