# Generated by Django 3.2.4 on 2021-06-28 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='food',
            name='id',
        ),
        migrations.AlterField(
            model_name='food',
            name='barcode',
            field=models.CharField(max_length=30, primary_key=True, serialize=False),
        ),
    ]
