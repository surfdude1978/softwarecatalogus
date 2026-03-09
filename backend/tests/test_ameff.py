"""Tests voor ArchiMate AMEFF import en export."""

import pytest

from apps.architectuur.ameff_export import generate_ameff
from apps.architectuur.ameff_import import import_ameff, parse_ameff
from apps.architectuur.models import GemmaComponent, PakketGemmaComponent
from apps.pakketten.models import PakketGebruik

pytestmark = pytest.mark.django_db


# ========================
# Voorbeeld AMEFF XML
# ========================

SAMPLE_AMEFF = """<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       identifier="id-model-1"
       xsi:schemaLocation="http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd">
  <name xml:lang="nl">GEMMA Applicatielaag</name>
  <elements>
    <element identifier="id-zaaksysteem" xsi:type="ApplicationComponent">
      <name xml:lang="nl">Zaaksysteem</name>
      <documentation xml:lang="nl">Centraal zaakregistratiesysteem</documentation>
    </element>
    <element identifier="id-zaakservice" xsi:type="ApplicationService">
      <name xml:lang="nl">Zaakafhandeling</name>
      <documentation xml:lang="nl">Service voor zaakafhandeling</documentation>
    </element>
    <element identifier="id-burgerzaken" xsi:type="ApplicationComponent">
      <name xml:lang="nl">Burgerzaken</name>
    </element>
  </elements>
  <relationships>
    <relationship identifier="rel-1" xsi:type="Composition"
                  source="id-zaaksysteem" target="id-zaakservice" />
  </relationships>
</model>
"""

SAMPLE_AMEFF_RENAMED = """<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       identifier="id-model-2">
  <elements>
    <element identifier="id-zaaksysteem" xsi:type="ApplicationComponent">
      <name xml:lang="nl">Zaakregistratiesysteem</name>
    </element>
  </elements>
  <relationships/>
</model>
"""


# ========================
# Parse tests
# ========================


class TestParseAMEFF:
    def test_parse_elementen(self):
        result = parse_ameff(SAMPLE_AMEFF)
        assert len(result["elements"]) == 3
        names = {e["name"] for e in result["elements"]}
        assert "Zaaksysteem" in names
        assert "Zaakafhandeling" in names
        assert "Burgerzaken" in names

    def test_parse_element_types(self):
        result = parse_ameff(SAMPLE_AMEFF)
        types = {e["name"]: e["type"] for e in result["elements"]}
        assert types["Zaaksysteem"] == "ApplicationComponent"
        assert types["Zaakafhandeling"] == "ApplicationService"

    def test_parse_documentatie(self):
        result = parse_ameff(SAMPLE_AMEFF)
        elem = next(e for e in result["elements"] if e["name"] == "Zaaksysteem")
        assert "zaakregistratiesysteem" in elem["documentation"].lower()

    def test_parse_relaties(self):
        result = parse_ameff(SAMPLE_AMEFF)
        assert len(result["relationships"]) == 1
        rel = result["relationships"][0]
        assert rel["type"] == "Composition"
        assert rel["source"] == "id-zaaksysteem"
        assert rel["target"] == "id-zaakservice"

    def test_parse_bytes_input(self):
        result = parse_ameff(SAMPLE_AMEFF.encode("utf-8"))
        assert len(result["elements"]) == 3


# ========================
# Import tests
# ========================


class TestImportAMEFF:
    def test_import_maakt_componenten_aan(self):
        stats = import_ameff(SAMPLE_AMEFF)
        assert stats["created"] == 3
        assert stats["updated"] == 0
        assert GemmaComponent.objects.count() == 3

    def test_import_component_types(self):
        import_ameff(SAMPLE_AMEFF)
        zaak = GemmaComponent.objects.get(archimate_id="id-zaaksysteem")
        assert zaak.type == GemmaComponent.Type.APPLICATIE_COMPONENT
        service = GemmaComponent.objects.get(archimate_id="id-zaakservice")
        assert service.type == GemmaComponent.Type.APPLICATIE_SERVICE

    def test_import_zet_parent_child_relatie(self):
        import_ameff(SAMPLE_AMEFF)
        child = GemmaComponent.objects.get(archimate_id="id-zaakservice")
        parent = GemmaComponent.objects.get(archimate_id="id-zaaksysteem")
        assert child.parent == parent

    def test_import_update_bestaand_component(self):
        GemmaComponent.objects.create(
            archimate_id="id-zaaksysteem",
            naam="Zaaksysteem",
            type=GemmaComponent.Type.APPLICATIE_COMPONENT,
        )
        stats = import_ameff(SAMPLE_AMEFF)
        assert stats["updated"] >= 1
        assert stats["created"] == 2  # 2 nieuwe

    def test_import_detecteert_naam_conflict(self):
        GemmaComponent.objects.create(
            archimate_id="id-zaaksysteem",
            naam="Zaaksysteem",
            type=GemmaComponent.Type.APPLICATIE_COMPONENT,
        )
        stats = import_ameff(SAMPLE_AMEFF_RENAMED)
        assert len(stats["conflicts"]) == 1
        conflict = stats["conflicts"][0]
        assert conflict["old_name"] == "Zaaksysteem"
        assert conflict["new_name"] == "Zaakregistratiesysteem"

    def test_dry_run_maakt_niets_aan(self):
        stats = import_ameff(SAMPLE_AMEFF, dry_run=True)
        assert stats["created"] == 3
        assert GemmaComponent.objects.count() == 0

    def test_idempotent_import(self):
        import_ameff(SAMPLE_AMEFF)
        count_after_first = GemmaComponent.objects.count()
        import_ameff(SAMPLE_AMEFF)
        assert GemmaComponent.objects.count() == count_after_first


# ========================
# Export tests
# ========================


class TestGenerateAMEFF:
    def test_export_bevat_xml_declaratie(self, pakket, pakket_gebruik, gemma_component):
        PakketGemmaComponent.objects.create(pakket=pakket, gemma_component=gemma_component)
        result = generate_ameff(organisatie_id=pakket_gebruik.organisatie.id)
        assert "<?xml" in result
        assert "archimate" in result.lower()

    def test_export_bevat_gemma_componenten(self, pakket, pakket_gebruik, gemma_component):
        PakketGemmaComponent.objects.create(pakket=pakket, gemma_component=gemma_component)
        result = generate_ameff(organisatie_id=pakket_gebruik.organisatie.id)
        assert "Zaaksysteem" in result
        assert gemma_component.archimate_id in result

    def test_export_bevat_pakketten(self, pakket, pakket_gebruik, gemma_component):
        PakketGemmaComponent.objects.create(pakket=pakket, gemma_component=gemma_component)
        result = generate_ameff(organisatie_id=pakket_gebruik.organisatie.id)
        assert "Suite4Gemeenten" in result

    def test_export_bevat_relaties(self, pakket, pakket_gebruik, gemma_component):
        PakketGemmaComponent.objects.create(pakket=pakket, gemma_component=gemma_component)
        result = generate_ameff(organisatie_id=pakket_gebruik.organisatie.id)
        assert "Realization" in result

    def test_export_zonder_pakketten(self, gemeente):
        result = generate_ameff(organisatie_id=gemeente.id)
        assert "<?xml" in result
        # Lege export is wel geldig XML

    def test_export_alleen_in_gebruik(self, pakket, pakket2, gemeente, gemma_component):
        PakketGebruik.objects.create(pakket=pakket, organisatie=gemeente, status="in_gebruik")
        PakketGebruik.objects.create(pakket=pakket2, organisatie=gemeente, status="gestopt")
        PakketGemmaComponent.objects.create(pakket=pakket, gemma_component=gemma_component)
        result = generate_ameff(organisatie_id=gemeente.id)
        assert "Suite4Gemeenten" in result
        assert "eBurgerzaken" not in result
