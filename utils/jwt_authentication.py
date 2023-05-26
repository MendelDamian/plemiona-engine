from datetime import datetime, timedelta

import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from game.models import Player


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Extract the JWT from the Authorization header
        jwt_token = request.META.get("HTTP_AUTHORIZATION")
        if jwt_token is None:
            return None

        jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)  # clean the token

        # Decode the JWT and verify its signature
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed("Invalid signature")
        except:
            raise AuthenticationFailed("Invalid token")

        # Get the user from the database
        player_id = payload.get("player_id")
        if player_id is None:
            raise AuthenticationFailed("Player identifier not found in JWT")

        player = Player.objects.filter(id=player_id).first()
        if player is None:
            raise AuthenticationFailed("Player not found")

        # Return the player and token payload
        return player, payload

    def authenticate_header(self, request):
        return "Bearer"

    @classmethod
    def create_jwt(cls, user):
        # Create the JWT payload
        payload = {
            "user_identifier": user.username,
            "exp": int((datetime.now() + timedelta(hours=settings.JWT_CONF["TOKEN_LIFETIME_HOURS"])).timestamp()),
            # set the expiration time for 5 hour from now
            "iat": datetime.now().timestamp(),
            "username": user.username,
        }

        # Encode the JWT with your secret key
        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return jwt_token

    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace("Bearer", "").replace(" ", "")  # clean the token
        return token
