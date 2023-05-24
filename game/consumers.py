import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from game.models import Player
from game.serializers import PlayerSerializer

class LobbyConsumer(WebsocketConsumer):
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

        self.send_players_list(player)


    def players_list(self, event):
        players_list = event["players_list"]
        owner = event["owner"]

        players_list_serializer = PlayerSerializer(players_list, many=True)
        owner_serializer = PlayerSerializer(owner)

        data = {
            "owner": owner_serializer.data,
            "players": players_list_serializer.data
        }
        self.send(text_data=json.dumps({
            "type": "players_list",
            "data": data
        }))

    def send_players_list(self, player):
        players_list = Player.objects.filter(game_session=player.game_session)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "players_list",
                "players_list": players_list,
                "owner": player.game_session.owner
            }
        )
