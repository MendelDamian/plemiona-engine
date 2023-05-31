import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from game.models import Player
from game.serializers import PlayerInListSerializer

class GameConsumer(WebsocketConsumer):
    def connect(self):
        player = self.scope.get("player", None)
        if not player:
            self.close()
            return

        self.room_group_name = player.game_session.game_code

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        self.send_players_list(player.game_session)

    def players_list(self, event):
        players_list = event["players_list"]
        owner = event["owner"]

        players_list_serializer = PlayerInListSerializer(players_list, many=True)
        owner_serializer = PlayerInListSerializer(owner)

        data = {
            "owner": owner_serializer.data,
            "players": players_list_serializer.data
        }
        self.send(text_data=json.dumps({
            "type": "players_list",
            "data": data
        }))

    def start_game_session(self, event):
        self.send(text_data=json.dumps({
            "type": "start_game_session"
        }))

    def village_data(self, village):
        self.send(text_data=json.dumps({
            "type": "village_data",
            "data": {
                "resources": village.resources,
                "town_hall": village.town_hall,
                "granary": village.granary,
                "iron_mine": village.iron_mine,
                "clay_pit": village.clay_pit,
                "sawmill": village.sawmill,
                "barracks": village.barracks
            }
        }))

    def send_players_list(self, game_session):
        players_list = Player.objects.filter(game_session=game_session)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "players_list",
                "players_list": players_list,
                "owner": game_session.owner
            }
        )

    def send_start_game_session(self):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "start_game_session"
            }
        )
