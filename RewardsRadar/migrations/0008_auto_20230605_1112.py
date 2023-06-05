# Generated by Django 3.2 on 2023-06-05 11:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('RewardsRadar', '0007_auto_20230602_1406'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rewardtier',
            name='price',
        ),
        migrations.AddField(
            model_name='rewardtier',
            name='points_required',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.PositiveIntegerField(default=0)),
                ('tier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='RewardsRadar.rewardtier')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]