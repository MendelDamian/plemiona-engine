from django.urls import path

from game import views

app_name = "game"

urlpatterns = [
    path("", views.CreateJoinGameSessionView.as_view(), name="create_join_game_session"),
    path("start/", views.StartGameSessionView.as_view(), name="start_game_session"),
    path("building/<str:building_name>/upgrade/", views.UpgradeBuildingView.as_view(), name="upgrade_building"),
    path("train_units/", views.TrainUnitsView.as_view(), name="train_units"),
    path("attack/<int:defender_id>/", views.AttackPlayerView.as_view(), name="attack_player"),
]
