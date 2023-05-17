from django.test import TestCase

from game.models import Player, GameSession, Village


class PlayerTestCase(TestCase):
    def setUp(self):
        GameSession.objects.create(id=1, name="Session1")
        Village.objects.create(id=1)
        Player.objects.create(id=1, nickname="Player1", game_session_id=1, village_id=1)

    def test_player_nickname(self):
        player = Player.objects.get(id=1)
        self.assertEqual(player.nickname, "Player1")

    def test_player_game_session(self):
        player = Player.objects.get(id=1)
        self.assertEqual(player.game_session_id, 1)

    def test_player_village(self):
        player = Player.objects.get(id=1)
        self.assertEqual(player.village_id, 1)
