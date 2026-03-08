"""AMEFF (ArchiMate Exchange File Format) import parser.

Parseert een AMEFF XML-bestand en importeert GEMMA componenten
in de database. Bestaande componenten worden bijgewerkt op basis
van hun archimate_id.
"""
import logging
from xml.etree import ElementTree as ET

from .models import GemmaComponent

logger = logging.getLogger(__name__)

# ArchiMate 3.x namespaces
NAMESPACES = {
    "archimate": "http://www.opengroup.org/xsd/archimate/3.0/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

# Mapping van ArchiMate xsi:type naar GemmaComponent.Type
TYPE_MAPPING = {
    "ApplicationComponent": GemmaComponent.Type.APPLICATIE_COMPONENT,
    "ApplicationService": GemmaComponent.Type.APPLICATIE_SERVICE,
    "ApplicationFunction": GemmaComponent.Type.APPLICATIE_FUNCTIE,
}


def parse_ameff(file_content):
    """
    Parse een AMEFF XML bestand en retourneer een lijst van componenten en relaties.

    Args:
        file_content: bytes of string van het AMEFF XML bestand.

    Returns:
        dict met 'elements' en 'relationships' lijsten.
    """
    root = ET.fromstring(file_content if isinstance(file_content, str) else file_content.decode("utf-8"))

    elements = []
    relationships = []

    # Parse elements
    for elem in root.iter():
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

        if tag == "element":
            xsi_type = elem.get(f"{{{NAMESPACES['xsi']}}}type", "")
            # Strip namespace prefix if present
            xsi_type = xsi_type.split(":")[-1] if ":" in xsi_type else xsi_type

            identifier = elem.get("identifier", "")
            name_elem = elem.find(".//{%s}name" % NAMESPACES.get("archimate", "*"))
            if name_elem is None:
                # Try without namespace
                name_elem = elem.find(".//name")

            name = ""
            if name_elem is not None:
                name = name_elem.text or ""
            else:
                # Fallback: try 'name' attribute
                name = elem.get("name", "")

            doc_elem = elem.find(".//{%s}documentation" % NAMESPACES.get("archimate", "*"))
            if doc_elem is None:
                doc_elem = elem.find(".//documentation")
            documentation = doc_elem.text if doc_elem is not None else ""

            if identifier and name and xsi_type in TYPE_MAPPING:
                elements.append({
                    "identifier": identifier,
                    "name": name,
                    "type": xsi_type,
                    "documentation": documentation or "",
                })

        elif tag == "relationship":
            xsi_type = elem.get(f"{{{NAMESPACES['xsi']}}}type", "")
            xsi_type = xsi_type.split(":")[-1] if ":" in xsi_type else xsi_type
            source = elem.get("source", "")
            target = elem.get("target", "")
            identifier = elem.get("identifier", "")

            if source and target:
                relationships.append({
                    "identifier": identifier,
                    "type": xsi_type,
                    "source": source,
                    "target": target,
                })

    return {"elements": elements, "relationships": relationships}


def import_ameff(file_content, dry_run=False):
    """
    Importeer GEMMA componenten uit een AMEFF bestand.

    Args:
        file_content: bytes of string van het AMEFF XML bestand.
        dry_run: Als True, voer geen database wijzigingen door.

    Returns:
        dict met statistieken en eventuele conflicten.
    """
    parsed = parse_ameff(file_content)

    stats = {
        "elements_found": len(parsed["elements"]),
        "relationships_found": len(parsed["relationships"]),
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "conflicts": [],
    }

    # Fase 1: Importeer elementen
    id_to_component = {}

    for elem in parsed["elements"]:
        component_type = TYPE_MAPPING.get(elem["type"], GemmaComponent.Type.ANDERS)

        existing = GemmaComponent.objects.filter(archimate_id=elem["identifier"]).first()

        if existing:
            # Check voor conflicten (naam veranderd)
            if existing.naam != elem["name"]:
                stats["conflicts"].append({
                    "archimate_id": elem["identifier"],
                    "old_name": existing.naam,
                    "new_name": elem["name"],
                })

            if not dry_run:
                existing.naam = elem["name"]
                existing.type = component_type
                existing.beschrijving = elem["documentation"]
                existing.save(update_fields=["naam", "type", "beschrijving", "gewijzigd_op"])

            id_to_component[elem["identifier"]] = existing
            stats["updated"] += 1
        else:
            if not dry_run:
                component = GemmaComponent.objects.create(
                    archimate_id=elem["identifier"],
                    naam=elem["name"],
                    type=component_type,
                    beschrijving=elem["documentation"],
                )
                id_to_component[elem["identifier"]] = component
            stats["created"] += 1

    # Fase 2: Verwerk relaties (Composition/Aggregation -> parent-child)
    composition_types = {"Composition", "Aggregation"}
    for rel in parsed["relationships"]:
        if rel["type"] in composition_types:
            source_comp = id_to_component.get(rel["source"])
            target_comp = id_to_component.get(rel["target"])

            if source_comp and target_comp and not dry_run:
                # In ArchiMate: source bevat target (composition)
                target_comp.parent = source_comp
                target_comp.save(update_fields=["parent", "gewijzigd_op"])

    logger.info(
        "AMEFF import: %d gevonden, %d aangemaakt, %d bijgewerkt, %d conflicten",
        stats["elements_found"],
        stats["created"],
        stats["updated"],
        len(stats["conflicts"]),
    )

    return stats
