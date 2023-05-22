from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from game.models import Player, GameSession


class GameSessionTestCase(TestCase):
    def test_game_session_has_game_code(self):
        game_session = GameSession.objects.create()
        self.assertTrue(game_session.game_code)

    def test_game_session_has_not_started(self):
        game_session = GameSession.objects.create()
        self.assertFalse(game_session.has_started)

    def test_view_create_join_game_session_with_no_game_code_and_valid_username(self):
        response = self.client.post(reverse("game:create_join_game_session"), data={"nickname": "test"})
        game_session = GameSession.objects.last()
        player = Player.objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["game_session_id"], game_session.id)
        self.assertEqual(response.data["game_code"], game_session.game_code)
        self.assertEqual(response.data["player_id"], player.id)
        self.assertEqual(game_session.owner, player)
        self.assertIn(player, game_session.player_set.all())

    def test_view_create_join_game_session_with_no_game_code_and_invalid_username(self):
        response = self.client.post(reverse("game:create_join_game_session"), data={"nickname": "te"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_create_join_game_session_with_valid_game_code_and_valid_username(self):
        game_code = "123456"
        game_session = GameSession.objects.create(game_code=game_code)
        response = self.client.post(
            reverse("game:create_join_game_session"), data={"nickname": "test", "game_code": game_code}
        )
        player = Player.objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["game_session_id"], game_session.id)
        self.assertEqual(response.data["game_code"], game_code)
        self.assertEqual(response.data["player_id"], player.id)
        self.assertIn(player, game_session.player_set.all())

    def test_view_create_join_game_session_with_valid_game_code_and_invalid_username(self):
        game_code = "123456"
        GameSession.objects.create(game_code=game_code)
        response = self.client.post(
            reverse("game:create_join_game_session"), data={"nickname": "te", "game_code": game_code}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_create_join_game_session_with_invalid_game_code_and_valid_username(self):
        response = self.client.post(
            reverse("game:create_join_game_session"), data={"nickname": "test", "game_code": "123456"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_create_join_game_session_with_invalid_game_code_and_invalid_username(self):
        response = self.client.post(
            reverse("game:create_join_game_session"), data={"nickname": "te", "game_code": "123456"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_create_join_game_session_with_valid_game_code_and_valid_username_and_game_session_has_started(self):
        game_code = "123456"
        GameSession.objects.create(game_code=game_code, has_started=True)
        response = self.client.post(
            reverse("game:create_join_game_session"), data={"nickname": "test", "game_code": game_code}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_create_join_game_session_with_existing_game_session_and_new_player(self):
        game_code = "123456"
        game_session = GameSession.objects.create(game_code=game_code)
        game_session.owner = Player.objects.create(nickname="test", game_session=game_session)
        game_session.player_set.add(game_session.owner)
        game_session.save()

        response = self.client.post(
            reverse("game:create_join_game_session"), data={"nickname": "test2", "game_code": game_code}
        )
        player = Player.objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["game_session_id"], game_session.id)
        self.assertEqual(response.data["game_code"], game_code)
        self.assertEqual(response.data["player_id"], player.id)
        self.assertIn(player, game_session.player_set.all())

    def test_view_create_join_game_session_with_same_nickname(self):
        game_code = "123456"
        nickname = "test"
        game_session = GameSession.objects.create(game_code=game_code)
        game_session.owner = Player.objects.create(nickname=nickname, game_session=GameSession.objects.last())
        game_session.player_set.add(game_session.owner)
        game_session.save()

        response = self.client.post(
            reverse("game:create_join_game_session"), data={"nickname": nickname, "game_code": game_code}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_create_join_game_session_with_same_nickname_and_game_session_has_started(self):
        game_code = "123456"
        nickname = "test"
        game_session = GameSession.objects.create(game_code=game_code, has_started=True)
        game_session.owner = Player.objects.create(nickname=nickname, game_session=GameSession.objects.last())
        game_session.save()

        response = self.client.post(
            reverse("game:create_join_game_session"), data={"nickname": nickname, "game_code": game_code}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_create_join_game_session_with_full_game_session(self):
        game_code = "123456"
        game_session = GameSession.objects.create(game_code=game_code)
        game_session.owner = Player.objects.create(nickname="test", game_session=game_session)
        game_session.player_set.add(game_session.owner)
        game_session.save()

        for i in range(GameSession.MAXIMUM_PLAYERS):
            Player.objects.create(nickname=f"test{i}", game_session=game_session)

        response = self.client.post(
            reverse("game:create_join_game_session"), data={"nickname": "NEW_PLAYER", "game_code": game_code}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_start_game_session_as_owner(self):
        game_session = GameSession.objects.create(game_code="123456")
        player = Player.objects.create(nickname="test", game_session=game_session)
        player2 = Player.objects.create(nickname="test2", game_session=game_session)

        game_session.owner = player
        game_session.player_set.add(player, player2)
        game_session.save()

        player_token = RefreshToken.for_user(player)
        response = self.client.post(
            reverse("game:start_game_session"), headers={"Authorization": f"Bearer {player_token.access_token}"}
        )
        game_session.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(game_session.has_started)

    def test_view_start_game_session_as_not_owner(self):
        game_session = GameSession.objects.create(game_code="123456")
        player = Player.objects.create(nickname="test", game_session=game_session)
        player2 = Player.objects.create(nickname="test2", game_session=game_session)

        game_session.owner = player
        game_session.player_set.add(player, player2)
        game_session.save()

        player2_token = RefreshToken.for_user(player2)
        response = self.client.post(
            reverse("game:start_game_session"),
            headers={"Authorization": f"Bearer {player2_token.access_token}"},
        )
        game_session.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(game_session.has_started)

    def test_view_start_game_session_with_invalid_token(self):
        game_session = GameSession.objects.create(game_code="123456")
        player = Player.objects.create(nickname="test", game_session=game_session)
        player2 = Player.objects.create(nickname="test2", game_session=game_session)

        game_session.owner = player
        game_session.player_set.add(player, player2)
        game_session.save()

        response = self.client.post(
            reverse("game:start_game_session"),
            headers={"Authorization": f"Bearer invalid_token"},
        )
        game_session.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(game_session.has_started)
