from django.contrib import admin

from server.catflap.models import CatFlap, Event


class CatFlapAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "modified_at", "id")
    search_fields = ("name",)


class EventAdmin(admin.ModelAdmin):
    list_display = ("catflap", "kind", "created_at", "modified_at", "id")
    autocomplete_fields = ("catflap",)


admin.site.title = "Catflap Admin"
admin.site.register(CatFlap, CatFlapAdmin)
admin.site.register(Event, EventAdmin)
