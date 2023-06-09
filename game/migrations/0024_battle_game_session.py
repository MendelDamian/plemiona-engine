# Generated by Django 4.2.1 on 2023-06-18 19:37

from django.db import migrations, models
import django.db.models.deletion


def populate_game_session_field_to_existing_battle_records(apps, schema_editor):
    Battle = apps.get_model("game", "Battle")
    for battle in Battle.objects.all():
        battle.game_session = battle.attacker.game_session
        battle.save()


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0023_alter_battle_unique_together"),
    ]

    operations = [
        migrations.AddField(
            model_name="battle",
            name="game_session",
            field=models.ForeignKey(
                db_index=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="battles",
                to="game.gamesession",
            ),
        ),
        migrations.RunPython(populate_game_session_field_to_existing_battle_records, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="battle",
            name="game_session",
            field=models.ForeignKey(
                db_index=True,
                null=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="battles",
                to="game.gamesession",
            ),
        ),
    ]
