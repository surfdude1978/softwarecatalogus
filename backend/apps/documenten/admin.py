from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("naam", "pakket", "type", "status", "gedeeld_met")
    list_filter = ("type", "status", "gedeeld_met")
    search_fields = ("naam", "pakket__naam")
