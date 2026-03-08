from django.contrib import admin
from .models import GemmaComponent, PakketGemmaComponent


@admin.register(GemmaComponent)
class GemmaComponentAdmin(admin.ModelAdmin):
    list_display = ("naam", "type", "archimate_id", "parent")
    list_filter = ("type",)
    search_fields = ("naam", "archimate_id")


@admin.register(PakketGemmaComponent)
class PakketGemmaComponentAdmin(admin.ModelAdmin):
    list_display = ("pakket", "gemma_component")
    search_fields = ("pakket__naam", "gemma_component__naam")
