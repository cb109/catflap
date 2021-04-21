from django.contrib import admin
from server.catflap.models import CatFlap, Event, ManualStatusUpdate


class CatFlapAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "cat_name",
        "cat_inside",
        "created_at",
        "modified_at",
        "id",
    )
    readonly_fields = (
        "created_at",
        "modified_at",
    )
    search_fields = ("name",)


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "catflap",
        "kind",
        "created_at",
        "modified_at",
        "id",
    )
    autocomplete_fields = ("catflap",)
    readonly_fields = (
        "created_at",
        "modified_at",
    )


class ManualStatusUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "catflap_name",
        "cat_inside",
        "created_at",
        "modified_at",
        "id",
    )
    autocomplete_fields = ("catflap",)
    readonly_fields = (
        "created_at",
        "modified_at",
    )

    def catflap_name(self, update):
        return update.catflap.name


admin.site.site_header = "Catflap Admin"
admin.site.register(CatFlap, CatFlapAdmin)
admin.site.register(ManualStatusUpdate, ManualStatusUpdateAdmin)
admin.site.register(Event, EventAdmin)
