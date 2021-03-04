from django.contrib import admin

from server.catflap.models import CatFlap


class CatFlapAdmin(admin.ModelAdmin):
    list_fields = ("name", "created_at", "modified_at", "id")


admin.site.title = "Catflap Admin"
admin.site.register(CatFlap, CatFlapAdmin)
