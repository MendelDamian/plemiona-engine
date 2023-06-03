import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from game.models import Player, GameSession
from game.serializers import PlayerSerializer, PlayerStartGameSessionConsumerSerializer, VillageSerializer


class GameConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = None
        self.room_name = None
        self.room_group_name = None
        self.player_group_name = None

    def connect(self):
        self.player = self.scope.get("player", None)
        if not self.player:
            return

        self.room_group_name = str(self.player.game_session.game_code)
        self.player_group_name = str(self.player.channel_name)

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        async_to_sync(self.channel_layer.group_add)(self.player_group_name, self.channel_name)
        self.accept()

        players_list = Player.objects.filter(game_session=self.player.game_session)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "players_list",
                "players_list": PlayerSerializer(players_list, many=True).data,
                "owner": PlayerSerializer(self.player.game_session.owner).data,
            },
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        command_type = text_data_json.get("type", None)

        self.player.refresh_from_db()

        if not self.player.game_session.has_started:
            return

        if command_type == "fetch_resources":
            self.player.village.update_resources()
            self.fetch_resources(self.player)

        elif command_type == "fetch_buildings":
            self.fetch_buildings(self.player)

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

    def fetch_resources(self, event):
        self.send(
            text_data=json.dumps(
                {
                    "type": "fetch_resources",
                    "data": self.player.village.resources,
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

        data = {
            "end_time": game_session.ended_at.isoformat(),
            "duration": int(game_session.DURATION.total_seconds()),
            "players": PlayerStartGameSessionConsumerSerializer(game_session.player_set.all(), many=True).data,
        }

        self.send(
            text_data=json.dumps(
                {
                    "type": "start_game_session",
                    "data": data,
                }
            )
        )
