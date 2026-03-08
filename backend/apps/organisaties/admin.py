from django.contrib import admin
from .models import Organisatie, Contactpersoon


class ContactpersoonInline(admin.TabularInline):
    model = Contactpersoon
    extra = 0


@admin.register(Organisatie)
class OrganisatieAdmin(admin.ModelAdmin):
    list_display = ("naam", "type", "status", "oin")
    list_filter = ("type", "status")
    search_fields = ("naam", "oin")
    inlines = [ContactpersoonInline]


@admin.register(Contactpersoon)
class ContactpersoonAdmin(admin.ModelAdmin):
    list_display = ("naam", "organisatie", "email", "functie")
    search_fields = ("naam", "email")
