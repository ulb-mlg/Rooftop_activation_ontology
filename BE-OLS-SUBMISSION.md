# BE-OLS submission

The Built Environment Ontology Lookup Service is maintained by the EC3 Modelling
and Standards Committee at https://github.com/CyberbuildLab/BE-OLS and published
at https://cyberbuildlab.github.io/BE-OLS/. New ontologies are added by opening
an issue on that repository, either the automated Ontology Submission Issue
template or a free-form issue containing the fields below.

Keep this file updated so the submission is a copy and paste job.

## Submission fields

- **Title**: My Ontology
- **Prefix**: `myont`
- **URI**: https://w3id.org/myont
- **Reference**: DOI of the paper, or the URL of the documentation page if there is no paper
- **Link to AEC ontologies**: bot, beo, dot, ...
- **Link to Upper ontologies**: dcterms, foaf, vann, skos, prov, schema, qudt, unit
- **Link to other professional domain ontologies**: ...

## Checklist against the BE-OLS evaluation framework

The framework is described at
https://github.com/CyberbuildLab/BE-OLS/wiki/Evaluation-Framework. Each item
below is something you can actually satisfy before submitting.

### Connectivity

- [ ] Aligned with upper or cross-domain vocabularies, and the alignments are in
      the RDF file, not only in the paper
- [ ] Aligned with existing AECO ontologies
- [ ] Aligned with domain meta-schemas such as BOT, Brick, RealEstateCore,
      SAREF4BLDG, SSN or SOSA

### Accessibility

- [ ] A conceptual model of the classes and their relations is published, for
      example a diagram in the documentation page and the WebVOWL view
- [ ] Available in at least one machine-readable serialisation. The workflow
      publishes Turtle, RDF/XML, JSON-LD and N-Triples
- [ ] Resolvable at a persistent URI with content negotiation, see `w3id/`

### Documentation and reuse

- [ ] Human-readable documentation of classes and properties, which is what the
      WIDOCO page provides
- [ ] Machine-readable annotations, meaning `rdfs:comment` or
      `dcterms:description` on every term inside the serialisation
- [ ] Evidence of reuse or extension, such as citations, imports by other
      vocabularies, or datasets that use it

### Also worth doing

- [ ] Archive a versioned release on Zenodo to obtain a DOI
- [ ] Run OOPS! (https://oops.linkeddata.es/) and resolve critical pitfalls
- [ ] Run FOOPS! (https://foops.linkeddata.es/FAIR_validator.html) and record the
      FAIR score in the README
- [ ] Register on the Linked Open Vocabularies (https://lov.linkeddata.es/) too
