from rest_framework import serializers

from game.models import Player


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'nickname']

class CreateGameSessionSerializer(serializers.Serializer):
    nickname = serializers.CharField(
        max_length=Player.NICKNAME_MAX_LENGTH, min_length=Player.NICKNAME_MIN_LENGTH, required=True
    )
    game_code = serializers.CharField(max_length=6, required=False, allow_blank=True)
