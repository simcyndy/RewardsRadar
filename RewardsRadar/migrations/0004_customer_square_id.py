# Generated by Django 3.2 on 2023-06-02 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RewardsRadar', '0003_auto_20230602_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='square_id',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]
