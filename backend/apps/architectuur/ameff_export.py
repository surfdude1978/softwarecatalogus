"""AMEFF (ArchiMate Exchange File Format) export generator.

Genereert een AMEFF XML-bestand van het pakketlandschap van een organisatie,
inclusief GEMMA referentiecomponenten en hun relaties met pakketten.
"""
import io
import uuid
from xml.etree import ElementTree as ET

from apps.pakketten.models import PakketGebruik


ARCHIMATE_NS = "http://www.opengroup.org/xsd/archimate/3.0/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"


def generate_ameff(organisatie_id=None, pakketten_queryset=None):
    """
    Genereer een AMEFF XML-bestand.

    Args:
        organisatie_id: UUID van de organisatie (voor export van pakketlandschap).
        pakketten_queryset: Optionele queryset van pakketten om te exporteren.

    Returns:
        str: XML string in AMEFF formaat.
    """
    # Registreer namespaces
    ET.register_namespace("", ARCHIMATE_NS)
    ET.register_namespace("xsi", XSI_NS)

    # Root element
    root = ET.Element("model", {
        "xmlns": ARCHIMATE_NS,
        "xmlns:xsi": XSI_NS,
        "identifier": f"id-{uuid.uuid4()}",
        "name": "Softwarecatalogus Export",
    })

    # Metadata
    metadata = ET.SubElement(root, "metadata")
    schema = ET.SubElement(metadata, "schema")
    schema.text = "http://www.opengroup.org/xsd/archimate/3.0/"
    schema_version = ET.SubElement(metadata, "schemaversion")
    schema_version.text = "3.1"

    # Elements container
    elements = ET.SubElement(root, "elements")

    # Relationships container
    relationships = ET.SubElement(root, "relationships")

    # Verzamel pakketten en GEMMA componenten
    if organisatie_id:
        gebruik_items = PakketGebruik.objects.filter(
            organisatie_id=organisatie_id,
            status="in_gebruik",
        ).select_related("pakket").prefetch_related("pakket__gemma_componenten")

        pakket_set = {pg.pakket for pg in gebruik_items}
    elif pakketten_queryset is not None:
        pakket_set = set(pakketten_queryset.prefetch_related("gemma_componenten"))
    else:
        pakket_set = set()

    gemma_components = set()
    pakket_to_gemma = {}

    for pakket in pakket_set:
        componenten = list(pakket.gemma_componenten.all())
        pakket_to_gemma[pakket] = componenten
        gemma_components.update(componenten)

    # Exporteer GEMMA componenten als ArchiMate elementen
    archimate_type_map = {
        "applicatiecomponent": "ApplicationComponent",
        "applicatieservice": "ApplicationService",
        "applicatiefunctie": "ApplicationFunction",
        "anders": "ApplicationComponent",
    }

    for component in gemma_components:
        elem = ET.SubElement(elements, "element", {
            "identifier": component.archimate_id,
            f"{{{XSI_NS}}}type": archimate_type_map.get(component.type, "ApplicationComponent"),
        })
        name = ET.SubElement(elem, "name", {"xml:lang": "nl"})
        name.text = component.naam
        if component.beschrijving:
            doc = ET.SubElement(elem, "documentation", {"xml:lang": "nl"})
            doc.text = component.beschrijving

    # Exporteer pakketten als ArchiMate ApplicationComponents
    for pakket in pakket_set:
        pakket_arch_id = f"pkg-{pakket.id}"
        elem = ET.SubElement(elements, "element", {
            "identifier": pakket_arch_id,
            f"{{{XSI_NS}}}type": "ApplicationComponent",
        })
        name = ET.SubElement(elem, "name", {"xml:lang": "nl"})
        name.text = pakket.naam
        if pakket.beschrijving:
            doc = ET.SubElement(elem, "documentation", {"xml:lang": "nl"})
            doc.text = pakket.beschrijving

        # Relaties: pakket -> GEMMA component (Realization)
        for component in pakket_to_gemma.get(pakket, []):
            ET.SubElement(relationships, "relationship", {
                "identifier": f"rel-{uuid.uuid4()}",
                f"{{{XSI_NS}}}type": "Realization",
                "source": pakket_arch_id,
                "target": component.archimate_id,
            })

    # Genereer XML string
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")

    output = io.BytesIO()
    tree.write(output, encoding="utf-8", xml_declaration=True)
    return output.getvalue().decode("utf-8")
