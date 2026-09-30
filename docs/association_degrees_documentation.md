# Registering association degrees

This section explains how to record, in your own data, how strongly rooftop activation types, urban challenges, owner types and incentive types are associated, and how to query those associations for a given rooftop, including the actual owner of its building and the incentives implemented in its region.

## 1. What an association is

The ontology defines the types (rooftop colours, owner types, incentive types) and the urban challenges. How strongly they relate to each other depends on local context, so these links are registered by the users of the ontology, typically local authorities.

Each link is registered as an individual of one of three association classes. The individual carries the two linked elements and a degree.

| Association class | Links | Question it answers |
|---|---|---|
| `Rooftop_Challenge_Association` | rooftop type and urban challenge | How much does this rooftop type contribute to addressing this challenge? |
| `Owner_Rooftop_Association` | owner type and rooftop type | How likely is this owner type to activate this rooftop type? |
| `Incentive_Owner_Association` | incentive type and owner type | How suitable is this incentive type for this owner type? |

Together they form a chain. For a rooftop of a given type, you can retrieve the challenges it addresses, the owner types likely to activate it, and the incentives those owners can use:

```
urban challenge  <-  rooftop type  <-  owner type  <-  incentive type
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

## 2. Before you start

1. **Create your own data file.** Do not edit the ontology. Create a separate ontology for your data that imports `https://w3id.org/rooftop_activation`, and use your own namespace for everything you create (in the examples below, `ex:` stands for `https://example.org/my-region#`).
2. **Identify your region.** Use an existing `Region` individual of the ontology (for example `:Brussels`) or create your own individual of type `Region`.
3. **Describe your rooftops so the region can be found.** The queries find a rooftop's region through this path:

   `rooftop  is_part_of  building  is_located_in  district  is_part_of_region  region`

   A rooftop without this path is still queried, but only associations valid for all regions are returned.
4. **Give each rooftop its activation type.** Either assert the colour class directly (for example `ex:rooftop42 a :Blue_Rooftop`), or assert its functions with `has_function` and let a reasoner infer the colour. In the second case, see section 10 before querying.
5. **Register the owners of your buildings (optional).** Query 3 uses the actual owner of the building and the incentives implemented in your region. It needs owner individuals (section 8) and incentive individuals, registered as explained in the incentive registration tutorial.

## 3. Structure of an association

| Property | Rooftop_Challenge | Owner_Rooftop | Incentive_Owner | Value |
|---|---|---|---|---|
| `relates_rooftop_type` | required | required | | A rooftop colour class, e.g. `:Blue_Rooftop` |
| `relates_challenge` | required | | | An urban challenge individual, e.g. `:Flood_risk` |
| `relates_owner_type` | | required | required | An `Owner` subclass, e.g. `:Home_Owner_Associations` |
| `relates_incentive_type` | | | required | An `Incentive` instrument subclass, e.g. `:Grant` |
| `has_degree` | required | required | required | Decimal from 0 to 1 (`xsd:decimal`) |
| `defined_for_region` | optional | optional | optional | A `Region` individual. Omit it for an association valid in all regions |

Each property takes exactly one value per association.

**Why a class name is used as a value.** Rooftop colours, owner types and incentive types are classes. To be used as values of `relates_rooftop_type`, `relates_owner_type` and `relates_incentive_type`, each of these classes is also declared as an individual with the same IRI (OWL 2 punning). This is already done in the ontology for all rooftop colours, owner types and incentive instrument types.

**Valid values:**

- Rooftop types: the seven colour subclasses of `Rooftop` (`Blue_Rooftop`, `Gray_Rooftop`, `Green_Rooftop`, `Orange_Rooftop`, `Purple_Rooftop`, `Red_Rooftop`, `Yellow_Rooftop`).
- Urban challenges: the individuals of the `Urban_Challenge` subclasses.
- Owner types: any subclass of `Owner`.
- Incentive types: any instrument subclass of `Incentive`. Do not use the defined classes computed from facets (for example `Financial_Incentive` or `European_Incentive`).

**Provenance (recommended).** Add to each association:

- `dcterms:creator`: the authority that registered it;
- `dcterms:date`: the date it was registered or last reviewed;
- `rdfs:comment`: the source of the degree (study, survey, expert workshop, etc.).

## 4. Rules

1. **One association per pair and per region.** Do not register the same pair twice for the same region. To change a degree, edit the existing association.
2. **Regional values replace general values.** An association with `defined_for_region` replaces, for that region, an association of the same pair registered for all regions.
3. **Use a degree of 0 to cancel a general association locally.** If an association valid for all regions does not apply in your region, register the same pair for your region with degree 0. If there is simply no association, do not register anything.
4. **Register at the most general type that shares the same degree.** An owner or incentive association applies to all subclasses of the type. For example, an association with `:Grant` covers `:Pre-financed_Grant` and the other grant subclasses.
5. **A more specific owner type replaces an inherited value.** If `:Grant` is associated with `:Real_Estate` (degree 0.5) and also with `:Real_Estate_Corporate` (degree 0.9), the value 0.9 applies to `:Real_Estate_Corporate` and 0.5 to the other `Real_Estate` subclasses.
6. **A more specific incentive type replaces an inherited value.** If `:Grant` is associated with `:Home_Owner_Associations` (degree 0.5) and `:Pre-financed_Grant` also is (degree 0.9), the value 0.9 applies to pre-financed grants and 0.5 to the other grants. This matters when concrete incentives are matched to an owner (Query 3).

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

For many associations, prepare them in a spreadsheet (one row per association) and import them with the Cellfie plugin (**Tools > Create axioms from Excel workbook**), or convert the spreadsheet to Turtle with a script.

## 7. Adding new owner or incentive types

If you extend the ontology with a new subclass of `Owner` or `Incentive`, also declare an individual with exactly the same IRI. Otherwise the new type cannot be used in associations.

In Protégé: **Entities > Individuals > Add individual**, enter exactly the class name, and check that the IRI is identical to the class IRI. Do not add types or annotations to this individual; it shares the class annotations.

## 8. Registering building owners

Associations are registered between owner *types*. To find the incentives available to the actual owner of a building (Query 3), register the owner as an individual and link the building to it.

| Property | On | Required | Value |
|---|---|---|---|
| `rdf:type` | owner | required | **One** `Owner` subclass, the most specific that applies, e.g. `:Home_Owner_Associations`. The owner types are disjoint, so an owner cannot have two |
| `rdfs:label` | owner | recommended | A name or reference for the owner |
| `is_owned_by` | building | required | The owner individual |
| `has_owner_urban_challenge_priority` | owner | optional | The urban challenge individuals the owner prioritises, e.g. `:Flood_risk` |

Rules:

1. **One owner individual per party.** A party owning several buildings is one individual, linked from each building. Co-owners who decide together through an association (for example a homeowners' association) are one individual of that type.
2. **Never use an owner type as the owner.** `:Home_Owner_Associations` as value of `is_owned_by` would refer to the type, not to a party. Always create an individual.
3. **Protect personal data.** Owners of type `Private_Individual`, and sometimes `Landlords`, are natural persons. Use a pseudonymous identifier (for example `ex:owner_0042`) and a neutral label, and keep names and contact details outside the ontology.

In Turtle:

```turtle
ex:owner_0042 a owl:NamedIndividual , :Home_Owner_Associations ;
    rdfs:label "Homeowners' association 0042"@en ;
    :has_owner_urban_challenge_priority :Flood_risk .

ex:building_B0001 :is_owned_by ex:owner_0042 .
```

In Protégé:

1. Go to **Entities > Individuals**, click **Add individual** and enter the name, for example `owner_0042`.
2. In **Description > Types**, click **+** and select the owner type.
3. In **Annotations**, add an `rdfs:label`.
4. Select the building individual. In **Property assertions > Object property assertions**, click **+**, select `is_owned_by` and then the owner.
5. Save your data ontology.

If your buildings are generated from a CityJSON file, add the owners and the `is_owned_by` links in your hand-made file, not in the generated one, so that they survive a regeneration.

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
  {
    FILTER NOT EXISTS { ?association :has_degree ?d }
    BIND ("missing has_degree" AS ?problem)
  } UNION {
    ?association :has_degree ?d .
    FILTER (?d < 0 || ?d > 1)
    BIND ("degree outside 0-1" AS ?problem)
  } UNION {
    FILTER (?kind IN (:Rooftop_Challenge_Association, :Owner_Rooftop_Association))
    FILTER NOT EXISTS { ?association :relates_rooftop_type ?x }
    BIND ("missing relates_rooftop_type" AS ?problem)
  } UNION {
    FILTER (?kind = :Rooftop_Challenge_Association)
    FILTER NOT EXISTS { ?association :relates_challenge ?x }
    BIND ("missing relates_challenge" AS ?problem)
  } UNION {
    FILTER (?kind IN (:Owner_Rooftop_Association, :Incentive_Owner_Association))
    FILTER NOT EXISTS { ?association :relates_owner_type ?x }
    BIND ("missing relates_owner_type" AS ?problem)
  } UNION {
    FILTER (?kind = :Incentive_Owner_Association)
    FILTER NOT EXISTS { ?association :relates_incentive_type ?x }
    BIND ("missing relates_incentive_type" AS ?problem)
  }
}
ORDER BY ?association
```

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
  OPTIONAL { ?a :relates_incentive_type ?it }
  OPTIONAL { ?a :defined_for_region     ?r }
  BIND (CONCAT(COALESCE(STR(?rt), ""), " | ", COALESCE(STR(?ch), ""), " | ",
               COALESCE(STR(?ot), ""), " | ", COALESCE(STR(?it), "")) AS ?pair)
  BIND (COALESCE(STR(?r), "all regions") AS ?region)
}
GROUP BY ?kind ?pair ?region
HAVING (COUNT(?a) > 1)
```

## 10. Querying the associations of a rooftop

Run the queries on a dataset that contains **both the ontology and your data**, because they use the class hierarchy of the ontology (for owner and incentive type inheritance). For example, load both files into the same triplestore, or merge them.

If the activation type of your rooftops is inferred from `has_function` rather than asserted, or if the types of your owners or incentives are inferred, the inferred types must be available to the query. Either export the inferred axioms first (in Protégé: **File > Export inferred axioms as ontology**) or use a query engine with OWL reasoning.

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

For each incentive individual, the query looks for an association between its type (or a supertype) and the owner's type (or a supertype). Rules 2, 5 and 6 of section 4 apply: a regional value replaces a general one, and the association registered at the most specific owner type and incentive type is used.

It requires:

- the path `rooftop is_part_of building is_located_in district is_part_of_region region`;
- `is_owned_by` on the building, with an owner individual of an `Owner` subclass;
- incentive individuals with `implemented_in` your region (see the incentive registration tutorial).

```sparql
PREFIX :     <https://w3id.org/rooftop_activation#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ex:   <https://example.org/my-region#>

SELECT ?owner ?ownerType ?incentive ?incentiveLabel ?incentiveType ?degree ?degreeDefinedFor ?supportsRooftopType
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

  # 3. Association between the incentive's type (or a supertype) and the owner's type (or a supertype)
  ?incentiveClass rdfs:subClassOf* ?incentiveType .
  ?ownerType rdfs:subClassOf* ?ownerLevel .
  ?a a :Incentive_Owner_Association ;
     :relates_incentive_type ?incentiveType ;
     :relates_owner_type     ?ownerLevel ;
     :has_degree             ?degree .
  OPTIONAL { ?a :defined_for_region ?ra }
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
  BIND (IF(BOUND(?ra), ?ra, "all regions") AS ?degreeDefinedFor)

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
| `incentiveType` | Incentive type at which the matching association was registered (the incentive's type or one of its supertypes) |
| `degree` | Degree of the association |
| `degreeDefinedFor` | Region of the association, or "all regions" |
| `supportsRooftopType` | `yes` if the incentive states that it supports the rooftop's activation type (with `incentive_associated_to_rooftop`), `no` if it states other types only, `not stated` if it states none |

Incentives without a matching association are not returned. To see all incentives of the region, register an association for them, or remove step 3 of the query.

#### Example

With a green rooftop in Brussels, whose building is owned by `ex:owner_0042` (a `Home_Owner_Associations`), and these registered associations:

| Association | Region | Degree |
|---|---|---|
| `Grant` - `Home_Owner_Associations` | all regions | 0.5 |
| `Pre-financed_Grant` - `Home_Owner_Associations` | Brussels | 0.9 |
| `Advisory_Service` - `Owner` | all regions | 0.75 |
| `Tax_Credit` - `Home_Owner_Associations` | all regions | 0.25 |

and these incentive individuals:

| Incentive | Type | Region | Rooftop type stated |
|---|---|---|---|
| `inc_Brussels_green_roof_grant` | `Grant` | Brussels | `Green_Rooftop` |
| `inc_Brussels_prefinanced_water_grant` | `Pre-financed_Grant` | Brussels | `Blue_Rooftop` |
| `inc_Brussels_rooftop_advice` | `Advisory_Service` | Brussels | none |
| `inc_Rotterdam_rooftop_advice` | `Advisory_Service` | Rotterdam | none |

Query 3 returns:

| incentive | incentiveType | degree | degreeDefinedFor | supportsRooftopType |
|---|---|---|---|---|
| inc_Brussels_prefinanced_water_grant | Pre-financed_Grant | 0.9 | Brussels | no |
| inc_Brussels_rooftop_advice | Advisory_Service | 0.75 | all regions | not stated |
| inc_Brussels_green_roof_grant | Grant | 0.5 | all regions | yes |

The pre-financed grant uses the value registered for `Pre-financed_Grant`, which replaces the value inherited from `Grant` (rule 6). The advice desk inherits the association registered for all owners. The Rotterdam incentive is not in the rooftop's region, and no tax credit is implemented in Brussels, so neither appears.
