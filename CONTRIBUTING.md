# Contributing

## Reporting

Open an issue for a modelling error, a missing term or an unclear definition.
Include the affected term IRI and, where possible, a competency question that the
current model cannot answer.

## Proposing a change

1. Fork the repository and branch off `main`.
2. Edit the ontology in Protege and save as Turtle to `ontology/myont.ttl`.
   Do not reformat the whole file: a small diff is easier to review.
3. Give every new term an `rdfs:label` and an `rdfs:comment` in English.
4. Run a reasoner in Protege and confirm the ontology is consistent.
5. Add or update a competency question in `queries/` if the change adds
   expressivity.
6. Open a pull request describing the modelling rationale.

## Versioning

Semantic versioning applied to the vocabulary:

- **patch**: annotations, documentation, no change in meaning
- **minor**: new terms, backwards compatible
- **major**: removed or redefined terms

On release, update `owl:versionIRI` and `owl:versionInfo`, tag the commit
(`git tag v1.1.0`), and add an entry to `CHANGELOG.md`.

## Deprecation

Do not delete published terms. Mark them with `owl:deprecated true` and point to
the replacement with `dcterms:isReplacedBy`.
