from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from server.catflap.models import CatFlap, Event, ManualStatusUpdate


class CatFlapAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "cat_name",
        "cat_inside",
        "created_at",
        "modified_at",
        "uuid",
        "status_page_link",
    )
    readonly_fields = (
        "created_at",
        "modified_at",
        "uuid",
        "status_page_link",
    )
    search_fields = ("name",)

    @mark_safe
    def status_page_link(self, catflap):
        url = reverse("status", args=(catflap.uuid,))
        return f"<a href='{url}' target='blank_'>Status Page</a>"


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "catflap",
        "kind",
        "duration",
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
