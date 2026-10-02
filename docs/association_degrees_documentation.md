# Registering association degrees

This section explains how to record, in your own data, how strongly rooftop activation types, urban challenges, owner types, district types, incentive types and specific incentives are associated, and how to query those associations for a given rooftop, including the actual owner of its building, the priorities of its owner and district, and the incentives implemented in its region.

## 1. What an association is

The ontology defines the types (rooftop colours, owner types, district types, incentive types) and the urban challenges. Specific incentives (for example a grant programme of a given city) are individuals registered by users. How strongly they relate to each other depends on local context, so these links are registered by the users of the ontology, typically local authorities.

Each link is registered as an individual of one of six association classes. The individual carries the two linked elements and a degree.

| Association class | Links | Question it answers |
|---|---|---|
| `Rooftop_Challenge_Association` | rooftop type and urban challenge | How much does this rooftop type contribute to addressing this challenge? |
| `Owner_Rooftop_Association` | owner type and rooftop type | How likely is this owner type to activate this rooftop type? |
| `Incentive_Owner_Association` | incentive type and owner type | How suitable is this incentive type for this owner type? |
| `Specific_Incentive_Owner_Association` | specific incentive and owner type | How suitable is this particular incentive for this owner type? |
| `Owner_Challenge_Association` | owner type and urban challenge | How high a priority is this challenge for this owner type? |
| `District_Challenge_Association` | district type and urban challenge | How high a priority is this challenge in this district type? |

Use `Specific_Incentive_Owner_Association` only when a particular incentive differs from what its type suggests, for example when its eligibility conditions favour or exclude some owner types. An association with a specific incentive replaces the associations of its types (section 4, rule 7).

Together they form a chain. For a rooftop of a given type, you can retrieve the challenges it addresses, the owner types likely to activate it, and the incentives those owners can use:

```
urban challenge  <-  rooftop type  <-  owner type  <-  incentive type or specific incentive
```

The two priority associations describe the demand side: which challenges matter most to an owner type and in a district type. They let you weight the challenges a rooftop addresses by the priorities of its owner and its district (Query 4):

```
owner type     ->  urban challenge   (priority)
district type  ->  urban challenge   (priority)
```

### Degree scale

The degree (`has_degree`) is a decimal from 0 to 1:

| Degree | Meaning |
|---|---|
| 0.0 | No association |
| 0.25 | Weak |
| 0.5 | Moderate |
| 0.75 | Strong |
| 1.0 | Primary purpose or strongest association |

Intermediate values are allowed. Use the same scale for all associations so that degrees from different regions can be compared.

For `Owner_Challenge_Association` and `District_Challenge_Association`, read the degree as a priority: 0.0 means the challenge is not a priority, 1.0 means it is the highest priority.

## 2. Before you start

1. **Create your own data file.** Do not edit the ontology. Create a separate ontology for your data that imports `https://w3id.org/rooftop_activation`, and use your own namespace for everything you create (in the examples below, `ex:` stands for `https://example.org/my-region#`).
2. **Identify your region.** Use an existing `Region` individual of the ontology (for example `:Brussels`) or create your own individual of type `Region`.
3. **Describe your rooftops so the region can be found.** The queries find a rooftop's region through this path:

   `rooftop  is_part_of  building  is_located_in  district  is_part_of_region  region`

   A rooftop without this path is still queried, but only associations valid for all regions are returned.
4. **Give each district its district type.** Type each district individual with the most specific `District` subclass that applies, for example `ex:district_07 a :Historical` (section 8). Query 4 uses it to find the district priorities.
5. **Give each rooftop its activation type.** Either assert the colour class directly (for example `ex:rooftop42 a :Blue_Rooftop`), or assert its functions with `has_function` and let a reasoner infer the colour. In the second case, see section 10 before querying.
6. **Register the owners of your buildings (optional).** Query 3 uses the actual owner of the building and the incentives implemented in your region. Query 4 uses the owner to find the owner priorities. It needs owner individuals (section 8) and incentive individuals, registered as explained in the incentive registration tutorial. Incentive individuals are also needed for any `Specific_Incentive_Owner_Association`.

## 3. Structure of an association

Each association class requires two linking properties:

| Association class | First property | Second property |
|---|---|---|
| `Rooftop_Challenge_Association` | `relates_rooftop_type` | `relates_challenge` |
| `Owner_Rooftop_Association` | `relates_owner_type` | `relates_rooftop_type` |
| `Incentive_Owner_Association` | `relates_incentive_type` | `relates_owner_type` |
| `Specific_Incentive_Owner_Association` | `relates_incentive` | `relates_owner_type` |
| `Owner_Challenge_Association` | `relates_owner_type` | `relates_challenge` |
| `District_Challenge_Association` | `relates_district_type` | `relates_challenge` |

All association classes also require `has_degree` and accept `defined_for_region`.

| Property | Value |
|---|---|
| `relates_rooftop_type` | A rooftop colour class, e.g. `:Blue_Rooftop` |
| `relates_challenge` | An urban challenge individual, e.g. `:Flood_risk` |
| `relates_owner_type` | An `Owner` subclass, e.g. `:Home_Owner_Associations` |
| `relates_district_type` | A `District` subclass, e.g. `:Historical` |
| `relates_incentive_type` | An `Incentive` instrument subclass, e.g. `:Grant` |
| `relates_incentive` | An incentive individual, e.g. `ex:inc_Brussels_green_roof_grant` |
| `has_degree` | Decimal from 0 to 1 (`xsd:decimal`). Required |
| `defined_for_region` | A `Region` individual. Optional: omit it for an association valid in all regions |

Each property takes exactly one value per association.

**Why a class name is used as a value.** Rooftop colours, owner types, district types and incentive types are classes. To be used as values of `relates_rooftop_type`, `relates_owner_type`, `relates_district_type` and `relates_incentive_type`, each of these classes is also declared as an individual with the same IRI (OWL 2 punning). This is already done in the ontology for all rooftop colours, owner types, district types and incentive instrument types. `relates_incentive` does not use punning: its value is an ordinary incentive individual.

**Valid values:**

- Rooftop types: the seven colour subclasses of `Rooftop` (`Blue_Rooftop`, `Gray_Rooftop`, `Green_Rooftop`, `Orange_Rooftop`, `Purple_Rooftop`, `Red_Rooftop`, `Yellow_Rooftop`).
- Urban challenges: the individuals of the `Urban_Challenge` subclasses.
- Owner types: any subclass of `Owner`.
- District types: any subclass of `District`.
- Incentive types: any instrument subclass of `Incentive`. Do not use the defined classes computed from facets (for example `Financial_Incentive` or `European_Incentive`).
- Specific incentives: individuals typed with an instrument subclass of `Incentive`, registered as explained in the incentive registration tutorial. Never use an incentive type as value of `relates_incentive`, or an incentive individual as value of `relates_incentive_type`.

**Provenance (recommended).** Add to each association:

- `dcterms:creator`: the authority that registered it;
- `dcterms:date`: the date it was registered or last reviewed;
- `rdfs:comment`: the source of the degree (study, survey, expert workshop, etc.).

## 4. Rules

1. **One association per pair and per region.** Do not register the same pair twice for the same region. To change a degree, edit the existing association. For a `Specific_Incentive_Owner_Association`, the pair is the incentive individual and the owner type.
2. **Regional values replace general values.** An association with `defined_for_region` replaces, for that region, an association of the same pair registered for all regions.
3. **Use a degree of 0 to cancel a general association locally.** If an association valid for all regions does not apply in your region, register the same pair for your region with degree 0. If there is simply no association, do not register anything.
4. **Register at the most general type that shares the same degree.** An owner, district or incentive association applies to all subclasses of the type. For example, an association with `:Grant` covers `:Pre-financed_Grant` and the other grant subclasses.
5. **A more specific owner type replaces an inherited value.** If `:Grant` is associated with `:Real_Estate` (degree 0.5) and also with `:Real_Estate_Corporate` (degree 0.9), the value 0.9 applies to `:Real_Estate_Corporate` and 0.5 to the other `Real_Estate` subclasses.
6. **A more specific incentive type replaces an inherited value.** If `:Grant` is associated with `:Home_Owner_Associations` (degree 0.5) and `:Pre-financed_Grant` also is (degree 0.9), the value 0.9 applies to pre-financed grants and 0.5 to the other grants. This matters when concrete incentives are matched to an owner (Query 3).
7. **An association with a specific incentive replaces the associations of its types.** If an incentive individual has its own association with an owner type, that association is used for this incentive and that owner type (and its subclasses, as in rule 5). The associations registered for the incentive's types are then ignored for this pair, whatever the owner type or region at which they were registered. For example, if `:Grant` is associated with `:Home_Owner_Associations` (degree 0.5, Brussels) and the individual `ex:inc_Brussels_green_roof_grant`, of type `:Grant`, is associated with `:Home_Owner_Associations` (degree 0.7, all regions), the value 0.7 applies to that grant for homeowners' associations, and 0.5 to the other grants in Brussels. For owner types without a specific association for this incentive, the type associations still apply. Among the specific associations of the same incentive, rules 2 and 5 apply.
8. **Use a degree of 0 to exclude a specific incentive.** If an incentive does not apply to an owner type although its type does, register a specific association for that owner type with degree 0.
9. **A more specific district type replaces an inherited value.** If `:City_Center` has a priority of 0.5 for `:Flood_risk` and `:Historical` has 0.8, the value 0.8 applies to historical city centres and 0.5 to the other city centres. Rule 5 applies in the same way to owner priorities.

Order of precedence when several associations match a concrete incentive and an owner: first an association with the incentive individual (rule 7); otherwise the associations of its types, applying rules 5 and 6. At each level, a regional value replaces a general one (rule 2).

A specific incentive is implemented in a region (`implemented_in`), so `defined_for_region` is usually unnecessary on its associations.

## 5. Registering associations in Turtle

```turtle
@prefix :        <https://w3id.org/rooftop_activation#> .
@prefix ex:      <https://example.org/my-region#> .
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<https://example.org/my-region> a owl:Ontology ;
    owl:imports <https://w3id.org/rooftop_activation> .

# Rooftop type -> urban challenge
ex:assoc_Brussels_Blue_Rooftop_Flood_risk
    a owl:NamedIndividual , :Rooftop_Challenge_Association ;
    :relates_rooftop_type :Blue_Rooftop ;
    :relates_challenge    :Flood_risk ;
    :has_degree           "0.9"^^xsd:decimal ;
    :defined_for_region   :Brussels ;
    dcterms:creator       "Brussels Environment" ;
    dcterms:date          "2026-10-01"^^xsd:date ;
    rdfs:comment          "Source: regional stormwater plan."@en .

# Owner type -> rooftop type
ex:assoc_Brussels_Home_Owner_Associations_Blue_Rooftop
    a owl:NamedIndividual , :Owner_Rooftop_Association ;
    :relates_owner_type   :Home_Owner_Associations ;
    :relates_rooftop_type :Blue_Rooftop ;
    :has_degree           "0.7"^^xsd:decimal ;
    :defined_for_region   :Brussels .

# Incentive type -> owner type (no region: valid in all regions)
ex:assoc_Grant_Home_Owner_Associations
    a owl:NamedIndividual , :Incentive_Owner_Association ;
    :relates_incentive_type :Grant ;
    :relates_owner_type     :Home_Owner_Associations ;
    :has_degree             "0.8"^^xsd:decimal .
```

The names, dates and sources above are illustrative. A naming convention such as `assoc_<Region>_<FirstType>_<SecondType>` makes associations easy to find and prevents duplicates.

An association with a specific incentive follows the same pattern. The incentive individual must already exist, registered as explained in the incentive registration tutorial:

```turtle
# Specific incentive -> owner type (replaces the Grant association for this incentive)
ex:assoc_inc_Brussels_green_roof_grant_Home_Owner_Associations
    a owl:NamedIndividual , :Specific_Incentive_Owner_Association ;
    :relates_incentive  ex:inc_Brussels_green_roof_grant ;
    :relates_owner_type :Home_Owner_Associations ;
    :has_degree         "0.7"^^xsd:decimal ;
    rdfs:comment        "Source: eligibility conditions favour co-owned buildings."@en .
```

For these associations, use the convention `assoc_<Incentive>_<OwnerType>`.

Priority associations follow the same pattern:

```turtle
# Owner type -> urban challenge (priority)
ex:assoc_Real_Estate_Corporate_Flood_risk
    a owl:NamedIndividual , :Owner_Challenge_Association ;
    :relates_owner_type :Real_Estate_Corporate ;
    :relates_challenge  :Flood_risk ;
    :has_degree         "0.6"^^xsd:decimal .

# District type -> urban challenge (priority)
ex:assoc_Brussels_Historical_Flood_risk
    a owl:NamedIndividual , :District_Challenge_Association ;
    :relates_district_type :Historical ;
    :relates_challenge     :Flood_risk ;
    :has_degree            "0.8"^^xsd:decimal ;
    :defined_for_region    :Brussels .
```

## 6. Registering associations in Protégé

1. Open your data ontology (the one that imports the Rooftop Activation Ontology).
2. Go to **Entities > Individuals** and click **Add individual**. Enter the name, for example `assoc_Brussels_Blue_Rooftop_Flood_risk`, and check that the IRI uses your namespace.
3. In **Description > Types**, click **+** and select the association class, for example `Rooftop_Challenge_Association`.
4. In **Property assertions > Object property assertions**, click **+** for each link:
   - `relates_rooftop_type` and select `Blue_Rooftop`;
   - `relates_challenge` and select `Flood_risk`;
   - optionally `defined_for_region` and select your region.
5. In **Property assertions > Data property assertions**, click **+**, select `has_degree`, enter the value (for example `0.9`) and set the type to `xsd:decimal`.
6. In **Annotations**, click **+** to add `dcterms:creator`, `dcterms:date` and an `rdfs:comment` with the source.
7. Save your data ontology.

For a `Specific_Incentive_Owner_Association`, in step 3 select `Specific_Incentive_Owner_Association`, and in step 4 add `relates_incentive` (select the incentive individual) and `relates_owner_type` (select the owner type). The incentive individual must be in your data ontology or in a file it imports.

For an `Owner_Challenge_Association` or a `District_Challenge_Association`, in step 4 add `relates_owner_type` (select the owner type) or `relates_district_type` (select the district type), and `relates_challenge` (select the urban challenge).

For many associations, prepare them in a spreadsheet (one row per association) and import them with the Cellfie plugin (**Tools > Create axioms from Excel workbook**), or convert the spreadsheet to Turtle with a script.

## 7. Adding new owner, district or incentive types

If you extend the ontology with a new subclass of `Owner`, `District` or `Incentive`, also declare an individual with exactly the same IRI. Otherwise the new type cannot be used in associations. Incentive individuals do not need this declaration.

In Protégé: **Entities > Individuals > Add individual**, enter exactly the class name, and check that the IRI is identical to the class IRI. Do not add types or annotations to this individual; it shares the class annotations.

## 8. Registering building owners and districts

Associations are registered between owner *types*. To find the incentives available to the actual owner of a building (Query 3) and the owner's priorities (Query 4), register the owner as an individual and link the building to it.

| Property | On | Required | Value |
|---|---|---|---|
| `rdf:type` | owner | required | **One** `Owner` subclass, the most specific that applies, e.g. `:Home_Owner_Associations`. The owner types are disjoint, so an owner cannot have two |
| `rdfs:label` | owner | recommended | A name or reference for the owner |
| `is_owned_by` | building | required | The owner individual |

Owner priorities are registered for owner types with `Owner_Challenge_Association` (section 5), not on owner individuals. The properties `has_owner_urban_challenge_priority` and `has_district_urban_challenge_priority`, and their inverses, are deprecated: they could not carry a degree. Do not use them in new data.

Rules:

1. **One owner individual per party.** A party owning several buildings is one individual, linked from each building. Co-owners who decide together through an association (for example a homeowners' association) are one individual of that type.
2. **Never use an owner type as the owner.** `:Home_Owner_Associations` as value of `is_owned_by` would refer to the type, not to a party. Always create an individual.
3. **Protect personal data.** Owners of type `Private_Individual`, and sometimes `Landlords`, are natural persons. Use a pseudonymous identifier (for example `ex:owner_0042`) and a neutral label, and keep names and contact details outside the ontology.

In Turtle:

```turtle
ex:owner_0042 a owl:NamedIndividual , :Home_Owner_Associations ;
    rdfs:label "Homeowners' association 0042"@en .

ex:building_B0001 :is_owned_by ex:owner_0042 .
```

In Protégé:

1. Go to **Entities > Individuals**, click **Add individual** and enter the name, for example `owner_0042`.
2. In **Description > Types**, click **+** and select the owner type.
3. In **Annotations**, add an `rdfs:label`.
4. Select the building individual. In **Property assertions > Object property assertions**, click **+**, select `is_owned_by` and then the owner.
5. Save your data ontology.

If your buildings are generated from a CityJSON file, add the owners and the `is_owned_by` links in your hand-made file, not in the generated one, so that they survive a regeneration.

### Districts

Priorities are registered between district *types*. To find the priorities of the district of a rooftop (Query 4), type each district individual with its district type.

| Property | On | Required | Value |
|---|---|---|---|
| `rdf:type` | district | required | **One** `District` subclass, the most specific that applies, e.g. `:Historical` |
| `is_part_of_region` | district | required | The region individual |
| `is_located_in` | building | required | The district individual |

The top-level district types (`City_Center`, `Green_Areas`, `Industrial_and_Service_Districts`, `Residential`, `Sub-center`, `Unused_Areas`) are disjoint, so a district cannot belong to two of them. As for owners, never use a district type as value of `is_located_in`: always create a district individual.

```turtle
ex:district_07 a owl:NamedIndividual , :Historical ;
    rdfs:label "Historic centre"@en ;
    :is_part_of_region :Brussels .

ex:building_B0001 :is_located_in ex:district_07 .
```

## 9. Checking your data

**Consistency.** Run a reasoner (in Protégé: **Reasoner > HermiT > Start reasoner**). Two different degrees on the same association make the ontology inconsistent, because `has_degree` is functional.

**Completeness.** OWL does not report missing values: an association without a degree is not an error for a reasoner. Run these two queries on your data to find incomplete and duplicated associations. Both should return no rows.

Missing or invalid values:

```sparql
PREFIX :     <https://w3id.org/rooftop_activation#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?association ?problem
WHERE {
  ?association a ?kind .
  ?kind rdfs:subClassOf :Association .
  OPTIONAL { ?association :has_degree ?d }
  VALUES ?problem {
    "missing has_degree"
    "degree outside 0-1"
    "missing relates_rooftop_type"
    "missing relates_challenge"
    "missing relates_district_type"
    "missing relates_owner_type"
    "missing relates_incentive_type"
    "missing relates_incentive"
    "relates_incentive is not an incentive individual"
    "incentive type and specific incentive on the same association"
  }
  FILTER (
    (?problem = "missing has_degree" && !BOUND(?d))
    || (?problem = "degree outside 0-1" && BOUND(?d) && (?d < 0 || ?d > 1))
    || (?problem = "missing relates_rooftop_type"
        && ?kind IN (:Rooftop_Challenge_Association, :Owner_Rooftop_Association)
        && NOT EXISTS { ?association :relates_rooftop_type ?x })
    || (?problem = "missing relates_challenge"
        && ?kind IN (:Rooftop_Challenge_Association, :Owner_Challenge_Association, :District_Challenge_Association)
        && NOT EXISTS { ?association :relates_challenge ?x })
    || (?problem = "missing relates_district_type"
        && ?kind = :District_Challenge_Association
        && NOT EXISTS { ?association :relates_district_type ?x })
    || (?problem = "missing relates_owner_type"
        && ?kind IN (:Owner_Rooftop_Association, :Incentive_Owner_Association, :Specific_Incentive_Owner_Association, :Owner_Challenge_Association)
        && NOT EXISTS { ?association :relates_owner_type ?x })
    || (?problem = "missing relates_incentive_type"
        && ?kind = :Incentive_Owner_Association
        && NOT EXISTS { ?association :relates_incentive_type ?x })
    || (?problem = "missing relates_incentive"
        && ?kind = :Specific_Incentive_Owner_Association
        && NOT EXISTS { ?association :relates_incentive ?x })
    || (?problem = "relates_incentive is not an incentive individual"
        && EXISTS { ?association :relates_incentive ?x }
        && NOT EXISTS { ?association :relates_incentive ?x . ?x a ?c . ?c rdfs:subClassOf+ :Incentive })
    || (?problem = "incentive type and specific incentive on the same association"
        && EXISTS { ?association :relates_incentive_type ?x ; :relates_incentive ?y })
  )
}
ORDER BY ?association
```

The "not an incentive individual" check needs the ontology and your data in the same dataset (see section 10).

Duplicated pairs (same association class, same pair, same region):

```sparql
PREFIX :     <https://w3id.org/rooftop_activation#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?kind ?pair ?region (COUNT(?a) AS ?entries) (GROUP_CONCAT(STR(?a); separator=", ") AS ?associations)
WHERE {
  ?a a ?kind .
  ?kind rdfs:subClassOf :Association .
  OPTIONAL { ?a :relates_rooftop_type   ?rt }
  OPTIONAL { ?a :relates_challenge      ?ch }
  OPTIONAL { ?a :relates_owner_type     ?ot }
  OPTIONAL { ?a :relates_district_type  ?dt }
  OPTIONAL { ?a :relates_incentive_type ?it }
  OPTIONAL { ?a :relates_incentive      ?si }
  OPTIONAL { ?a :defined_for_region     ?r }
  BIND (CONCAT(COALESCE(STR(?rt), ""), " | ", COALESCE(STR(?ch), ""), " | ",
               COALESCE(STR(?ot), ""), " | ", COALESCE(STR(?dt), ""), " | ",
               COALESCE(STR(?it), ""), " | ", COALESCE(STR(?si), "")) AS ?pair)
  BIND (COALESCE(STR(?r), "all regions") AS ?region)
}
GROUP BY ?kind ?pair ?region
HAVING (COUNT(?a) > 1)
```

## 10. Querying the associations of a rooftop

Run the queries on a dataset that contains **both the ontology and your data**, because they use the class hierarchy of the ontology (for owner, district and incentive type inheritance). For example, load both files into the same triplestore, or merge them.

If the activation type of your rooftops is inferred from `has_function` rather than asserted, or if the types of your owners, districts or incentives are inferred, the inferred types must be available to the query. Either export the inferred axioms first (in Protégé: **File > Export inferred axioms as ontology**) or use a query engine with OWL reasoning.

In all queries, replace `ex:rooftop42` with the IRI of your rooftop.

### Query 1: urban challenges addressed by a rooftop

```sparql
PREFIX :     <https://w3id.org/rooftop_activation#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ex:   <https://example.org/my-region#>

SELECT ?rooftopType ?challenge ?degree ?definedFor
WHERE {
  BIND (ex:rooftop42 AS ?rooftop)   # <- replace with your rooftop IRI

  # 1. Region of the rooftop (rooftop -> building -> district -> region)
  OPTIONAL { ?rooftop :is_part_of/:is_located_in/:is_part_of_region ?foundRegion }
  BIND (COALESCE(?foundRegion, <urn:no-region>) AS ?region)

  # 2. Activation type(s) of the rooftop
  ?rooftop a ?rooftopType .
  ?rooftopType rdfs:subClassOf :Rooftop .

  # 3. Matching associations: regional ones for this region, or general ones
  ?a a :Rooftop_Challenge_Association ;
     :relates_rooftop_type ?rooftopType ;
     :relates_challenge    ?challenge ;
     :has_degree           ?degree .
  OPTIONAL { ?a :defined_for_region ?r }
  FILTER (!BOUND(?r) || ?r = ?region)

  # 4. A regional association replaces the general one for the same pair
  FILTER (BOUND(?r) || NOT EXISTS {
    ?other a :Rooftop_Challenge_Association ;
           :relates_rooftop_type ?rooftopType ;
           :relates_challenge    ?challenge ;
           :defined_for_region   ?region .
  })
  BIND (IF(BOUND(?r), ?r, "all regions") AS ?definedFor)
}
ORDER BY DESC(?degree)
```

| Column | Meaning |
|---|---|
| `rooftopType` | Activation type of the rooftop |
| `challenge` | Urban challenge the rooftop type contributes to addressing |
| `degree` | Degree of the association |
| `definedFor` | Region of the association, or "all regions" |

### Query 2: owner types likely to activate the rooftop, and their incentives

Query 2 works with types only. Associations with specific incentives (`Specific_Incentive_Owner_Association`) are not used here. They are used by Query 3.

```sparql
PREFIX :     <https://w3id.org/rooftop_activation#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ex:   <https://example.org/my-region#>

SELECT ?rooftopType ?ownerType ?ownerDegree ?incentiveType ?incentiveDegree ?incentiveDefinedAtOwner ?incentiveDefinedFor
WHERE {
  BIND (ex:rooftop42 AS ?rooftop)   # <- replace with your rooftop IRI

  OPTIONAL { ?rooftop :is_part_of/:is_located_in/:is_part_of_region ?foundRegion }
  BIND (COALESCE(?foundRegion, <urn:no-region>) AS ?region)

  ?rooftop a ?rooftopType .
  ?rooftopType rdfs:subClassOf :Rooftop .

  # Owner types likely to activate this rooftop type
  ?o a :Owner_Rooftop_Association ;
     :relates_rooftop_type ?rooftopType ;
     :relates_owner_type   ?ownerType ;
     :has_degree           ?ownerDegree .
  OPTIONAL { ?o :defined_for_region ?ro }
  FILTER (!BOUND(?ro) || ?ro = ?region)
  FILTER (BOUND(?ro) || NOT EXISTS {
    ?o2 a :Owner_Rooftop_Association ;
        :relates_rooftop_type ?rooftopType ;
        :relates_owner_type   ?ownerType ;
        :defined_for_region   ?region .
  })

  # Incentives for that owner type, also inherited from its superclasses
  OPTIONAL {
    ?ownerType rdfs:subClassOf* ?incentiveDefinedAtOwner .
    ?i a :Incentive_Owner_Association ;
       :relates_owner_type     ?incentiveDefinedAtOwner ;
       :relates_incentive_type ?incentiveType ;
       :has_degree             ?incentiveDegree .
    OPTIONAL { ?i :defined_for_region ?ri }
    FILTER (!BOUND(?ri) || ?ri = ?region)
    # regional replaces general for the same incentive and owner level
    FILTER (BOUND(?ri) || NOT EXISTS {
      ?i2 a :Incentive_Owner_Association ;
          :relates_owner_type     ?incentiveDefinedAtOwner ;
          :relates_incentive_type ?incentiveType ;
          :defined_for_region     ?region .
    })
    # a more specific owner level replaces an inherited one
    FILTER NOT EXISTS {
      ?i3 a :Incentive_Owner_Association ;
          :relates_owner_type     ?closer ;
          :relates_incentive_type ?incentiveType .
      ?ownerType rdfs:subClassOf* ?closer .
      ?closer rdfs:subClassOf+ ?incentiveDefinedAtOwner .
      OPTIONAL { ?i3 :defined_for_region ?r3 }
      FILTER (!BOUND(?r3) || ?r3 = ?region)
    }
    BIND (IF(BOUND(?ri), ?ri, "all regions") AS ?incentiveDefinedFor)
  }
}
ORDER BY DESC(?ownerDegree) DESC(?incentiveDegree)
```

| Column | Meaning |
|---|---|
| `rooftopType` | Activation type of the rooftop |
| `ownerType` | Owner type likely to activate this rooftop type |
| `ownerDegree` | Degree of the owner-rooftop association |
| `incentiveType` | Incentive type suitable for that owner type (empty if none is registered) |
| `incentiveDegree` | Degree of the incentive-owner association |
| `incentiveDefinedAtOwner` | Owner type at which the incentive association was registered (the owner type itself or one of its superclasses) |
| `incentiveDefinedFor` | Region of the incentive association, or "all regions" |

### Example

With these registered associations:

| Association | Region | Degree |
|---|---|---|
| `Blue_Rooftop` - `Flood_risk` | all regions | 0.5 |
| `Blue_Rooftop` - `Flood_risk` | Brussels | 0.9 |
| `Blue_Rooftop` - `Drought_resistance` | all regions | 0.6 |
| `Blue_Rooftop` - `Lack_of_water` | Rotterdam | 0.3 |
| `Real_Estate_Corporate` - `Blue_Rooftop` | all regions | 0.6 |
| `Grant` - `Real_Estate` | all regions | 0.5 |
| `Grant` - `Real_Estate_Corporate` | Brussels | 0.9 |
| `Green_Bond` - `Real_Estate` | all regions | 0.4 |

For a blue rooftop in Brussels, Query 1 returns:

| rooftopType | challenge | degree | definedFor |
|---|---|---|---|
| Blue_Rooftop | Flood_risk | 0.9 | Brussels |
| Blue_Rooftop | Drought_resistance | 0.6 | all regions |

The Brussels value replaces the general value for `Flood_risk`, and the Rotterdam association is ignored.

Query 2 returns:

| ownerType | ownerDegree | incentiveType | incentiveDegree | incentiveDefinedAtOwner | incentiveDefinedFor |
|---|---|---|---|---|---|
| Real_Estate_Corporate | 0.6 | Grant | 0.9 | Real_Estate_Corporate | Brussels |
| Real_Estate_Corporate | 0.6 | Green_Bond | 0.4 | Real_Estate | all regions |

`Grant` uses the Brussels value registered for `Real_Estate_Corporate`, which replaces the value inherited from `Real_Estate`. `Green_Bond` is inherited from `Real_Estate`.

For a blue rooftop outside Brussels, the same data returns `Flood_risk` with degree 0.5 and `Grant` with degree 0.5 (inherited from `Real_Estate`).

### Query 3: owner of the rooftop and the incentives available to it

Query 2 works with types: it lists the owner types likely to activate a rooftop type and the incentive types suitable for them. Query 3 works with individuals: it starts from the actual owner of the building (section 8) and returns the incentives implemented in the rooftop's region that suit that owner, with the degree of the matching association.

For each incentive individual, the query first looks for an association registered for that individual and the owner's type (or a supertype). If there is one, it is used (rule 7 of section 4). Otherwise, the query looks for an association between the incentive's type (or a supertype) and the owner's type (or a supertype). Rules 2, 5 and 6 of section 4 apply: a regional value replaces a general one, and the association registered at the most specific owner type and incentive type is used.

It requires:

- the path `rooftop is_part_of building is_located_in district is_part_of_region region`;
- `is_owned_by` on the building, with an owner individual of an `Owner` subclass;
- incentive individuals with `implemented_in` your region (see the incentive registration tutorial).

```sparql
PREFIX :     <https://w3id.org/rooftop_activation#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ex:   <https://example.org/my-region#>

SELECT DISTINCT ?owner ?ownerType ?incentive ?incentiveLabel ?associationLevel ?incentiveType ?degree ?degreeDefinedFor ?supportsRooftopType
WHERE {
  BIND (ex:rooftop42 AS ?rooftop)   # <- replace with your rooftop IRI

  # 1. Building, region and owner of the rooftop
  ?rooftop :is_part_of ?building .
  ?building :is_located_in/:is_part_of_region ?region ;
            :is_owned_by ?owner .
  ?owner a ?ownerType .
  ?ownerType rdfs:subClassOf+ :Owner .

  # 2. Incentives implemented in that region
  ?incentive :implemented_in ?region ;
             a ?incentiveClass .
  ?incentiveClass rdfs:subClassOf+ :Incentive .
  OPTIONAL { ?incentive rdfs:label ?incentiveLabel }

  # 3a. Association registered for this incentive individual and the owner's type (or a supertype)
  OPTIONAL {
    ?ownerType rdfs:subClassOf* ?specificOwnerLevel .
    ?s a :Specific_Incentive_Owner_Association ;
       :relates_incentive  ?incentive ;
       :relates_owner_type ?specificOwnerLevel ;
       :has_degree         ?specificDegree .
    OPTIONAL { ?s :defined_for_region ?rs }
    FILTER (!BOUND(?rs) || ?rs = ?region)
    # regional replaces general for the same pair
    FILTER (BOUND(?rs) || NOT EXISTS {
      ?s2 a :Specific_Incentive_Owner_Association ;
          :relates_incentive  ?incentive ;
          :relates_owner_type ?specificOwnerLevel ;
          :defined_for_region ?region .
    })
    # a more specific owner type replaces an inherited one
    FILTER NOT EXISTS {
      ?s3 a :Specific_Incentive_Owner_Association ;
          :relates_incentive  ?incentive ;
          :relates_owner_type ?closerSpecificOwner .
      ?ownerType rdfs:subClassOf* ?closerSpecificOwner .
      ?closerSpecificOwner rdfs:subClassOf+ ?specificOwnerLevel .
      OPTIONAL { ?s3 :defined_for_region ?rs3 }
      FILTER (!BOUND(?rs3) || ?rs3 = ?region)
    }
  }

  # 3b. Otherwise, association between the incentive's type (or a supertype) and the owner's type (or a supertype)
  OPTIONAL {
    ?incentiveClass rdfs:subClassOf* ?incentiveType .
    ?ownerType rdfs:subClassOf* ?ownerLevel .
    ?a a :Incentive_Owner_Association ;
       :relates_incentive_type ?incentiveType ;
       :relates_owner_type     ?ownerLevel ;
       :has_degree             ?typeDegree .
    OPTIONAL { ?a :defined_for_region ?ra }
    # an association with the incentive individual replaces the type associations
    FILTER (!BOUND(?specificDegree))
    FILTER (!BOUND(?ra) || ?ra = ?region)
    # regional replaces general for the same pair
    FILTER (BOUND(?ra) || NOT EXISTS {
      ?a2 a :Incentive_Owner_Association ;
          :relates_incentive_type ?incentiveType ;
          :relates_owner_type     ?ownerLevel ;
          :defined_for_region     ?region .
    })
    # a more specific owner type or incentive type replaces an inherited one
    FILTER NOT EXISTS {
      ?a3 a :Incentive_Owner_Association ;
          :relates_incentive_type ?closerIncentive ;
          :relates_owner_type     ?closerOwner .
      ?incentiveClass rdfs:subClassOf* ?closerIncentive .
      ?closerIncentive rdfs:subClassOf* ?incentiveType .
      ?ownerType rdfs:subClassOf* ?closerOwner .
      ?closerOwner rdfs:subClassOf* ?ownerLevel .
      FILTER (?closerIncentive != ?incentiveType || ?closerOwner != ?ownerLevel)
      OPTIONAL { ?a3 :defined_for_region ?r3 }
      FILTER (!BOUND(?r3) || ?r3 = ?region)
    }
  }

  FILTER (BOUND(?specificDegree) || BOUND(?typeDegree))
  BIND (COALESCE(?specificDegree, ?typeDegree) AS ?degree)
  BIND (IF(BOUND(?specificDegree), "incentive", "incentive type") AS ?associationLevel)
  BIND (IF(BOUND(?specificDegree),
           IF(BOUND(?rs), ?rs, "all regions"),
           IF(BOUND(?ra), ?ra, "all regions")) AS ?degreeDefinedFor)

  # 4. Does the incentive support the activation type of this rooftop?
  BIND (EXISTS {
    ?incentive a ?anyRestriction .
    ?anyRestriction owl:onProperty :incentive_associated_to_rooftop .
  } AS ?statesRooftopTypes)
  BIND (IF(!?statesRooftopTypes, "not stated",
        IF(EXISTS {
             ?rooftop a ?rooftopType .
             ?incentive a ?restriction .
             ?restriction owl:onProperty :incentive_associated_to_rooftop ;
                          owl:someValuesFrom ?rooftopType .
           }, "yes", "no")) AS ?supportsRooftopType)
}
ORDER BY DESC(?degree) ?incentive
```

| Column | Meaning |
|---|---|
| `owner` | Owner of the building |
| `ownerType` | Type of the owner |
| `incentive` | Incentive implemented in the rooftop's region |
| `incentiveLabel` | Name of the incentive |
| `associationLevel` | `incentive` if the association was registered for the incentive individual, `incentive type` if it was registered for one of its types |
| `incentiveType` | Incentive type at which the matching association was registered (the incentive's type or one of its supertypes). Empty when `associationLevel` is `incentive` |
| `degree` | Degree of the association |
| `degreeDefinedFor` | Region of the association, or "all regions" |
| `supportsRooftopType` | `yes` if the incentive states that it supports the rooftop's activation type (with `incentive_associated_to_rooftop`), `no` if it states other types only, `not stated` if it states none |

Incentives without a matching association are not returned. To see all incentives of the region, register an association for them, or remove steps 3a, 3b and the `FILTER` that follows them.

#### Example

With a green rooftop in Brussels, whose building is owned by `ex:owner_0042` (a `Home_Owner_Associations`), and these registered associations:

| Association | Region | Degree |
|---|---|---|
| `Grant` - `Home_Owner_Associations` | all regions | 0.5 |
| `Pre-financed_Grant` - `Home_Owner_Associations` | Brussels | 0.9 |
| `Advisory_Service` - `Owner` | all regions | 0.75 |
| `Tax_Credit` - `Home_Owner_Associations` | all regions | 0.25 |
| `inc_Brussels_green_roof_grant` - `Home_Owner_Associations` (specific) | all regions | 0.7 |
| `inc_Brussels_rooftop_advice` - `Landlords` (specific) | all regions | 0.2 |

and these incentive individuals:

| Incentive | Type | Region | Rooftop type stated |
|---|---|---|---|
| `inc_Brussels_green_roof_grant` | `Grant` | Brussels | `Green_Rooftop` |
| `inc_Brussels_prefinanced_water_grant` | `Pre-financed_Grant` | Brussels | `Blue_Rooftop` |
| `inc_Brussels_rooftop_advice` | `Advisory_Service` | Brussels | none |
| `inc_Rotterdam_rooftop_advice` | `Advisory_Service` | Rotterdam | none |

Query 3 returns:

| incentive | associationLevel | incentiveType | degree | degreeDefinedFor | supportsRooftopType |
|---|---|---|---|---|---|
| inc_Brussels_prefinanced_water_grant | incentive type | Pre-financed_Grant | 0.9 | Brussels | no |
| inc_Brussels_rooftop_advice | incentive type | Advisory_Service | 0.75 | all regions | not stated |
| inc_Brussels_green_roof_grant | incentive | | 0.7 | all regions | yes |

The pre-financed grant uses the value registered for `Pre-financed_Grant`, which replaces the value inherited from `Grant` (rule 6). The green roof grant uses its own association, which replaces the value 0.5 of its type `Grant` (rule 7). The advice desk inherits the association registered for all owners: its specific association concerns `Landlords` only, so it does not apply to a homeowners' association. The Rotterdam incentive is not in the rooftop's region, and no tax credit is implemented in Brussels, so neither appears.

### Query 4: challenges addressed by a rooftop, with the priorities of its district and owner

Query 4 extends Query 1. For each urban challenge the rooftop's activation type contributes to addressing, it adds the priority of that challenge for the rooftop's district type and for the owner's type. Rules 2, 5 and 9 of section 4 apply: a regional value replaces a general one, and the priority registered at the most specific district type and owner type is used.

It requires, in addition to the requirements of Query 1:

- `is_located_in` on the building, with a district individual typed with a `District` subclass (section 8);
- optionally, `is_owned_by` on the building, with an owner individual of an `Owner` subclass (section 8).

If the district or the owner is missing, the corresponding columns are empty.

```sparql
PREFIX :     <https://w3id.org/rooftop_activation#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ex:   <https://example.org/my-region#>

SELECT ?rooftopType ?challenge ?contribution
       ?districtType ?districtPriority ?districtPriorityDefinedAt ?districtPriorityDefinedFor
       ?ownerType ?ownerPriority ?ownerPriorityDefinedAt ?ownerPriorityDefinedFor
WHERE {
  BIND (ex:rooftop42 AS ?rooftop)   # <- replace with your rooftop IRI

  # 1. Region, district type and owner type of the rooftop (most specific types only)
  OPTIONAL { ?rooftop :is_part_of/:is_located_in/:is_part_of_region ?foundRegion }
  BIND (COALESCE(?foundRegion, <urn:no-region>) AS ?region)
  OPTIONAL {
    ?rooftop :is_part_of/:is_located_in ?district .
    ?district a ?districtType .
    ?districtType rdfs:subClassOf+ :District .
    FILTER NOT EXISTS { ?district a ?subDistrictType . ?subDistrictType rdfs:subClassOf+ ?districtType }
  }
  BIND (COALESCE(?districtType, <urn:no-district>) AS ?districtKey)
  OPTIONAL {
    ?rooftop :is_part_of/:is_owned_by ?owner .
    ?owner a ?ownerType .
    ?ownerType rdfs:subClassOf+ :Owner .
    FILTER NOT EXISTS { ?owner a ?subOwnerType . ?subOwnerType rdfs:subClassOf+ ?ownerType }
  }
  BIND (COALESCE(?ownerType, <urn:no-owner>) AS ?ownerKey)

  # 2. Challenges addressed by the rooftop's activation type (as in Query 1)
  ?rooftop a ?rooftopType .
  ?rooftopType rdfs:subClassOf :Rooftop .
  ?c a :Rooftop_Challenge_Association ;
     :relates_rooftop_type ?rooftopType ;
     :relates_challenge    ?challenge ;
     :has_degree           ?contribution .
  OPTIONAL { ?c :defined_for_region ?rc }
  FILTER (!BOUND(?rc) || ?rc = ?region)
  FILTER (BOUND(?rc) || NOT EXISTS {
    ?c2 a :Rooftop_Challenge_Association ;
        :relates_rooftop_type ?rooftopType ;
        :relates_challenge    ?challenge ;
        :defined_for_region   ?region .
  })

  # 3. Priority of the challenge for the district type (or a supertype)
  OPTIONAL {
    ?districtKey rdfs:subClassOf* ?districtPriorityDefinedAt .
    ?d a :District_Challenge_Association ;
       :relates_district_type ?districtPriorityDefinedAt ;
       :relates_challenge     ?challenge ;
       :has_degree            ?districtPriority .
    OPTIONAL { ?d :defined_for_region ?rd }
    FILTER (!BOUND(?rd) || ?rd = ?region)
    # regional replaces general for the same pair
    FILTER (BOUND(?rd) || NOT EXISTS {
      ?d2 a :District_Challenge_Association ;
          :relates_district_type ?districtPriorityDefinedAt ;
          :relates_challenge     ?challenge ;
          :defined_for_region    ?region .
    })
    # a more specific district type replaces an inherited one
    FILTER NOT EXISTS {
      ?d3 a :District_Challenge_Association ;
          :relates_district_type ?closerDistrict ;
          :relates_challenge     ?challenge .
      ?districtKey rdfs:subClassOf* ?closerDistrict .
      ?closerDistrict rdfs:subClassOf+ ?districtPriorityDefinedAt .
      OPTIONAL { ?d3 :defined_for_region ?rd3 }
      FILTER (!BOUND(?rd3) || ?rd3 = ?region)
    }
    BIND (IF(BOUND(?rd), ?rd, "all regions") AS ?districtPriorityDefinedFor)
  }

  # 4. Priority of the challenge for the owner type (or a supertype)
  OPTIONAL {
    ?ownerKey rdfs:subClassOf* ?ownerPriorityDefinedAt .
    ?o a :Owner_Challenge_Association ;
       :relates_owner_type ?ownerPriorityDefinedAt ;
       :relates_challenge  ?challenge ;
       :has_degree         ?ownerPriority .
    OPTIONAL { ?o :defined_for_region ?ro }
    FILTER (!BOUND(?ro) || ?ro = ?region)
    # regional replaces general for the same pair
    FILTER (BOUND(?ro) || NOT EXISTS {
      ?o2 a :Owner_Challenge_Association ;
          :relates_owner_type ?ownerPriorityDefinedAt ;
          :relates_challenge  ?challenge ;
          :defined_for_region ?region .
    })
    # a more specific owner type replaces an inherited one
    FILTER NOT EXISTS {
      ?o3 a :Owner_Challenge_Association ;
          :relates_owner_type ?closerOwner ;
          :relates_challenge  ?challenge .
      ?ownerKey rdfs:subClassOf* ?closerOwner .
      ?closerOwner rdfs:subClassOf+ ?ownerPriorityDefinedAt .
      OPTIONAL { ?o3 :defined_for_region ?ro3 }
      FILTER (!BOUND(?ro3) || ?ro3 = ?region)
    }
    BIND (IF(BOUND(?ro), ?ro, "all regions") AS ?ownerPriorityDefinedFor)
  }
}
ORDER BY DESC(?contribution) ?challenge
```

| Column | Meaning |
|---|---|
| `rooftopType` | Activation type of the rooftop |
| `challenge` | Urban challenge the rooftop type contributes to addressing |
| `contribution` | Degree of the rooftop-challenge association (as in Query 1) |
| `districtType` | Type of the rooftop's district (empty if no district is found) |
| `districtPriority` | Priority of the challenge for that district type (empty if none is registered) |
| `districtPriorityDefinedAt` | District type at which the priority was registered (the district type itself or one of its superclasses) |
| `districtPriorityDefinedFor` | Region of the district priority, or "all regions" |
| `ownerType` | Type of the building's owner (empty if no owner is registered) |
| `ownerPriority` | Priority of the challenge for that owner type (empty if none is registered) |
| `ownerPriorityDefinedAt` | Owner type at which the priority was registered (the owner type itself or one of its superclasses) |
| `ownerPriorityDefinedFor` | Region of the owner priority, or "all regions" |

The query does not combine the three degrees into a single score. How to combine them (for example a product or a weighted mean) is a decision of the user.

Challenges that are a priority for the district or the owner but that the rooftop's activation type does not address are not returned.

#### Example

With the rooftop-challenge associations of the Query 1 example, a blue rooftop in Brussels whose building is in `ex:district_07` (a `Historical` district) and is owned by a `Real_Estate_Corporate` owner, and these registered priorities:

| Priority association | Region | Degree |
|---|---|---|
| `City_Center` - `Flood_risk` | all regions | 0.5 |
| `Historical` - `Flood_risk` | Brussels | 0.8 |
| `Residential` - `Drought_resistance` | all regions | 0.7 |
| `Real_Estate` - `Drought_resistance` | all regions | 0.4 |
| `Real_Estate_Corporate` - `Flood_risk` | all regions | 0.6 |

Query 4 returns:

| challenge | contribution | districtPriority | districtPriorityDefinedAt | ownerPriority | ownerPriorityDefinedAt |
|---|---|---|---|---|---|
| Flood_risk | 0.9 | 0.8 | Historical | 0.6 | Real_Estate_Corporate |
| Drought_resistance | 0.6 | | | 0.4 | Real_Estate |

For `Flood_risk`, the Brussels priority registered for `Historical` replaces the value inherited from `City_Center` (rule 9). For `Drought_resistance`, the district priority registered for `Residential` does not apply to a historical city centre, and the owner priority is inherited from `Real_Estate`.
