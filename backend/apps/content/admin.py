from django.contrib import admin

from .models import Nieuwsbericht, Pagina


@admin.register(Pagina)
class PaginaAdmin(admin.ModelAdmin):
    list_display = ("titel", "slug", "gepubliceerd", "aangemaakt_op")
    list_filter = ("gepubliceerd",)
    search_fields = ("titel",)
    prepopulated_fields = {"slug": ("titel",)}


@admin.register(Nieuwsbericht)
class NieuwsberichtAdmin(admin.ModelAdmin):
    list_display = ("titel", "gepubliceerd", "publicatie_datum")
    list_filter = ("gepubliceerd",)
    search_fields = ("titel",)
    prepopulated_fields = {"slug": ("titel",)}
