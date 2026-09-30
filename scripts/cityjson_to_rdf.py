#!/usr/bin/env python3
"""Create Rooftop Activation Ontology individuals from a CityJSON file.

For every Building city object (and its BuildingParts) the script creates:
  - a Building individual with has_city_model_id, and optionally
    has_osm_element and has_construction_year;
  - a 2D footprint geometry (geo:hasDefaultGeometry) and a centroid
    (geo:hasCentroid);
  - one Rooftop individual linked to the building, with a 3D geometry
    built from the roof surfaces.

Supports CityJSON 1.1 and 2.0 files (.city.json). Requires rdflib and shapely:
    pip install rdflib shapely

Example:
    python cityjson_to_rdf.py city.city.json buildings.ttl \
        --base https://example.org/my-region# \
        --osm-attribute osm_id --crs-2d 28992
"""
import argparse
import datetime
import json
import math
import re
import sys
from urllib.parse import quote

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD
from shapely.geometry import Polygon
from shapely.ops import unary_union

RA = Namespace("https://w3id.org/rooftop_activation#")
BLD = Namespace("http://bimerr.iot.linkeddata.es/def/building#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
ONTOLOGY_IRI = URIRef("https://w3id.org/rooftop_activation")

ROOF, GROUND = "RoofSurface", "GroundSurface"
NORMAL_THRESHOLD = 0.2  # |nz| above this: roof (up) or ground (down) when no semantics


def warn(msg):
    print(f"WARNING: {msg}", file=sys.stderr)


# ---------------------------------------------------------------- CRS

def crs_iri(value):
    """Normalise an EPSG code or CRS IRI/URN to the OGC http IRI used in WKT literals."""
    if value is None:
        return None
    value = str(value).strip()
    m = re.search(r"EPSG(?:/0/|::|:)(\d+)$", value, re.I) or re.fullmatch(r"(\d+)", value)
    if not m:
        sys.exit(f"Cannot read CRS '{value}'. Give an EPSG code, e.g. --crs 3812.")
    return f"http://www.opengis.net/def/crs/EPSG/0/{m.group(1)}"


# ---------------------------------------------------------------- geometry

def surfaces_of(geometry):
    """Yield (surface, semantic_index) for every surface of a CityJSON geometry.

    surface = list of rings, ring = list of vertex indices.
    """
    gtype = geometry.get("type")
    b = geometry.get("boundaries", [])
    sem = geometry.get("semantics", {}).get("values")
    if gtype in ("MultiSurface", "CompositeSurface"):
        for i, s in enumerate(b):
            yield s, (sem[i] if sem is not None else None)
    elif gtype == "Solid":
        for i, shell in enumerate(b):
            for j, s in enumerate(shell):
                yield s, (sem[i][j] if sem is not None and sem[i] is not None else None)
    elif gtype in ("MultiSolid", "CompositeSolid"):
        for k, solid in enumerate(b):
            for i, shell in enumerate(solid):
                for j, s in enumerate(shell):
                    v = None
                    if sem is not None and sem[k] is not None and sem[k][i] is not None:
                        v = sem[k][i][j]
                    yield s, v
    elif gtype == "GeometryInstance":
        warn("GeometryInstance (template) geometries are skipped.")
    # Point, line and other types are ignored


def newell_nz(coords):
    """Z component of the unit normal of a ring (Newell's method)."""
    nx = ny = nz = 0.0
    n = len(coords)
    for i in range(n):
        x1, y1, z1 = coords[i]
        x2, y2, z2 = coords[(i + 1) % n]
        nx += (y1 - y2) * (z1 + z2)
        ny += (z1 - z2) * (x1 + x2)
        nz += (x1 - x2) * (y1 + y2)
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    return nz / length if length else 0.0


def classify(geometry, rings_xyz, sem_index):
    """Return RoofSurface, GroundSurface or None for one surface."""
    surfaces = geometry.get("semantics", {}).get("surfaces")
    if surfaces is not None and sem_index is not None:
        return surfaces[sem_index].get("type")
    if surfaces is not None:
        return None  # semantics present but this surface has none
    nz = newell_nz(rings_xyz[0])  # fallback on orientation of the exterior ring
    if nz > NORMAL_THRESHOLD:
        return ROOF
    if nz < -NORMAL_THRESHOLD:
        return GROUND
    return None


def best_geometry(geometries):
    """Pick the geometry with the highest LoD, preferring ones with semantics."""
    usable = [g for g in geometries if g.get("type") != "GeometryInstance"]
    if not usable:
        return None
    return max(usable, key=lambda g: ("semantics" in g, float(str(g.get("lod", 0)))))


def fmt(v, precision):
    s = f"{v:.{precision}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def ring_wkt(ring, precision):
    ring = ring + [ring[0]]
    return "(" + ", ".join(" ".join(fmt(c, precision) for c in p) for p in ring) + ")"


def polygon2d_wkt(geom, precision):
    """WKT for a shapely Polygon or MultiPolygon, rounded."""
    def poly(p):
        rings = [list(p.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in p.interiors]
        return "(" + ", ".join(ring_wkt(r, precision) for r in rings) + ")"
    if geom.geom_type == "Polygon":
        return "POLYGON " + poly(geom)
    return "MULTIPOLYGON (" + ", ".join(poly(p) for p in geom.geoms) + ")"


# ---------------------------------------------------------------- helpers

def local_name(prefix, cityjson_id):
    return prefix + quote(str(cityjson_id), safe="-._~")


def osm_url(value, default_type):
    value = str(value).strip()
    if value.startswith(("http://", "https://")):
        return value
    m = re.fullmatch(r"(way|relation|node)[/ :]?(\d+)", value, re.I)
    if m:
        return f"https://www.openstreetmap.org/{m.group(1).lower()}/{m.group(2)}"
    m = re.fullmatch(r"([wrn])(\d+)", value, re.I)
    if m:
        kind = {"w": "way", "r": "relation", "n": "node"}[m.group(1).lower()]
        return f"https://www.openstreetmap.org/{kind}/{m.group(2)}"
    if re.fullmatch(r"\d+", value):
        return f"https://www.openstreetmap.org/{default_type}/{value}"
    warn(f"OSM value '{value}' not recognised, skipped.")
    return None


def year_of(value):
    m = re.match(r"\s*(\d{4})", str(value))
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="CityJSON file (.city.json)")
    ap.add_argument("output", help="Turtle file to write")
    ap.add_argument("--base", default="https://example.org/my-region#",
                    help="Namespace of your data, ending with # or /")
    ap.add_argument("--crs", help="EPSG code of the file if metadata.referenceSystem is missing")
    ap.add_argument("--crs-2d", help="EPSG code for the 2D footprint and centroid, e.g. the "
                                     "horizontal part of a compound CRS (default: same as the file)")
    ap.add_argument("--precision", type=int, default=3,
                    help="Decimals in WKT coordinates (3 for metres, 7 or more for degrees)")
    ap.add_argument("--osm-attribute", help="CityJSON attribute holding the OSM identifier")
    ap.add_argument("--osm-type", default="way", choices=["way", "relation", "node"],
                    help="OSM element type when the identifier is only a number")
    ap.add_argument("--year-attribute", default="yearOfConstruction",
                    help="CityJSON attribute holding the construction year")
    ap.add_argument("--district", help="IRI of a District to assign to every building")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        cj = json.load(f)
    if cj.get("type") != "CityJSON":
        sys.exit("Input is not a CityJSON file. Convert CityJSONSeq files to CityJSON first.")
    if str(cj.get("version")) not in ("1.1", "2.0", "2.0.1"):
        warn(f"CityJSON version {cj.get('version')} not tested.")

    crs3d = crs_iri(cj.get("metadata", {}).get("referenceSystem") or args.crs)
    if crs3d is None:
        sys.exit("No CRS in metadata.referenceSystem. Give one with --crs.")
    crs2d = crs_iri(args.crs_2d) if args.crs_2d else crs3d

    tr = cj.get("transform", {"scale": [1, 1, 1], "translate": [0, 0, 0]})
    sx, sy, sz = tr["scale"]
    tx, ty, tz = tr["translate"]
    verts = [(x * sx + tx, y * sy + ty, z * sz + tz) for x, y, z in cj["vertices"]]
    objects = cj["CityObjects"]

    base = args.base
    ex = Namespace(base)
    g = Graph()
    g.bind("", RA)
    g.bind("ex", ex)
    g.bind("bld", BLD)
    g.bind("geo", GEO)
    g.bind("dcterms", DCTERMS)

    data_ontology = URIRef(base.rstrip("#/"))
    g.add((data_ontology, RDF.type, OWL.Ontology))
    g.add((data_ontology, OWL.imports, ONTOLOGY_IRI))
    g.add((data_ontology, DCTERMS.source, Literal(args.input.split("/")[-1])))
    g.add((data_ontology, DCTERMS.created, Literal(datetime.date.today().isoformat(), datatype=XSD.date)))

    district = URIRef(args.district) if args.district else None
    counts = {"buildings": 0, "no_footprint": 0, "no_roof": 0, "osm": 0, "year": 0}

    for oid, obj in objects.items():
        if obj.get("type") != "Building":
            continue
        counts["buildings"] += 1

        # geometry of the building and of its BuildingParts
        members = [obj] + [objects[c] for c in obj.get("children", [])
                           if objects.get(c, {}).get("type") == "BuildingPart"]
        roof_polys, ground_2d, all_2d = [], [], []
        for m in members:
            geom = best_geometry(m.get("geometry", []))
            if geom is None:
                continue
            lod0 = str(geom.get("lod", "0")).startswith("0")  # LoD0: footprint only, no roof
            for surface, sem_idx in surfaces_of(geom):
                rings = [[verts[i] for i in ring] for ring in surface]
                if len(rings[0]) < 3:
                    continue
                kind = None if lod0 else classify(geom, rings, sem_idx)
                if kind == ROOF:
                    roof_polys.append(rings)
                p2d = Polygon([(x, y) for x, y, _ in rings[0]],
                              [[(x, y) for x, y, _ in r] for r in rings[1:]])
                if p2d.area > 0:
                    all_2d.append(p2d.buffer(0))
                    if kind == GROUND:
                        ground_2d.append(p2d.buffer(0))

        b = ex[local_name("building_", oid)]
        g.add((b, RDF.type, OWL.NamedIndividual))
        g.add((b, RDF.type, BLD.Building))
        g.add((b, RDFS.label, Literal(f"Building {oid}", lang="en")))
        g.add((b, RA.has_city_model_id, Literal(str(oid), datatype=XSD.string)))

        attrs = obj.get("attributes", {})
        if args.osm_attribute and args.osm_attribute in attrs:
            url = osm_url(attrs[args.osm_attribute], args.osm_type)
            if url:
                g.add((b, RA.has_osm_element, Literal(url, datatype=XSD.anyURI)))
                counts["osm"] += 1
        if args.year_attribute in attrs:
            year = year_of(attrs[args.year_attribute])
            if year:
                g.add((b, RA.has_construction_year, Literal(year, datatype=XSD.integer)))
                counts["year"] += 1
        if district is not None:
            g.add((b, RA.is_located_in, district))

        # footprint and centroid
        footprint = unary_union(ground_2d or all_2d) if (ground_2d or all_2d) else None
        if footprint is not None and not footprint.is_empty:
            fp = ex[local_name("building_", oid) + "_footprint"]
            g.add((b, GEO.hasDefaultGeometry, fp))
            g.add((b, GEO.hasGeometry, fp))
            g.add((fp, RDF.type, OWL.NamedIndividual))
            g.add((fp, RDF.type, GEO.Geometry))
            g.add((fp, GEO.asWKT, Literal(f"<{crs2d}> {polygon2d_wkt(footprint, args.precision)}",
                                          datatype=GEO.wktLiteral)))
            c = footprint.centroid
            ct = ex[local_name("building_", oid) + "_centroid"]
            g.add((b, GEO.hasCentroid, ct))
            g.add((ct, RDF.type, OWL.NamedIndividual))
            g.add((ct, RDF.type, GEO.Geometry))
            g.add((ct, GEO.asWKT, Literal(
                f"<{crs2d}> POINT ({fmt(c.x, args.precision)} {fmt(c.y, args.precision)})",
                datatype=GEO.wktLiteral)))
        else:
            counts["no_footprint"] += 1
            warn(f"Building {oid}: no footprint could be derived.")

        # rooftop
        r = ex[local_name("rooftop_", oid)]
        g.add((r, RDF.type, OWL.NamedIndividual))
        g.add((r, RDF.type, RA.Rooftop))
        g.add((r, RDFS.label, Literal(f"Rooftop of building {oid}", lang="en")))
        g.add((b, RA.has_rooftop, r))
        g.add((r, RA.is_part_of, b))
        if roof_polys:
            rg = ex[local_name("rooftop_", oid) + "_geometry"]
            wkt = "MULTIPOLYGON Z (" + ", ".join(
                "(" + ", ".join(ring_wkt(ring, args.precision) for ring in poly) + ")"
                for poly in roof_polys) + ")"
            g.add((r, GEO.hasDefaultGeometry, rg))
            g.add((r, GEO.hasGeometry, rg))
            g.add((rg, RDF.type, OWL.NamedIndividual))
            g.add((rg, RDF.type, GEO.Geometry))
            g.add((rg, GEO.asWKT, Literal(f"<{crs3d}> {wkt}", datatype=GEO.wktLiteral)))
        else:
            counts["no_roof"] += 1
            warn(f"Building {oid}: no roof surface found, rooftop created without geometry.")

    g.serialize(args.output, format="turtle")
    print(f"Buildings: {counts['buildings']} | with OSM link: {counts['osm']} | "
          f"with construction year: {counts['year']} | without footprint: {counts['no_footprint']} | "
          f"rooftops without geometry: {counts['no_roof']}")
    print(f"CRS 3D: {crs3d} | CRS 2D: {crs2d}")
    print(f"Written to {args.output}")


if __name__ == "__main__":
    main()
