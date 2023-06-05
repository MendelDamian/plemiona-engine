from typing import Optional

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from game import models, serializers


class GameSessionConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name: Optional[str] = None
        self.player: Optional[models.Player] = None
        self.player_channel_name: Optional[str] = None

    async def connect(self):
        self.player = self.scope.get("player", None)
        if not self.player:
            return

        first_connection = not self.player.is_connected
        if not self.player.is_connected:
            self.player.is_connected = True
            await self.player.asave()

        self.room_group_name = await self.get_room_group_name()
        self.player_channel_name = str(self.player.channel_name)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(self.player_channel_name, self.channel_name)
        await self.accept()

        players = await self.get_game_session_players()
        owner = await self.get_owner()

        data = {
            "type": "players_list",
            "data": {
                "owner": owner,
                "players": players,
            },
        }

        if first_connection:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_message",
                    "data": data,
                },
            )
        else:
            await self.send_message(
                {
                    "type": "players_list",
                    "data": data,
                }
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.player_channel_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        has_started = self.player.game_session.has_started
        if not has_started:
            return

        command_type = content.get("type", None)

        if not self.player:
            return

        await self.player.arefresh_from_db()

        if command_type == "fetch_resources":
            await self.send_message(
                {
                    "type": "fetch_resources",
                    "data": await self.update_resources(),
                }
            )

        if command_type == "fetch_buildings":
            await self.send_message(
                {
                    "type": "fetch_buildings",
                    "data": await self.get_village(),
                }
            )

    async def send_message(self, event):
        await self.send_json(event["data"])

    @database_sync_to_async
    def get_room_group_name(self):
        return str(self.player.game_session.game_code)

    @database_sync_to_async
    def get_game_session_players(self):
        return serializers.PlayerInLobbySerializer(self.player.game_session.player_set.all(), many=True).data

    @database_sync_to_async
    def get_owner(self):
        return serializers.PlayerInLobbySerializer(self.player.game_session.owner).data

    @database_sync_to_async
    def update_resources(self):
        self.player.village.update_resources()
        return serializers.ResourcesSerializer(self.player.village).data

    @database_sync_to_async
    def get_village(self):
        return serializers.VillageSerializer(self.player.village).data
