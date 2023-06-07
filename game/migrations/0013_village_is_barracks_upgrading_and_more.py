# Generated by Django 4.2.1 on 2023-06-06 14:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('game', '0012_player_is_connected'),
    ]

    operations = [
        migrations.AddField(
            model_name='village',
            name='is_barracks_upgrading',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='village',
            name='is_clay_pit_upgrading',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='village',
            name='is_iron_mine_upgrading',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='village',
            name='is_sawmill_upgrading',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='village',
            name='is_town_hall_upgrading',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='village',
            name='is_warehouse_upgrading',
            field=models.BooleanField(default=False),
        ),
    ]