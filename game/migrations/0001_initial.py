# Generated by Django 4.2.1 on 2023-05-17 08:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GameSession",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("game_code", models.CharField(max_length=6)),
                ("has_started", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Game session",
                "verbose_name_plural": "Game sessions",
            },
        ),
        migrations.CreateModel(
            name="Village",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                "verbose_name": "Village",
                "verbose_name_plural": "Villages",
            },
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nickname", models.CharField(max_length=30)),
                (
                    "game_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="game.gamesession",
                    ),
                ),
                (
                    "village",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="game.village"
                    ),
                ),
            ],
            options={
                "verbose_name": "Player",
                "verbose_name_plural": "Players",
            },
        ),
        migrations.AddField(
            model_name="gamesession",
            name="owner",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="game.player"
            ),
        ),
    ]
