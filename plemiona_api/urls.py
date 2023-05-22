"""
URL configuration for plemiona_api project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/game/", include("game.urls", namespace="game")),
]
