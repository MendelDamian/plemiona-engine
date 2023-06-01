import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from game.models import Player, GameSession
from game.serializers import PlayerSerializer, VillageSerializer


class GameConsumer(WebsocketConsumer):
    def connect(self):
        player = self.scope.get("player", None)
        if not player:
            self.close()
            return

        self.room_group_name = player.game_session.game_code

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

        self.accept()

        players_list = Player.objects.filter(game_session=player.game_session)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "players_list",
                "players_list": players_list,
                "owner": player.game_session.owner,
            },
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        command_type = text_data_json.get("type", None)

        player = self.scope.get("player", None)
        if not player:
            self.close()
            return

        player.refresh_from_db()

        if not player.game_session.has_started:
            return

        if command_type == "fetch_resources":
            player.village.update_resources()
            player.village.save()
            self.fetch_resources(player)

        elif command_type == "fetch_buildings":
            self.fetch_buildings(player)

    def players_list(self, event):
        players_list = event["players_list"]
        owner = event["owner"]

        players_list_serializer = PlayerSerializer(players_list, many=True)
        owner_serializer = PlayerSerializer(owner)

        data = {
            "owner": owner_serializer.data,
            "players": players_list_serializer.data,
        }

        self.send(
            text_data=json.dumps(
                {
                    "type": "players_list",
                    "data": data,
                }
            )
        )

    def fetch_resources(self, player):
        self.send(
            text_data=json.dumps(
                {
                    "type": "fetch_resources",
                    "data": player.village.resources,
                }
            )
        )

    def fetch_buildings(self, player):
        player.village.refresh_from_db()

        village_serializer = VillageSerializer(player.village)
        self.send(
            text_data=json.dumps(
                {
                    "type": "fetch_buildings",
                    "data": village_serializer.data,
                }
            )
        )

    def start_game_session(self, event):
        game_session: GameSession = event["game_session"]

        self.send(
            text_data=json.dumps(
                {
                    "type": "start_game_session",
                    "data": {
                        "end_time": game_session.ended_at.isoformat(),
                    },
                }
            )
        )

    def send_start_game_session(self, game_session: GameSession):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "start_game_session",
                "game_session": game_session,
            },
        )
