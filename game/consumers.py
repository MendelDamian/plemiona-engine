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
        self.has_game_session_started: bool = False
        self.has_game_session_ended: bool = False

    async def connect(self):
        self.player = self.scope.get("player", None)
        if not self.player:
            await self.close()
            return

        self.has_game_session_started = await self.get_has_game_session_started()

        if self.has_game_session_started:
            self.has_game_session_ended = await self.get_has_game_session_ended()

        if self.has_game_session_ended:
            await self.close()
            return

        self.room_group_name = await self.get_room_group_name()
        self.player_channel_name = str(self.player.channel_name)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(self.player_channel_name, self.channel_name)
        await self.accept()

        await self._send_message_on_connect()

    async def disconnect(self, close_code):
        if not (self.room_group_name or self.player_channel_name):
            return

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.player_channel_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        command_type = content.get("type", None)

        if not self.player:
            return

        await self.player.arefresh_from_db()

        if not self.has_game_session_started:
            self.has_game_session_started = await self.get_has_game_session_started()

            if not self.has_game_session_started:
                return

        if not self.has_game_session_ended:
            self.has_game_session_ended = await self.get_has_game_session_ended()

        if self.has_game_session_ended:
            return

        if command_type == "fetch_resources":
            await self.send_json(
                {
                    "type": "fetch_resources",
                    "data": await self.update_resources(),
                }
            )

        elif command_type == "fetch_buildings":
            await self.send_json(
                {
                    "type": "fetch_buildings",
                    "data": await self.get_village(),
                }
            )

        elif command_type == "fetch_players":
            await self.send_json(
                {
                    "type": "fetch_players",
                    "data": await self.get_players_in_game(),
                }
            )

    async def send_message(self, event):
        # Should be called by group_send only
        await self.send_json(event["data"])

    async def _send_message_on_connect(self):
        if self.has_game_session_started:
            await self.send_json(
                {
                    "type": "fetch_game_session_state",
                    "data": {
                        "players": await self.get_players_in_game(),
                        "owner": await self.get_owner(),
                        "endedAt": await self.get_game_session_ended_at(),
                        "battleLog": await self.get_battle_log(),
                        **await self.get_village(),
                        **await self.update_resources(),
                        **await self.get_units(),
                    },
                }
            )
        else:
            players = await self.get_players_in_lobby()
            owner = await self.get_owner()

            data = {
                "type": "players_list",
                "data": {
                    "owner": owner,
                    "players": players,
                },
            }

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_message",
                    "data": data,
                },
            )

    @database_sync_to_async
    def get_room_group_name(self):
        return str(self.player.game_session.game_code)

    @database_sync_to_async
    def get_players_in_lobby(self):
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

    @database_sync_to_async
    def get_has_game_session_started(self):
        return self.player.game_session.has_started

    @database_sync_to_async
    def get_game_session_ended_at(self):
        return self.player.game_session.ended_at.isoformat()

    @database_sync_to_async
    def get_has_game_session_ended(self):
        return self.player.game_session.has_ended

    @database_sync_to_async
    def get_players_in_game(self):
        return serializers.PlayerDataSerializer(self.player.game_session.player_set.all(), many=True).data

    @database_sync_to_async
    def get_units(self):
        return serializers.UnitsInVillageSerializer(self.player.village).data

    @database_sync_to_async
    def get_battle_log(self):
        battles = self.player.game_session.battles.order_by("-start_time")[:10]
        return serializers.BattleLogSerializer(battles, many=True).data
