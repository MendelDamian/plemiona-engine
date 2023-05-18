from django.urls import path

from game import views

app_name = "game"

urlpatterns = [
    path("", views.CreateJoinGameSessionView.as_view(), name="create_join_game_session"),
    path("start/", views.StartGameSessionView.as_view(), name="start_game_session")
]
