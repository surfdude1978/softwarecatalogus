"""Tests voor beveiligde API endpoints (beheerders)."""
import pytest
from django.urls import reverse

from apps.organisaties.models import Organisatie
from apps.pakketten.models import Koppeling, Pakket, PakketGebruik

pytestmark = pytest.mark.django_db


# ========================
# Pakketbeheer (aanbod-beheerder)
# ========================

class TestPakketBeheerAPI:
    def test_pakket_aanmaken_als_aanbod_beheerder(self, aanbod_client, leverancier):
        url = reverse("api:pakket-list")
        data = {
            "naam": "Nieuw SaaS Pakket",
            "versie": "1.0",
            "beschrijving": "Test pakket",
            "leverancier": str(leverancier.pk),
            "licentievorm": "saas",
        }
        response = aanbod_client.post(url, data)
        assert response.status_code == 201
        pakket = Pakket.objects.get(naam="Nieuw SaaS Pakket")
        assert pakket.leverancier == leverancier

    def test_pakket_aanmaken_als_gebruik_beheerder_maakt_concept(self, auth_client, leverancier, gebruik_beheerder):
        url = reverse("api:pakket-list")
        data = {
            "naam": "Ontbrekend Pakket",
            "leverancier": str(leverancier.pk),
            "licentievorm": "commercieel",
        }
        response = auth_client.post(url, data)
        # Gebruik-beheerder heeft geen IsAanbodBeheerder permission
        assert response.status_code == 403

    def test_pakket_bijwerken_eigen_leverancier(self, aanbod_client, pakket, leverancier, aanbod_beheerder):
        url = reverse("api:pakket-detail", kwargs={"pk": pakket.pk})
        response = aanbod_client.patch(url, {"versie": "6.0"})
        assert response.status_code == 200

    def test_pakket_bijwerken_andere_leverancier_verboden(self, aanbod_client, db):
        andere_lev = Organisatie.objects.create(
            naam="Andere Lev", type="leverancier", status="actief"
        )
        ander_pakket = Pakket.objects.create(
            naam="AnderPakket", leverancier=andere_lev, status="actief"
        )
        url = reverse("api:pakket-detail", kwargs={"pk": ander_pakket.pk})
        response = aanbod_client.patch(url, {"versie": "2.0"})
        assert response.status_code == 403

    def test_functioneel_beheerder_mag_alles(self, admin_client, pakket):
        url = reverse("api:pakket-detail", kwargs={"pk": pakket.pk})
        response = admin_client.patch(url, {"versie": "10.0"})
        assert response.status_code == 200


# ========================
# Pakketoverzicht (gebruik-beheerder)
# ========================

class TestMijnPakketOverzichtAPI:
    def test_lijst_pakketoverzicht(self, auth_client, pakket_gebruik):
        url = reverse("api:mijn-pakketoverzicht-list")
        response = auth_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_pakket_toevoegen_aan_overzicht(self, auth_client, pakket2, gemeente):
        url = reverse("api:mijn-pakketoverzicht-list")
        data = {"pakket": str(pakket2.pk), "status": "in_gebruik"}
        response = auth_client.post(url, data)
        assert response.status_code == 201
        assert PakketGebruik.objects.filter(
            pakket=pakket2, organisatie=gemeente
        ).exists()

    def test_pakket_verwijderen_uit_overzicht(self, auth_client, pakket_gebruik):
        url = reverse("api:mijn-pakketoverzicht-detail", kwargs={"pk": pakket_gebruik.pk})
        response = auth_client.delete(url)
        assert response.status_code == 204

    def test_overzicht_alleen_eigen_organisatie(self, auth_client, pakket, gemeente2):
        PakketGebruik.objects.create(pakket=pakket, organisatie=gemeente2, status="in_gebruik")
        url = reverse("api:mijn-pakketoverzicht-list")
        response = auth_client.get(url)
        orgs = [r["organisatie_naam"] for r in response.data["results"]]
        assert "Gemeente Amsterdam" not in orgs

    def test_overzicht_publiek_verboden(self, api_client):
        url = reverse("api:mijn-pakketoverzicht-list")
        response = api_client.get(url)
        assert response.status_code == 401


# ========================
# Gluren bij de buren
# ========================

class TestGlurenBijDeBurenAPI:
    def test_gemeente_pakketoverzicht_bekijken(self, auth_client, pakket, gemeente2):
        PakketGebruik.objects.create(pakket=pakket, organisatie=gemeente2, status="in_gebruik")
        url = reverse("api:gemeente-pakketoverzicht", kwargs={"gemeente_id": gemeente2.pk})
        response = auth_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_gluren_toont_alleen_in_gebruik(self, auth_client, pakket, pakket2, gemeente2):
        PakketGebruik.objects.create(pakket=pakket, organisatie=gemeente2, status="in_gebruik")
        PakketGebruik.objects.create(pakket=pakket2, organisatie=gemeente2, status="gestopt")
        url = reverse("api:gemeente-pakketoverzicht", kwargs={"gemeente_id": gemeente2.pk})
        response = auth_client.get(url)
        assert len(response.data["results"]) == 1

    def test_gluren_vereist_authenticatie(self, api_client, gemeente2):
        url = reverse("api:gemeente-pakketoverzicht", kwargs={"gemeente_id": gemeente2.pk})
        response = api_client.get(url)
        assert response.status_code == 401


# ========================
# Koppelingen
# ========================

class TestKoppelingenAPI:
    def test_koppeling_aanmaken(self, auth_client, pakket_gebruik, pakket_gebruik2):
        url = reverse("api:koppeling-list")
        data = {
            "van_pakket_gebruik": str(pakket_gebruik.pk),
            "naar_pakket_gebruik": str(pakket_gebruik2.pk),
            "type": "api",
            "beschrijving": "REST koppeling",
        }
        response = auth_client.post(url, data)
        assert response.status_code == 201

    def test_koppeling_lijst(self, auth_client, pakket_gebruik, pakket_gebruik2):
        Koppeling.objects.create(
            van_pakket_gebruik=pakket_gebruik,
            naar_pakket_gebruik=pakket_gebruik2,
            type="api",
        )
        url = reverse("api:koppeling-list")
        response = auth_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1


# ========================
# Notificaties
# ========================

class TestNotificatiesAPI:
    def test_lijst_notificaties(self, auth_client, gebruik_beheerder):
        from apps.gebruikers.models import Notificatie
        Notificatie.objects.create(
            user=gebruik_beheerder, type="info", bericht="Test notificatie"
        )
        url = reverse("api:notificatie-list")
        response = auth_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_markeer_notificatie_gelezen(self, auth_client, gebruik_beheerder):
        from apps.gebruikers.models import Notificatie
        n = Notificatie.objects.create(
            user=gebruik_beheerder, type="info", bericht="Ongelezen"
        )
        url = reverse("api:notificatie-markeer-gelezen", kwargs={"pk": n.pk})
        response = auth_client.post(url)
        assert response.status_code == 200
        n.refresh_from_db()
        assert n.gelezen is True

    def test_markeer_alles_gelezen(self, auth_client, gebruik_beheerder):
        from apps.gebruikers.models import Notificatie
        Notificatie.objects.create(user=gebruik_beheerder, type="a", bericht="Een")
        Notificatie.objects.create(user=gebruik_beheerder, type="b", bericht="Twee")
        url = reverse("api:notificatie-markeer-alles-gelezen")
        response = auth_client.post(url)
        assert response.status_code == 200
        assert Notificatie.objects.filter(user=gebruik_beheerder, gelezen=False).count() == 0

    def test_alleen_eigen_notificaties(self, auth_client, functioneel_beheerder):
        from apps.gebruikers.models import Notificatie
        Notificatie.objects.create(
            user=functioneel_beheerder, type="info", bericht="Andermans notificatie"
        )
        url = reverse("api:notificatie-list")
        response = auth_client.get(url)
        assert len(response.data["results"]) == 0


# ========================
# Admin: Organisatiebeheer
# ========================

class TestAdminOrganisatieAPI:
    def test_concept_organisaties_ophalen(self, admin_client, concept_organisatie):
        url = reverse("api:admin-organisatie-concept")
        response = admin_client.get(url)
        assert response.status_code == 200
        namen = [o["naam"] for o in response.data]
        assert "Nieuwe Leverancier BV" in namen

    def test_organisatie_fiatteren(self, admin_client, concept_organisatie):
        url = reverse("api:admin-organisatie-fiatteren", kwargs={"pk": concept_organisatie.pk})
        response = admin_client.post(url)
        assert response.status_code == 200
        concept_organisatie.refresh_from_db()
        assert concept_organisatie.status == Organisatie.Status.ACTIEF

    def test_fiatteren_actieve_org_faalt(self, admin_client, gemeente):
        url = reverse("api:admin-organisatie-fiatteren", kwargs={"pk": gemeente.pk})
        response = admin_client.post(url)
        assert response.status_code == 400

    def test_organisaties_samenvoegen(
        self,
        admin_client,
        gemeente,
        gemeente2,
        gebruik_beheerder,
        pakket,
        pakket_gebruik,
    ):
        url = reverse("api:admin-organisatie-samenvoegen")
        data = {
            "bron_id": str(gemeente.pk),
            "doel_id": str(gemeente2.pk),
        }
        response = admin_client.post(url, data)
        assert response.status_code == 200
        gemeente.refresh_from_db()
        assert gemeente.status == Organisatie.Status.INACTIEF
        # Gebruiker is verplaatst
        gebruik_beheerder.refresh_from_db()
        assert gebruik_beheerder.organisatie == gemeente2

    def test_admin_endpoint_verboden_voor_gebruik_beheerder(self, auth_client, concept_organisatie):
        url = reverse("api:admin-organisatie-concept")
        response = auth_client.get(url)
        assert response.status_code == 403

    def test_samenvoegen_zonder_ids_faalt(self, admin_client):
        url = reverse("api:admin-organisatie-samenvoegen")
        response = admin_client.post(url, {})
        assert response.status_code == 400
