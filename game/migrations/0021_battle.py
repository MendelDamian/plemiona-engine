# Generated by Django 4.2.2 on 2023-06-09 19:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('game', '0020_task_game_session'),
    ]

    operations = [
        migrations.CreateModel(
            name='Battle',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('battle_time', models.DateTimeField()),
                ('return_time', models.DateTimeField(null=True)),
                ('attacker_spearman_count', models.IntegerField(default=0)),
                ('attacker_swordsman_count', models.IntegerField(default=0)),
                ('attacker_axeman_count', models.IntegerField(default=0)),
                ('attacker_archer_count', models.IntegerField(default=0)),
                ('defender_spearman_count', models.IntegerField(default=0)),
                ('defender_swordsman_count', models.IntegerField(default=0)),
                ('defender_axeman_count', models.IntegerField(default=0)),
                ('defender_archer_count', models.IntegerField(default=0)),
                ('plundered_wood', models.FloatField(default=0)),
                ('plundered_clay', models.FloatField(default=0)),
                ('plundered_iron', models.FloatField(default=0)),
                ('left_attacker_spearman_count', models.IntegerField(default=0)),
                ('left_attacker_swordsman_count', models.IntegerField(default=0)),
                ('left_attacker_axeman_count', models.IntegerField(default=0)),
                ('left_attacker_archer_count', models.IntegerField(default=0)),
                ('left_defender_spearman_count', models.IntegerField(default=0)),
                ('left_defender_swordsman_count', models.IntegerField(default=0)),
                ('left_defender_axeman_count', models.IntegerField(default=0)),
                ('left_defender_archer_count', models.IntegerField(default=0)),
                ('attacker_lost_morale', models.IntegerField(default=0)),
                ('defender_lost_morale', models.IntegerField(default=0)),
                ('attacker',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battles_as_attacker',
                                   to='game.player')),
                ('defender',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battles_as_defender',
                                   to='game.player')),
            ],
            options={
                'unique_together': {('attacker', 'defender')},
            },
        ),
    ]
