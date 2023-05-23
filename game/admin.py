from django.contrib import admin

from .models import GameSession, Player, Village


class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0


class GameSessionAdmin(admin.ModelAdmin):
    list_display = ("game_code", "has_started", "owner")
    inlines = [
        PlayerInline,
    ]


class PlayerAdmin(admin.ModelAdmin):
    list_display = ("nickname", "game_session", "village")


admin.site.register(GameSession, GameSessionAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Village)
