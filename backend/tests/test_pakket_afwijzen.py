"""Tests voor het afwijzen van concept-pakketten (issue #56)."""

import pytest
from django.urls import reverse

from apps.gebruikers.models import Notificatie
from apps.pakketten.models import Pakket

pytestmark = pytest.mark.django_db


class TestPakketAfwijzen:
    """POST /api/v1/pakketten/{id}/afwijzen/ — wijs concept-pakket af."""

    def test_afwijzen_zet_status_op_ingetrokken(self, admin_client, concept_pakket):
        url = reverse("api:pakket-afwijzen", kwargs={"pk": concept_pakket.pk})
        response = admin_client.post(url, {"reden": "Onvolledige informatie."}, format="json")
        assert response.status_code == 200
        concept_pakket.refresh_from_db()
        assert concept_pakket.status == Pakket.Status.INGETROKKEN

    def test_afwijzen_zonder_reden_geeft_400(self, admin_client, concept_pakket):
        url = reverse("api:pakket-afwijzen", kwargs={"pk": concept_pakket.pk})
        response = admin_client.post(url, {"reden": ""}, format="json")
        assert response.status_code == 400
        assert "reden" in response.data["detail"].lower()

    def test_afwijzen_zonder_reden_veld_geeft_400(self, admin_client, concept_pakket):
        url = reverse("api:pakket-afwijzen", kwargs={"pk": concept_pakket.pk})
        response = admin_client.post(url, {}, format="json")
        assert response.status_code == 400

    def test_afwijzen_actief_pakket_geeft_400(self, admin_client, pakket):
        url = reverse("api:pakket-afwijzen", kwargs={"pk": pakket.pk})
        response = admin_client.post(url, {"reden": "Reden"}, format="json")
        assert response.status_code == 400

    def test_afwijzen_vereist_functioneel_beheerder(self, auth_client, concept_pakket):
        url = reverse("api:pakket-afwijzen", kwargs={"pk": concept_pakket.pk})
        response = auth_client.post(url, {"reden": "Reden"}, format="json")
        assert response.status_code == 403

    def test_afwijzen_vereist_authenticatie(self, api_client, concept_pakket):
        url = reverse("api:pakket-afwijzen", kwargs={"pk": concept_pakket.pk})
        response = api_client.post(url, {"reden": "Reden"}, format="json")
        assert response.status_code == 401

    def test_afwijzen_stuurt_notificatie_naar_indiener(
        self, admin_client, concept_pakket, gebruik_beheerder
    ):
        concept_pakket.geregistreerd_door = gebruik_beheerder
        concept_pakket.save(update_fields=["geregistreerd_door"])

        url = reverse("api:pakket-afwijzen", kwargs={"pk": concept_pakket.pk})
        admin_client.post(url, {"reden": "Pakket onvolledig beschreven."}, format="json")

        notificatie = Notificatie.objects.filter(
            user=gebruik_beheerder,
            type="pakket_afgewezen",
        ).first()
        assert notificatie is not None
        assert "onvolledig beschreven" in notificatie.bericht

    def test_afwijzen_zonder_indiener_geeft_geen_notificatie(self, admin_client, concept_pakket):
        """Pakket zonder geregistreerd_door: geen notificatie, wel succesvol."""
        assert concept_pakket.geregistreerd_door is None
        url = reverse("api:pakket-afwijzen", kwargs={"pk": concept_pakket.pk})
        response = admin_client.post(url, {"reden": "Reden"}, format="json")
        assert response.status_code == 200
        assert Notificatie.objects.filter(type="pakket_afgewezen").count() == 0

    def test_afwijzen_logt_audit(self, admin_client, concept_pakket):
        from apps.core.audit import AuditLog

        url = reverse("api:pakket-afwijzen", kwargs={"pk": concept_pakket.pk})
        admin_client.post(url, {"reden": "Audit reden"}, format="json")

        assert AuditLog.objects.filter(
            actie=AuditLog.Actie.AFGEWEZEN,
            object_type="Pakket",
            object_id=str(concept_pakket.pk),
        ).exists()


class TestPakketListSerializerVelden:
    """PakketListSerializer bevat de nieuwe velden voor het beheerscherm."""

    def test_lijst_bevat_aangemaakt_op(self, admin_client, pakket):
        url = reverse("api:pakket-list")
        response = admin_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1
        assert "aangemaakt_op" in response.data["results"][0]

    def test_lijst_bevat_geregistreerd_door_naam(self, admin_client, pakket):
        url = reverse("api:pakket-list")
        response = admin_client.get(url)
        assert "geregistreerd_door_naam" in response.data["results"][0]

    def test_geregistreerd_door_naam_is_null_indien_onbekend(self, admin_client, concept_pakket):
        url = reverse("api:pakket-list")
        response = admin_client.get(url)
        resultaat = next(r for r in response.data["results"] if r["naam"] == concept_pakket.naam)
        assert resultaat["geregistreerd_door_naam"] is None
