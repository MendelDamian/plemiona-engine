from django.urls import path

from game import views

app_name = "game"

urlpatterns = [
    path("game/", views.CreateJoinGameSessionView.as_view(), name="create_join_game_session"),
]
