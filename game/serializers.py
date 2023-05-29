from rest_framework import serializers

from game.models import Player


class PlayerInListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'nickname']


class PlayerInGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'nickname', 'resources', 'town_hall', 'granary', 'iron_mine', 'clay_pit', 'sawmill', 'barracks']


class CreateGameSessionSerializer(serializers.Serializer):
    nickname = serializers.CharField(
        max_length=Player.NICKNAME_MAX_LENGTH, min_length=Player.NICKNAME_MIN_LENGTH, required=True
    )
    game_code = serializers.CharField(max_length=6, required=False, allow_blank=True)
