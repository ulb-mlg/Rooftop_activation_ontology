# Changelog

All notable changes to the ontology are documented here.
The format follows Keep a Changelog and the vocabulary uses semantic versioning.

## [2.2.0] - 2026-09-30

### Added
- Disjoint property to the eras
- Class `Specific_Incentive_Owner_Association` (subclass of `Association`) to register the degree between a specific incentive individual and an owner type. Restrictions: `relates_incentive some Incentive`, `relates_owner_type some owl:Thing`, `has_degree some xsd:decimal`.
- Object property `relates_incentive` (functional, domain `Association`, range `Incentive`). Unlike `relates_incentive_type`, its value is an incentive individual, not a punned class.
- Class `Owner_Challenge_Association` (subclass of `Association`) to register the priority of an urban challenge for an owner type, with a degree from 0 to 1. Restrictions: `relates_owner_type some owl:Thing`, `relates_challenge some Urban_Challenge`, `has_degree some xsd:decimal`.
- Class `District_Challenge_Association` (subclass of `Association`) to register the priority of an urban challenge for a district type, with a degree from 0 to 1. Restrictions: `relates_district_type some owl:Thing`, `relates_challenge some Urban_Challenge`, `has_degree some xsd:decimal`.
- Object property `relates_district_type` (functional, domain `Association`). Its value is a `District` subclass used as an individual (OWL 2 punning).
- Punned individual declarations for the 15 `District` subclasses, so they can be used as values of `relates_district_type`.

### Changed
- `Specific_Incentive_Owner_Association`, `Owner_Challenge_Association` and `District_Challenge_Association` added to the disjointness axiom of the association classes.
- Comment of `Association` updated: an association links two entities of the ontology, types or individuals.
- Ontology description and introduction updated to describe the new associations.
- `owl:versionInfo`, `owl:versionIRI`, `owl:priorVersion` (2.1.0) and `dcterms:modified` updated.

### Deprecated
- `has_owner_urban_challenge_priority`, `has_urban_challenge_owner_priority`, `has_district_urban_challenge_priority` and `has_urban_challenge_district_priority`. They could not carry a degree. Replaced by `Owner_Challenge_Association` and `District_Challenge_Association`.

### Documentation
- `association_degrees_documentation.md`:
	- Covers the three new association classes.
	- New rule 7: an association with a specific incentive replaces the associations of its types for the same owner type.
	- New rule 8: a degree of 0 excludes a specific incentive for an owner type.
	- New rule 9: a more specific district type replaces an inherited priority.
	- New "Districts" subsection on typing district individuals. Owner priorities on owner individuals removed.
	- Query 3 now applies the specific incentive associations first, and has a new `associationLevel` column.
	- New Query 4: challenges addressed by a rooftop, with the priorities of its district type and owner type.
	- Structure tables reorganised by association class.

### Fixed
- Completeness check query in `association_degrees_documentation.md`. Its `UNION` branches filtered on variables bound outside the branch, so most checks returned no rows. The query was rewritten with `VALUES` and a single `FILTER`.

In total: 231 classes, 75 object properties, 24 data properties and 154 named individuals.


## [2.1.0] - 2026-09-30

### Added
- **Geolocation of buildings and rooftops:** `Building` and `Rooftop` are now GeoSPARQL features (`geo:Feature`), so each can carry geometries, such as a footprint, a centroid or roof surfaces. A building has at most one default geometry (`geo:hasDefaultGeometry max 1 geo:Geometry`).
- **Links to external datasets:** two data properties on `Building`:
  - `has_osm_element` (`xsd:anyURI`) links a building to its OpenStreetMap way or relation.
  - `has_city_model_id` (`xsd:string`) links a building to its city object in a CityJSON 3D city model.
- **Documentation:** 
  - the `Building` and `Rooftop` comments explain how geometries and external identifiers are used, and `Rooftop` has a usage example (`skos:example`).
  - documentation for registering buildings from CityJSON and incentives

### Changed
- `Location` is relabelled "Urban Location Context", and its comment now states that it describes the urban-to-rural context, while the geographic position is given by GeoSPARQL geometries.
- Query 3 and owner registration in the association tutorial

### Fixed
- `owl:versionInfo` is now a literal instead of an IRI.
- `dcterms:modified` is now typed as `xsd:date`.

In total: 216 classes, 36 object properties, 5 data properties and 63 named individuals.

## [2.0.0] - 2026-09-29

### Added
- **Rooftops and buildings:** seven activation types (blue, green, yellow, red, purple, orange and gray), defined by 10 rooftop functions, and building attributes such as construction era, material, height, location and primary use. The construction era is inferred from the construction year.
- **Urban context:** districts classified by function and density, and regions (Brussels, Dublin, Île-de-France, Mannheim, Mechelen and Rotterdam).
- **Owners:** 11 owner types, aligned with `foaf:Person` and `org:Organization`.
- **Urban challenges:** 47 challenges grouped into 10 themes, including climate adaptation, affordable housing, decarbonising energy systems, mobility and governance.
- **Incentives:** 56 incentive instrument types, classified by nature, function, funding source, allocation mechanism, obligation attachment and project stage, plus 12 defined classes computed from these facets.
- **Weighted associations:** `Rooftop_Challenge_Association`, `Owner_Rooftop_Association` and `Incentive_Owner_Association`, each carrying a degree between 0 and 1 (`has_degree`) and optionally a region (`defined_for_region`).

In total: 216 classes, 36 object properties, 3 data properties and 63 named individuals.
