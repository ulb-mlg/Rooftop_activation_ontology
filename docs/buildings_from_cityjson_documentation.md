# Registering buildings from a CityJSON file

This section explains how to create, in your own data, the buildings and rooftops of a 3D city model in CityJSON format, so that each building is located geographically and linked to its city object and to OpenStreetMap. It also explains how to check the result and link buildings to districts.

## 1. What is created

For each building of the city model, you create four or five individuals:

| Individual | Type | Purpose |
|---|---|---|
| Building | `bld:Building` | The building, linked to its city object in the CityJSON file and, optionally, to OpenStreetMap |
| Footprint | `geo:Geometry` | The 2D outline of the building, as a WKT polygon. Default geometry of the building |
| Centroid | `geo:Geometry` | A point at the centre of the footprint. Used to find the district of the building |
| Rooftop | `:Rooftop` | The roof of the building, as a site for activation |
| Rooftop geometry | `geo:Geometry` | The roof surfaces of the building, as a 3D WKT multipolygon (only if the model has roofs) |

```
district  <-  is_located_in  <-  building  ->  has_rooftop  ->  rooftop
                                    |                              |
                        hasDefaultGeometry, hasCentroid      hasDefaultGeometry
                                    |                              |
                            footprint, centroid             rooftop geometry
```

Prefixes used in this section:

| Prefix | Namespace |
|---|---|
| `:` | `https://w3id.org/rooftop_activation#` |
| `bld:` | `http://bimerr.iot.linkeddata.es/def/building#` |
| `geo:` | `http://www.opengis.net/ont/geosparql#` |
| `ex:` | your own namespace, for example `https://example.org/my-region#` |

## 2. Before you start

1. **Create your own data file.** Do not edit the ontology. Create a separate ontology for your data that imports `https://w3id.org/rooftop_activation` (version 2.1.0 or later), and use your own namespace for everything you create. Keep the generated buildings in their own file (for example `buildings.ttl`), separate from the data you add by hand (activation types, owners, associations). You can then regenerate the buildings when the city model changes without losing your own data.
2. **Inspect the CityJSON file.** You need to know:
   - its version (1.1 and 2.0 are supported);
   - its coordinate reference system (CRS), in `metadata.referenceSystem`;
   - its levels of detail (LoD). LoD0 gives footprints only, LoD1 gives flat roofs, LoD2 gives roof shapes;
   - the names of its attributes, in particular the construction year and the OpenStreetMap identifier, if present.

   With [cjio](https://github.com/cityjson/cjio), `cjio my_city.city.json info --long` shows all of these. Otherwise, open the file in a text editor and read the `metadata` member and the `attributes` of a few city objects.
3. **Identify the horizontal CRS.** If the CRS of the file is compound (horizontal CRS plus a height system, for example EPSG:7415 = EPSG:28992 + NAP height), note the EPSG code of its horizontal part. It is used for the 2D footprints and centroids.
4. **Prepare your districts.** To link buildings to districts automatically (section 8), each `District` individual needs a polygon geometry in the same horizontal CRS as the footprints.

## 3. Structure of a building

**Building** (`bld:Building`):

| Property | Required | Value |
|---|---|---|
| `has_city_model_id` | required | The key of the building in the `CityObjects` of the CityJSON file, exactly as written (`xsd:string`) |
| `geo:hasDefaultGeometry` | required | The footprint geometry |
| `geo:hasCentroid` | recommended | The centroid geometry |
| `has_rooftop` | required | The rooftop of the building |
| `is_located_in` | required | The `District` the building is in |
| `has_osm_element` | optional | The full URL of the OpenStreetMap way or relation, e.g. `https://www.openstreetmap.org/way/123456` (`xsd:anyURI`) |
| `has_construction_year` | optional | The construction year (`xsd:integer`). The construction era is inferred from it by a reasoner |

**Rooftop** (`:Rooftop`):

| Property | Required | Value |
|---|---|---|
| `is_part_of` | required | The building |
| `geo:hasDefaultGeometry` | recommended | The rooftop geometry |

**Geometry** (`geo:Geometry`):

| Property | Required | Value |
|---|---|---|
| `geo:asWKT` | required | The coordinates, as a `geo:wktLiteral` that starts with the CRS IRI |

**Writing WKT literals.** Start each literal with the CRS IRI in angle brackets, followed by the geometry:

```
"<http://www.opengis.net/def/crs/EPSG/0/28992> POLYGON ((150100 170100, 150110 170100, 150110 170106, 150100 170106, 150100 170100))"^^geo:wktLiteral
```

- Use `http://www.opengis.net/def/crs/EPSG/0/<code>`, with `http`, even if the CityJSON file writes the CRS with `https`.
- Footprints and centroids are 2D (`POLYGON`, `MULTIPOLYGON`, `POINT`) in the horizontal CRS.
- Rooftop geometries are 3D (`MULTIPOLYGON Z`) in the CRS of the file.
- Close every ring: the last point repeats the first.
- If you omit the CRS IRI, the coordinates are read as longitude and latitude (CRS84). Do not omit it for projected coordinates.

## 4. Rules

1. **One Building individual per CityJSON Building.** The BuildingParts of a building are merged into it: their surfaces form the footprint and the rooftop of the building. The ontology has no class for building parts.
2. **The CityJSON key is the identity of the building.** `has_city_model_id` holds the key exactly as written in the file, and the IRIs are derived from it (`ex:building_<key>`, `ex:rooftop_<key>`). Two buildings must never share a `has_city_model_id`.
3. **One rooftop per building.** The rooftop contains all roof surfaces of the building. If parts of a roof can be activated separately, create additional `Rooftop` individuals by hand, each with its own geometry and `is_part_of` the building.
4. **Do not edit generated geometry.** If a geometry is wrong, correct the CityJSON file and regenerate the buildings.
5. **Keep keys stable between versions of the city model.** When a new version of the city model is available, regenerate the buildings file and replace it. Your hand-made data stays valid if the keys, and therefore the IRIs, have not changed.
6. **Use one CRS per kind of geometry.** All footprints, centroids and district polygons in the same horizontal CRS; all rooftop geometries in the CRS of the city model.
7. **OpenStreetMap identifiers are not permanent.** An OSM element can be deleted and redrawn with a new identifier. Treat `has_osm_element` as a convenience link; the city model key and the geometry remain the reference.

## 5. Buildings in Turtle

```turtle
@prefix :        <https://w3id.org/rooftop_activation#> .
@prefix bld:     <http://bimerr.iot.linkeddata.es/def/building#> .
@prefix geo:     <http://www.opengis.net/ont/geosparql#> .
@prefix ex:      <https://example.org/my-region#> .
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<https://example.org/my-region> a owl:Ontology ;
    owl:imports <https://w3id.org/rooftop_activation> ;
    dcterms:source "my_city.city.json" .

ex:building_B0001 a owl:NamedIndividual , bld:Building ;
    rdfs:label             "Building B0001"@en ;
    :has_city_model_id     "B0001"^^xsd:string ;
    :has_osm_element       "https://www.openstreetmap.org/way/123456"^^xsd:anyURI ;
    :has_construction_year 1932 ;
    :is_located_in         ex:district_07 ;
    :has_rooftop           ex:rooftop_B0001 ;
    geo:hasDefaultGeometry ex:building_B0001_footprint ;
    geo:hasCentroid        ex:building_B0001_centroid .

ex:building_B0001_footprint a owl:NamedIndividual , geo:Geometry ;
    geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/28992> POLYGON ((150100 170100, 150100 170106, 150110 170106, 150110 170100, 150100 170100))"^^geo:wktLiteral .

ex:building_B0001_centroid a owl:NamedIndividual , geo:Geometry ;
    geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/28992> POINT (150105 170103)"^^geo:wktLiteral .

ex:rooftop_B0001 a owl:NamedIndividual , :Rooftop ;
    rdfs:label             "Rooftop of building B0001"@en ;
    :is_part_of            ex:building_B0001 ;
    geo:hasDefaultGeometry ex:rooftop_B0001_geometry .

ex:rooftop_B0001_geometry a owl:NamedIndividual , geo:Geometry ;
    geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/7415> MULTIPOLYGON Z (((150100 170100 6, 150110 170100 6, 150110 170103 9, 150100 170103 9, 150100 170100 6)), ((150110 170106 6, 150100 170106 6, 150100 170103 9, 150110 170103 9, 150110 170106 6)))"^^geo:wktLiteral .
```

The key, identifiers, coordinates and CRS above are illustrative. `has_rooftop` and `is_part_of` are inverse properties; asserting both lets the queries work without a reasoner.

## 6. Converting a CityJSON file with the script

A city model usually contains thousands of buildings, so the individuals are generated with the script `scripts/cityjson_to_rdf.py`. It requires Python 3 and two libraries:

```
pip install rdflib shapely
```

Run it on your file:

```
python scripts/cityjson_to_rdf.py my_city.city.json buildings.ttl \
    --base "https://example.org/my-region#" \
    --crs-2d 28992 \
    --osm-attribute osm_id \
    --year-attribute yearOfConstruction
```

| Option | Default | Meaning |
|---|---|---|
| `--base` | `https://example.org/my-region#` | Your namespace. The data ontology IRI is the namespace without the final `#` or `/` |
| `--crs` | from the file | EPSG code of the file, if `metadata.referenceSystem` is missing |
| `--crs-2d` | same as the file | EPSG code for footprints and centroids. Set it to the horizontal part of a compound CRS |
| `--precision` | `3` | Decimals in the coordinates. 3 gives millimetres in a projected CRS. Use 7 or more for degrees |
| `--osm-attribute` | none | Name of the CityJSON attribute that holds the OSM identifier |
| `--osm-type` | `way` | OSM element type used when the identifier is only a number |
| `--year-attribute` | `yearOfConstruction` | Name of the CityJSON attribute that holds the construction year |
| `--district` | none | IRI of a district to assign to every building. Use it only if the whole file covers one district; otherwise see section 8 |

The script prints a summary (number of buildings, OSM links, construction years, missing footprints and roofs) and a warning for each building it could not complete.

**How the geometry is derived.** For each building, the script uses the geometry with the highest LoD, preferring geometries with semantic surfaces:

- **Footprint:** the union of the `GroundSurface` surfaces, projected to 2D. If there are none, the union of the 2D projections of all surfaces. For LoD0 this is the footprint itself; for LoD1 and LoD2 it includes roof overhangs.
- **Centroid:** the centroid of the footprint.
- **Rooftop geometry:** the `RoofSurface` surfaces, in 3D. If the geometry has no semantic surfaces, surfaces facing upwards (slope below about 78 degrees) are taken as roof. LoD0 geometries give no rooftop geometry.
- **Coordinates:** the CityJSON `transform` (scale and translate) is applied to the vertices.

**OpenStreetMap identifiers.** The attribute value can be a full URL, `way/123456`, `w123456` (also `r` and `n`), or a number (then `--osm-type` gives the type).

**Limits.**

- CityJSONSeq files (`.city.jsonl`) must first be converted to CityJSON, for example with `cjseq collect`.
- Geometry templates (`GeometryInstance`) are skipped.
- City objects other than `Building` and `BuildingPart` are ignored.
- Districts, owners and activation types are not in CityJSON files. Add them separately (sections 8 and 10).

## 7. Registering or completing a building in Protégé

Use Protégé to register a few buildings by hand or to complete generated buildings, for example with an owner or an extra rooftop. For a whole city model, use the script (section 6).

1. Open your data ontology (the one that imports the Rooftop Activation Ontology). Check in **Active ontology > Imports** that GeoSPARQL is loaded; otherwise the `geo:` terms are not available.
2. **Create the footprint.** Go to **Entities > Individuals**, click **Add individual** and enter `building_B0001_footprint`. In **Description > Types**, click **+** and select `Geometry` (GeoSPARQL). In **Property assertions > Data property assertions**, click **+**, select `asWKT`, paste the literal (for example `<http://www.opengis.net/def/crs/EPSG/0/28992> POLYGON ((...))`) and set the type to `geo:wktLiteral`.
3. **Create the centroid** in the same way (`building_B0001_centroid`, a `POINT`).
4. **Create the building.** Add the individual `building_B0001` and, in **Types**, select `Building`. In **Data property assertions**, add:
   - `has_city_model_id`, with the key and type `xsd:string`;
   - optionally `has_osm_element`, with the full URL and type `xsd:anyURI`;
   - optionally `has_construction_year`, with the year and type `xsd:integer`.
5. In **Object property assertions** of the building, add `hasDefaultGeometry` (the footprint), `hasCentroid` (the centroid) and `is_located_in` (the district).
6. **Create the rooftop.** Add the individual `rooftop_B0001` with type `Rooftop`. In **Object property assertions**, add `is_part_of` with the building. On the building, add `has_rooftop` with the rooftop. If you have a rooftop geometry, create it as in step 2 (with a `MULTIPOLYGON Z` literal) and link it with `hasDefaultGeometry`.
7. Save your data ontology.

To add data to generated buildings, do it in your hand-made file (see section 2), not in the generated file. In Protégé, open the hand-made file, which imports the generated file, and select the existing building individuals.

## 8. Linking buildings to districts

The queries of the association tutorial find a rooftop's region through `rooftop is_part_of building is_located_in district is_part_of_region region`, so every building needs a district.

- **One district per file.** If the city model covers a single district, run the script with `--district`.
- **By hand.** In Protégé, add `is_located_in` to each building (section 7, step 5).
- **By location.** If your districts have polygon geometries, compute the district of each building from its centroid with a GeoSPARQL query. This needs a triplestore with GeoSPARQL support (for example GraphDB, Apache Jena Fuseki with GeoSPARQL, or Stardog), loaded with the ontology, the buildings and the districts. Protégé cannot evaluate geometries.

```sparql
PREFIX :     <https://w3id.org/rooftop_activation#>
PREFIX bld:  <http://bimerr.iot.linkeddata.es/def/building#>
PREFIX geo:  <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

CONSTRUCT {
  ?building :is_located_in     ?district .
  ?district :contains_building ?building .
}
WHERE {
  ?building a bld:Building ;
            geo:hasCentroid/geo:asWKT ?point .
  ?district a ?districtClass ;
            geo:hasDefaultGeometry/geo:asWKT ?area .
  ?districtClass rdfs:subClassOf* :District .
  FILTER (geof:sfWithin(?point, ?area))
}
```

Save the result as a file and add it to your data. The centroid is used rather than the footprint so that a building crossing a district boundary is assigned to one district only. Keep centroids and district polygons in the same CRS: not all triplestores convert between coordinate systems.

## 9. Checking your data

**Consistency.** Run a reasoner (in Protégé: **Reasoner > HermiT > Start reasoner**). Two different construction years on the same building make the ontology inconsistent, because `has_construction_year` is functional. If the reasoner stops with an error about an unsupported datatype (`geo:wktLiteral`), run it on a copy of your data without the geometry individuals, or use another reasoner.

**Completeness.** Run this query on your data. It lists buildings and rooftops with missing values. Rooftops without geometry are expected for buildings modelled only in LoD0.

```sparql
PREFIX :     <https://w3id.org/rooftop_activation#>
PREFIX bld:  <http://bimerr.iot.linkeddata.es/def/building#>
PREFIX geo:  <http://www.opengis.net/ont/geosparql#>

SELECT ?item ?problem
WHERE {
  {
    ?item a bld:Building .
    FILTER NOT EXISTS { ?item :has_city_model_id ?id }
    BIND ("missing has_city_model_id" AS ?problem)
  } UNION {
    ?item a bld:Building .
    FILTER NOT EXISTS { ?item geo:hasDefaultGeometry/geo:asWKT ?w }
    BIND ("building without footprint" AS ?problem)
  } UNION {
    ?item a bld:Building .
    FILTER NOT EXISTS { ?item :has_rooftop ?r }
    BIND ("building without rooftop" AS ?problem)
  } UNION {
    ?item a bld:Building .
    FILTER NOT EXISTS { ?item :is_located_in ?d }
    BIND ("building without district" AS ?problem)
  } UNION {
    ?item a :Rooftop .
    FILTER NOT EXISTS { ?item :is_part_of ?b }
    BIND ("rooftop without building" AS ?problem)
  } UNION {
    ?item a :Rooftop .
    FILTER NOT EXISTS { ?item geo:hasDefaultGeometry/geo:asWKT ?w }
    BIND ("rooftop without geometry" AS ?problem)
  }
}
ORDER BY ?problem ?item
```

**Duplicated city model keys.** This query should return no rows:

```sparql
PREFIX :    <https://w3id.org/rooftop_activation#>
PREFIX bld: <http://bimerr.iot.linkeddata.es/def/building#>

SELECT ?cityModelId (COUNT(?b) AS ?entries) (GROUP_CONCAT(STR(?b); separator=", ") AS ?buildings)
WHERE {
  ?b a bld:Building ;
     :has_city_model_id ?id .
  BIND (STR(?id) AS ?cityModelId)
}
GROUP BY ?cityModelId
HAVING (COUNT(?b) > 1)
```

## 10. Using the buildings

**Activation types.** The city model gives the position and shape of rooftops, not their activation. Give each rooftop its activation type in your hand-made file, as explained in the association tutorial: assert the colour class (for example `ex:rooftop_B0001 a :Blue_Rooftop`) or its functions with `has_function`.

**Association queries.** Once rooftops have an activation type and their buildings a district, the rooftop IRIs (`ex:rooftop_<key>`) can be used directly in the queries of the association tutorial.

**Going back to the city model or the map.** This query lists the rooftops of a district with the key needed to find the building in the CityJSON file and its OpenStreetMap link. Replace `ex:district_07` with the IRI of your district.

```sparql
PREFIX :    <https://w3id.org/rooftop_activation#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX ex:  <https://example.org/my-region#>

SELECT ?rooftop ?cityModelId ?osm ?rooftopGeometry
WHERE {
  ?building :is_located_in      ex:district_07 ;   # <- replace with your district IRI
            :has_city_model_id  ?cityModelId ;
            :has_rooftop        ?rooftop .
  OPTIONAL { ?building :has_osm_element ?osm }
  OPTIONAL { ?rooftop geo:hasDefaultGeometry/geo:asWKT ?rooftopGeometry }
}
ORDER BY ?cityModelId
```

| Column | Meaning |
|---|---|
| `rooftop` | IRI of the rooftop |
| `cityModelId` | Key of the building in the `CityObjects` of the CityJSON file |
| `osm` | OpenStreetMap element of the building (empty if not registered) |
| `rooftopGeometry` | Roof surfaces as a 3D WKT multipolygon (empty for LoD0 buildings) |
