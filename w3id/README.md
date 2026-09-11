# Persistent identifier

GitHub Pages serves static files only and ignores `.htaccess`, so it cannot
perform content negotiation. A machine asking for `text/turtle` will receive the
HTML page. w3id.org runs Apache and does honour `.htaccess`, which is why almost
every built environment ontology (BOT, BEO, DOT, SAREF4BLDG) publishes under
`https://w3id.org/...` and redirects to a static host behind it.

BE-OLS asks for a URI in the submission template and its accessibility axis
checks that the ontology resolves at a persistent URI, so this step matters for
the catalogue entry.

## Procedure

1. Fork https://github.com/perma-id/w3id.org
2. Create a directory named after your identifier, for example `myont/`.
3. Copy the `.htaccess` from this folder into it and replace the placeholders.
4. Open a pull request. Read `CONTRIBUTING.md` in that repository first: the
   maintainers require that the identifier is not already taken, that a real
   contact is given, and that the redirect target is stable.
5. Once merged, `https://w3id.org/myont` resolves. Make sure the ontology IRI
   inside the RDF file is exactly this URI.

## Verify

```bash
curl -sIL -H "Accept: text/turtle" https://w3id.org/myont | grep -i location
curl -sIL -H "Accept: text/html"   https://w3id.org/myont | grep -i location
```

## Alternative

If you prefer not to depend on w3id.org, PURL (https://purl.archive.org/) offers
a similar service. Do not use a bare `github.io` URL as the ontology IRI: it ties
the identifier to a hosting account you may lose control of.
