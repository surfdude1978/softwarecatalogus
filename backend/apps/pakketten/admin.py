from django.contrib import admin

from .models import Koppeling, Pakket, PakketGebruik


@admin.register(Pakket)
class PakketAdmin(admin.ModelAdmin):
    list_display = ("naam", "versie", "leverancier", "status", "licentievorm")
    list_filter = ("status", "licentievorm")
    search_fields = ("naam", "leverancier__naam")


@admin.register(PakketGebruik)
class PakketGebruikAdmin(admin.ModelAdmin):
    list_display = ("pakket", "organisatie", "status", "start_datum")
    list_filter = ("status",)
    search_fields = ("pakket__naam", "organisatie__naam")


@admin.register(Koppeling)
class KoppelingAdmin(admin.ModelAdmin):
    list_display = ("van_pakket_gebruik", "naar_pakket_gebruik", "type")
    list_filter = ("type",)
