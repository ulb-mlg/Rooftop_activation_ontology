# Rooftop activation ontology

<!--
REPLACE EVERY PLACEHOLDER BELOW.
Placeholders use the pattern MYONT / myont / My Ontology / YOUR-USER / my-ontology.
-->

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://YOUR-USER.github.io/my-ontology/)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.XXXXXXX-blue)](https://doi.org/10.5281/zenodo.XXXXXXX)

One paragraph describing what the ontology models, for which domain, and which
problem it solves. Keep it factual and short. This text is also what you paste
into the `dcterms:description` annotation of the ontology.

| Item | Value |
|---|---|
| Ontology name | My Ontology |
| Prefix | `myont` |
| Namespace URI | `https://w3id.org/myont#` |
| Current version | 1.0.0 |
| Documentation | https://YOUR-USER.github.io/my-ontology/ |
| Serialisations | [Turtle](https://YOUR-USER.github.io/my-ontology/ontology.ttl), [RDF/XML](https://YOUR-USER.github.io/my-ontology/ontology.xml), [JSON-LD](https://YOUR-USER.github.io/my-ontology/ontology.jsonld), [N-Triples](https://YOUR-USER.github.io/my-ontology/ontology.nt) |
| Licence | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| Repository | https://github.com/YOUR-USER/my-ontology |

## Namespace and prefix

```turtle
@prefix myont: <https://w3id.org/myont#> .
```

## Repository structure

```
.
├── .github/workflows/publish-docs.yml   CI that builds the docs and deploys GitHub Pages
├── ontology/
│   ├── myont.ttl                        the ontology (add it here, exported from Protege)
│   └── metadata-template.ttl            annotations to paste into the ontology header
├── examples/                            example instance data
├── queries/                             competency questions as SPARQL
├── w3id/                                .htaccess to submit to w3id.org
├── scripts/build-docs.sh                local documentation build
├── CITATION.cff
├── CONTRIBUTING.md
├── BE-OLS-SUBMISSION.md                 pre-filled submission form for the BE-OLS catalogue
└── LICENSE
```

## Reusing the ontology

Import it directly:

```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .
<https://example.org/my-dataset> a owl:Ontology ;
    owl:imports <https://w3id.org/myont> .
```

Or download a serialisation from the documentation page.

## Building the documentation locally

```bash
./scripts/build-docs.sh
```

Requires Java 11 or newer. The script downloads WIDOCO and writes the site to
`site/`. See [DOCUMENTATION.md](DOCUMENTATION.md) for the full procedure.

## Related ontologies

List the ontologies you align to. The BE-OLS catalogue evaluates connectivity,
so make this explicit.

- Upper and cross-domain: `dcterms`, `foaf`, `vann`, `skos`, `prov`, `qudt`
- Built environment: `bot`, `beo`, `dot`, `brick`, `saref4bldg`, `ifcowl`
- Other domains: ...

## Citation

See [CITATION.cff](CITATION.cff).

## Licence

The ontology and this documentation are licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code in `scripts/`
is licensed under the MIT licence.

## Contact

Name, affiliation, ORCID, e-mail or GitHub issues link.
