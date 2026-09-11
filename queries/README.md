# Competency questions

Each competency question is stated in natural language and paired with a SPARQL
query that answers it against `../examples/example-instances.ttl`. This is the
cheapest evidence that the ontology covers its intended scope, and reviewers of
ontology catalogues look for it.

| ID | Competency question | Query |
|----|---------------------|-------|
| CQ01 | Which X are related to Y? | [cq01.rq](cq01.rq) |

Run them locally:

```bash
# with Apache Jena
arq --data ../ontology/myont.ttl --data ../examples/example-instances.ttl --query cq01.rq
```
