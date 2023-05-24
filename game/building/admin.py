from django.contrib import admin

from game.building import models


class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "level")
    list_filter = ("name", "level")
    search_fields = ("name", "level")


admin.site.register(models.TownHall, BuildingAdmin)
admin.site.register(models.ClayPit, BuildingAdmin)
admin.site.register(models.Granary, BuildingAdmin)
admin.site.register(models.IronMine, BuildingAdmin)
admin.site.register(models.Sawmill, BuildingAdmin)
admin.site.register(models.Barracks, BuildingAdmin)
