import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from game.models import Player, GameSession
from game.serializers import PlayerInListSerializer


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

        if command_type == "update_resources":
            player = self.scope.get("player", None)
            if not player:
                self.close()
                return

            if player.game_session.has_started:
                player.village.update_resources()
                player.village.save()
                player.village.refresh_from_db()

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "update_resources",
                    "player": player,
                },
            )

    def players_list(self, event):
        players_list = event["players_list"]
        owner = event["owner"]

        players_list_serializer = PlayerInListSerializer(players_list, many=True)
        owner_serializer = PlayerInListSerializer(owner)

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

    def update_resources(self, event):
        player: Player = event["player"]
        player.village.refresh_from_db()

        data = {
            "resources": player.village.resources,
        }

        self.send(
            text_data=json.dumps(
                {
                    "type": "resources_update",
                    "data": data,
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
