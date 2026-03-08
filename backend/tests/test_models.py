"""Tests voor alle Django modellen."""
import uuid

import pytest
from django.db import IntegrityError

from apps.gebruikers.models import User, Notificatie
from apps.organisaties.models import Organisatie, Contactpersoon
from apps.pakketten.models import Pakket, PakketGebruik, Koppeling
from apps.standaarden.models import Standaard, PakketStandaard
from apps.architectuur.models import GemmaComponent, PakketGemmaComponent
from apps.documenten.models import Document


# ========================
# BaseModel
# ========================

class TestBaseModel:
    def test_uuid_pk_wordt_automatisch_gegenereerd(self, pakket):
        assert isinstance(pakket.id, uuid.UUID)

    def test_timestamps_worden_gezet(self, pakket):
        assert pakket.aangemaakt_op is not None
        assert pakket.gewijzigd_op is not None


# ========================
# User
# ========================

class TestUserModel:
    def test_create_user(self, db):
        user = User.objects.create_user(
            email="test@example.com",
            naam="Test Gebruiker",
            password="VeiligWachtwoord123!",
        )
        assert user.email == "test@example.com"
        assert user.naam == "Test Gebruiker"
        assert user.check_password("VeiligWachtwoord123!")
        assert not user.is_staff
        assert user.is_active

    def test_create_user_zonder_email_faalt(self, db):
        with pytest.raises(ValueError, match="E-mailadres is verplicht"):
            User.objects.create_user(email="", naam="Test", password="wachtwoord")

    def test_create_superuser(self, db):
        user = User.objects.create_superuser(
            email="super@example.com",
            naam="Super Admin",
            password="SuperWachtwoord123!",
        )
        assert user.is_staff
        assert user.is_superuser

    def test_email_is_uniek(self, db):
        User.objects.create_user(email="dubbel@example.com", naam="Een", password="ww12345678")
        with pytest.raises(IntegrityError):
            User.objects.create_user(email="dubbel@example.com", naam="Twee", password="ww12345678")

    def test_default_status_wacht_op_fiattering(self, db):
        user = User.objects.create_user(
            email="nieuw@example.com", naam="Nieuw", password="wachtwoord123"
        )
        assert user.status == User.Status.WACHT_OP_FIATTERING

    def test_is_beheerder_property(self, gebruik_beheerder, aanbod_beheerder, functioneel_beheerder, gebruiker_publiek):
        assert gebruik_beheerder.is_beheerder
        assert aanbod_beheerder.is_beheerder
        assert functioneel_beheerder.is_beheerder
        assert not gebruiker_publiek.is_beheerder

    def test_is_functioneel_beheerder_property(self, functioneel_beheerder, gebruik_beheerder):
        assert functioneel_beheerder.is_functioneel_beheerder
        assert not gebruik_beheerder.is_functioneel_beheerder

    def test_str_representatie(self, gebruik_beheerder):
        assert "Gebruik Beheerder" in str(gebruik_beheerder)
        assert "gebruik@utrecht.nl" in str(gebruik_beheerder)

    def test_rollen_choices(self, db):
        assert len(User.Rol.choices) == 8


# ========================
# Organisatie
# ========================

class TestOrganisatieModel:
    def test_create_organisatie(self, gemeente):
        assert gemeente.naam == "Gemeente Utrecht"
        assert gemeente.type == Organisatie.Type.GEMEENTE
        assert gemeente.status == Organisatie.Status.ACTIEF

    def test_default_status_is_concept(self, db):
        org = Organisatie.objects.create(
            naam="Test Org",
            type=Organisatie.Type.LEVERANCIER,
        )
        assert org.status == Organisatie.Status.CONCEPT

    def test_str_representatie(self, leverancier):
        assert "Centric" in str(leverancier)
        assert "Leverancier" in str(leverancier)

    def test_contactpersoon_relatie(self, gemeente):
        cp = Contactpersoon.objects.create(
            organisatie=gemeente,
            naam="Jan Jansen",
            email="jan@utrecht.nl",
            functie="ICT Manager",
        )
        assert cp.organisatie == gemeente
        assert gemeente.contactpersonen.count() == 1

    def test_organisatie_types(self, db):
        assert len(Organisatie.Type.choices) == 4


# ========================
# Pakket
# ========================

class TestPakketModel:
    def test_create_pakket(self, pakket, leverancier):
        assert pakket.naam == "Suite4Gemeenten"
        assert pakket.leverancier == leverancier
        assert pakket.licentievorm == Pakket.Licentievorm.SAAS

    def test_str_met_versie(self, pakket):
        assert "Suite4Gemeenten" in str(pakket)
        assert "5.0" in str(pakket)

    def test_str_zonder_versie(self, db, leverancier):
        p = Pakket.objects.create(naam="Simpel", leverancier=leverancier)
        assert str(p) == "Simpel"

    def test_aantal_gebruikers_property(self, pakket, gemeente, gemeente2):
        PakketGebruik.objects.create(pakket=pakket, organisatie=gemeente, status="in_gebruik")
        PakketGebruik.objects.create(pakket=pakket, organisatie=gemeente2, status="gepland")
        assert pakket.aantal_gebruikers == 1

    def test_licentievorm_choices(self, db):
        assert len(Pakket.Licentievorm.choices) == 4


# ========================
# PakketGebruik
# ========================

class TestPakketGebruikModel:
    def test_create_pakketgebruik(self, pakket_gebruik, pakket, gemeente):
        assert pakket_gebruik.pakket == pakket
        assert pakket_gebruik.organisatie == gemeente
        assert pakket_gebruik.status == PakketGebruik.Status.IN_GEBRUIK

    def test_unique_together_pakket_organisatie(self, pakket, gemeente):
        PakketGebruik.objects.create(pakket=pakket, organisatie=gemeente)
        with pytest.raises(IntegrityError):
            PakketGebruik.objects.create(pakket=pakket, organisatie=gemeente)

    def test_str_representatie(self, pakket_gebruik):
        assert "Utrecht" in str(pakket_gebruik)
        assert "Suite4Gemeenten" in str(pakket_gebruik)


# ========================
# Koppeling
# ========================

class TestKoppelingModel:
    def test_create_koppeling(self, pakket_gebruik, pakket_gebruik2):
        koppeling = Koppeling.objects.create(
            van_pakket_gebruik=pakket_gebruik,
            naar_pakket_gebruik=pakket_gebruik2,
            type=Koppeling.Type.API,
            beschrijving="REST API koppeling",
        )
        assert koppeling.type == "api"

    def test_koppeling_types(self, db):
        assert len(Koppeling.Type.choices) == 5


# ========================
# Standaard
# ========================

class TestStandaardModel:
    def test_create_standaard(self, standaard):
        assert standaard.naam == "DigiD"
        assert standaard.type == Standaard.Type.VERPLICHT

    def test_pakket_standaard_through(self, pakket, standaard):
        ps = PakketStandaard.objects.create(
            pakket=pakket,
            standaard=standaard,
            ondersteund=True,
            testrapport_url="https://example.com/test.pdf",
        )
        assert ps.ondersteund
        assert pakket.standaarden.count() == 1

    def test_pakket_standaard_unique_together(self, pakket, standaard):
        PakketStandaard.objects.create(pakket=pakket, standaard=standaard)
        with pytest.raises(IntegrityError):
            PakketStandaard.objects.create(pakket=pakket, standaard=standaard)


# ========================
# GemmaComponent
# ========================

class TestGemmaComponentModel:
    def test_create_component(self, gemma_component):
        assert gemma_component.naam == "Zaaksysteem"
        assert gemma_component.archimate_id == "id-gemma-001"

    def test_parent_child_relatie(self, gemma_component, gemma_child):
        assert gemma_child.parent == gemma_component
        assert gemma_component.children.count() == 1

    def test_archimate_id_is_uniek(self, db):
        GemmaComponent.objects.create(naam="A", archimate_id="unique-001")
        with pytest.raises(IntegrityError):
            GemmaComponent.objects.create(naam="B", archimate_id="unique-001")

    def test_pakket_gemma_through(self, pakket, gemma_component):
        PakketGemmaComponent.objects.create(pakket=pakket, gemma_component=gemma_component)
        assert pakket.gemma_componenten.count() == 1


# ========================
# Notificatie
# ========================

class TestNotificatieModel:
    def test_create_notificatie(self, gebruik_beheerder):
        notificatie = Notificatie.objects.create(
            user=gebruik_beheerder,
            type="fiattering",
            bericht="Uw organisatie is goedgekeurd.",
        )
        assert not notificatie.gelezen
        assert gebruik_beheerder.notificaties.count() == 1

    def test_str_representatie(self, gebruik_beheerder):
        n = Notificatie.objects.create(
            user=gebruik_beheerder,
            type="info",
            bericht="Kort bericht",
        )
        assert "[info]" in str(n)
