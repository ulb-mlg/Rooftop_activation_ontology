# Releasing a new version of the Rooftop Activation Ontology

This file lists the steps to follow every time the ontology file changes. It covers the version number, the metadata, the checks, the published files, the Git tag and the persistent identifier.

## 0. Where things are

| What | Where |
|---|---|
| Ontology source file (edited in Protégé) | `ontology/rooftop_activation_ontology.rdf` |
| Ontology IRI (never changes) | `https://w3id.org/rooftop_activation` |
| Version IRI | `https://w3id.org/rooftop_activation/X.Y.Z` |
| Files served for the ontology IRI | GitHub Pages: `ontology.ttl`, `ontology.owl` (RDF/XML), `ontology.jsonld`, `ontology.nt`, `index-en.html` |
| How GitHub Pages is built | Workflow `.github/workflows/publish-docs.yml`: WIDOCO generates the documentation and the four serialisations into `site/`, which is deployed. It runs on every push to `main` that changes `ontology/`, `docs/acknowledgements.html` or the workflow, and can be started by hand |
| Local preview | `scripts\build-docs_windows.cmd` (Docker Desktop must be running): same WIDOCO command, output in `site/` |
| File served for a version IRI | `ontology/rooftop_activation_ontology.rdf` in Git tag `vX.Y.Z` |
| Redirect rules | `rooftop_activation/.htaccess` in the perma-id/w3id.org repository (copy in `w3id/`) |

**Three rules follow from this set-up:**

1. **Every change to the published ontology file is a new version.** The file behind a version IRI must never change, so never edit the content of an existing tag and never move a tag.
2. **The file must keep its path.** Version IRIs point to `ontology/rooftop_activation_ontology.rdf` inside each tag, and the workflow reads it from there. If the file is moved or renamed, update the workflow, the local script and the `.htaccess` (step 11).
3. **Push ontology changes to `main` only when releasing.** Every push to `main` that touches `ontology/` republishes the documentation and the files served for the ontology IRI. Work on another branch (for example `develop`) and merge it into `main` in step 10.

Changes to documentation only (tutorials, README), which do not touch the ontology file, need no new version.

## 1. Choose the version number

Use semantic versioning, `MAJOR.MINOR.PATCH`:

| Change | Increase | Example |
|---|---|---|
| A term is removed or renamed, its meaning changes, or data valid in the previous version becomes invalid (new restriction, disjointness, range) | MAJOR | 2.1.0 to 3.0.0 |
| New classes, properties or individuals, or new axioms that do not invalidate existing data | MINOR | 2.1.0 to 2.2.0 |
| Corrections to labels, comments, typos or metadata only | PATCH | 2.1.0 to 2.1.1 |

## 2. Edit the ontology

Make the changes in Protégé on `ontology/rooftop_activation_ontology.rdf`, on a working branch (not `main`).

If a term is removed or renamed, do not delete it. Keep the old IRI and, in its **Annotations**, add:

- `owl:deprecated` with the value `true` (type `xsd:boolean`);
- `dcterms:isReplacedBy` with the IRI of the new term, if there is one.

To rename, use **Refactor > Rename entity**, then add a new entity with the old IRI carrying the annotations above.

## 3. Update the metadata

In Protégé, go to **Active ontology** tab > **Annotations** and update:

| Annotation | New value |
|---|---|
| `owl:versionIRI` | `https://w3id.org/rooftop_activation/X.Y.Z` (set in the **Ontology IRI / Version IRI** fields at the top of the tab) |
| `owl:versionInfo` | `X.Y.Z` as a literal, with no language tag |
| `owl:priorVersion` | `https://w3id.org/rooftop_activation/<previous version>` |
| `dcterms:modified` | Today's date, type `xsd:date` |
| `dcterms:issued` | The release date of this version, type `xsd:date` (check that the type is set: an untyped date is not read as a date) |
| `dcterms:bibliographicCitation` | The citation with the new version number |

Save the file.

## 4. Check the ontology

1. **Reasoner.** Run **Reasoner > HermiT > Start reasoner**. The ontology must be consistent, and `owl:Nothing` in the inferred class hierarchy must have no subclasses (no unsatisfiable classes).
2. **Metadata and statistics.** Run this script in the `ontology/` folder (requires `pip install rdflib`). Check that the version values are right, and note the totals for the change log.

   ```python
   from rdflib import Graph, URIRef
   from rdflib.namespace import OWL, RDF

   NS = "https://w3id.org/rooftop_activation#"
   g = Graph()
   g.parse("rooftop_activation_ontology.rdf", format="xml")
   local = lambda s: isinstance(s, URIRef) and str(s).startswith(NS)
   count = lambda t: len({s for s in g.subjects(RDF.type, t) if local(s)})
   classes = {s for s in g.subjects(RDF.type, OWL.Class) if local(s)}
   individuals = {s for s in g.subjects(RDF.type, OWL.NamedIndividual) if local(s) and s not in classes}

   print(f"Classes: {len(classes)}")
   print(f"Object properties: {count(OWL.ObjectProperty)}")
   print(f"Data properties: {count(OWL.DatatypeProperty)}")
   print(f"Named individuals: {len(individuals)}")
   o = URIRef(NS.rstrip("#"))
   for p in (OWL.versionIRI, OWL.versionInfo, OWL.priorVersion):
       print(p.split("#")[-1] + ":", g.value(o, p))
   ```

   The named individuals counted are those of the ontology namespace (rooftop functions, regions and urban challenges). The creator and publisher individuals are not counted.
3. **Optional.** Check the ontology with [FOOPS!](https://foops.linkeddata.es/) and [OOPS!](https://oops.linkeddata.es/), which report FAIR and modelling issues.
4. **Tutorials.** If the change affects terms used in the tutorials (building registration, incentive registration, association degrees), update their examples and queries.

## 5. Update the change log

Add an entry at the top of `CHANGELOG.md`:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
### Changed
### Deprecated
### Removed
### Fixed

In total: N classes, N object properties, N data properties and N named individuals.
```

Keep only the headings that apply, and use the totals from step 4.

## 6. Preview the documentation locally

Run the local script from the repository root, with Docker Desktop running:

```bat
scripts\build-docs_windows.cmd
```

Then preview the site:

```bat
python -m http.server 8000 --directory site
```

Open `http://localhost:8000` and check that the documentation shows the new version, metadata and terms, and that `site/` contains `ontology.ttl`, `ontology.owl`, `ontology.jsonld` and `ontology.nt`.

The `site/` folder is only a preview: GitHub Pages is built by the workflow (step 10), not from this folder. Do not commit it; add `site/` to `.gitignore`.

## 7. Documentation extras

If the acknowledgements changed, edit `docs/acknowledgements.html`. The workflow and the local script insert it into `index-en.html` after WIDOCO has run.

## 8. WIDOCO settings (only if needed)

The WIDOCO command is written twice: in `.github/workflows/publish-docs.yml` and in `scripts\build-docs_windows.cmd`. If you change an option or the WIDOCO version (`ghcr.io/dgarijo/widoco:v1.4.25`), change both, so that the preview matches the published site.

## 9. Update the repository README

In `README.md`, update the table: **Current version** and **Version IRI**.

## 10. Merge, publish and tag

1. Commit your changes on the working branch and merge it into `main`:

   ```bash
   git add ontology/ CHANGELOG.md README.md docs/
   git commit -m "Release X.Y.Z"
   git checkout main
   git merge <working branch>
   git push
   ```

2. The push starts the **Publish documentation** workflow. In the **Actions** tab of the repository, check that both jobs (`build` and `deploy`) succeed. If the workflow did not start (for example because only the README changed), run it by hand: **Actions > Publish documentation > Run workflow**.

3. Tag the release commit and push the tag:

   ```bash
   git tag -a vX.Y.Z -m "Rooftop Activation Ontology X.Y.Z"
   git push origin vX.Y.Z
   ```

   The tag name must be `v` followed by the version number (`v2.1.0`, not `2.1.0`): the w3id redirect builds the file URL from it.

Optionally, create a GitHub release from the tag (**Releases > Draft a new release**) with the change log entry. If the repository is connected to Zenodo, this also creates a DOI for the version.

## 11. Persistent identifier (w3id)

**Normally nothing to do.** The redirect rules work for any version: the ontology IRI always serves the current files on GitHub Pages, and `https://w3id.org/rooftop_activation/X.Y.Z` serves the file of tag `vX.Y.Z`.

**Update the w3id pull request only if:**

- the ontology file moves or is renamed in the repository;
- the GitHub Pages address or the names of the served files change (for example after a WIDOCO update that names the serialisations differently);
- a new serialisation format is added;
- the repository is renamed or moved to another account;
- the maintainer or contact details change.

In that case, update `w3id/.htaccess` and `w3id/README.md` in this repository, then copy them to `rooftop_activation/` in your fork of perma-id/w3id.org and open a pull request with a descriptive title, for example "rooftop_activation: update redirects".

## 12. Verify

After the workflow has finished, run:

```bash
curl -sIL -H "Accept: text/turtle"         https://w3id.org/rooftop_activation       | grep -i location
curl -sIL -H "Accept: application/rdf+xml" https://w3id.org/rooftop_activation       | grep -i location
curl -sIL -H "Accept: text/html"           https://w3id.org/rooftop_activation       | grep -i location
curl -sIL                                  https://w3id.org/rooftop_activation/X.Y.Z | grep -i location
curl -sIL                                  https://w3id.org/rooftop_activation/<previous version> | grep -i location
```

Each command should end at the expected file. Also open `https://w3id.org/rooftop_activation` in a browser and check that the documentation shows the new version.

## Checklist

- [ ] 1. Version number chosen
- [ ] 2. Ontology edited on a working branch; removed or renamed terms deprecated, not deleted
- [ ] 3. `owl:versionIRI`, `owl:versionInfo`, `owl:priorVersion`, `dcterms:modified`, `dcterms:issued`, `dcterms:bibliographicCitation` updated, dates typed `xsd:date`
- [ ] 4. Reasoner: consistent, no unsatisfiable classes; statistics noted; tutorials checked
- [ ] 5. `CHANGELOG.md` entry added
- [ ] 6. Documentation previewed locally with `build-docs_windows.cmd`
- [ ] 7. `docs/acknowledgements.html` updated, if needed
- [ ] 8. WIDOCO command identical in the workflow and the local script
- [ ] 9. Repository README updated
- [ ] 10. Merged into `main`, workflow succeeded, tag `vX.Y.Z` pushed
- [ ] 11. w3id updated, only if paths, names, hosting or contacts changed
- [ ] 12. Redirects verified
