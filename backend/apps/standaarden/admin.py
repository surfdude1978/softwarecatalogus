from django.contrib import admin

from .models import PakketStandaard, Standaard


@admin.register(Standaard)
class StandaardAdmin(admin.ModelAdmin):
    list_display = ("naam", "type", "versie")
    list_filter = ("type",)
    search_fields = ("naam",)


@admin.register(PakketStandaard)
class PakketStandaardAdmin(admin.ModelAdmin):
    list_display = ("pakket", "standaard", "ondersteund")
    list_filter = ("ondersteund",)
