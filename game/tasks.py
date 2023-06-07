from time import sleep

from game.models import Player, GameSession
from plemiona_api.celery import app


@app.task
def upgrade_building_task(player_id, building_name, seconds):
    from game.services import GameSessionConsumerService

    player = Player.objects.get(id=player_id)
    player.village.set_building_upgrading_state(building_name, True)

    sleep(seconds)

    refreshed_player = Player.objects.get(id=player_id)
    refreshed_player.village.update_resources()

    refreshed_player.village.upgrade_building_level(building_name)
    refreshed_player.village.set_building_upgrading_state(building_name, False)

    GameSessionConsumerService.send_fetch_buildings(refreshed_player)
    GameSessionConsumerService.send_fetch_resources(refreshed_player)


@app.task
def send_leaderboard_task(game_session_id, seconds):
    from game.services import GameSessionConsumerService

    sleep(seconds)

    game_session = GameSession.objects.get(id=game_session_id)
    GameSessionConsumerService.send_leaderboard(game_session)
