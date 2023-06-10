from django.contrib import admin

from game import models


admin.site.register(models.GameSession)
admin.site.register(models.Task)
admin.site.register(models.Player)
admin.site.register(models.Village)
admin.site.register(models.Battle)
