# Generated by Django 4.2.1 on 2023-06-07 21:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0013_village_is_barracks_upgrading_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="village",
            name="units_archer",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="village",
            name="units_axeman",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="village",
            name="units_spearman",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="village",
            name="units_swordman",
            field=models.IntegerField(default=0),
        ),
    ]