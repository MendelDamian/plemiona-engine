import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from game.serializers import PlayerSerializer, PlayerStartGameSessionConsumerSerializer, VillageSerializer


class GameConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = None
        self.game_session = None
        self.room_name = None
        self.room_group_name = None
        self.player_group_name = None

    def connect(self):
        self.player = self.scope.get("player", None)
        if not self.player:
            return

        first_connection = not self.player.is_connected
        if not self.player.is_connected:
            self.player.is_connected = True
            self.player.save()

        self.game_session = self.player.game_session

        self.room_group_name = str(self.player.game_session.game_code)
        self.player_group_name = str(self.player.channel_name)

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        async_to_sync(self.channel_layer.group_add)(self.player_group_name, self.channel_name)
        self.accept()

        if first_connection:
            players_list = self.player.game_session.player_set.all()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "players_list",
                    "players_list": PlayerSerializer(players_list, many=True).data,
                    "owner": PlayerSerializer(self.player.game_session.owner).data,
                },
            )
        else:
            self.players_list(
                {
                    "players_list": [PlayerSerializer(self.player).data],
                    "owner": PlayerSerializer(self.player.game_session.owner).data,
                }
            )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)
        async_to_sync(self.channel_layer.group_discard)(self.player_group_name, self.channel_name)

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
        self.game_session.refresh_from_db()
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
        self.player.refresh_from_db()
        self.send(
            text_data=json.dumps(
                {
                    "type": "fetch_resources",
                    "data": self.player.village.resources,
                }
            )
        )

    def fetch_buildings(self, event):
        self.player.refresh_from_db()
        self.send(
            text_data=json.dumps(
                {
                    "type": "fetch_buildings",
                    "data": VillageSerializer(self.player.village).data,
                }
            )
        )

    def start_game_session(self, event):
        self.game_session.refresh_from_db()
        data = {
            "end_time": self.game_session.ended_at.isoformat(),
            "duration": int(self.game_session.DURATION.total_seconds()),
            "players": PlayerStartGameSessionConsumerSerializer(self.game_session.player_set.all(), many=True).data,
        }

        self.send(
            text_data=json.dumps(
                {
                    "type": "start_game_session",
                    "data": data,
                }
            )
        )
