# Generated by Django 3.2 on 2023-06-02 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('RewardsRadar', '0006_transaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='RewardTier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('benefits', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='reward_tier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='RewardsRadar.rewardtier'),
        ),
    ]
