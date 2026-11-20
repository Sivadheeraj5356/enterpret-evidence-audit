# Feedback Evidence Audit

Independent proof of work for Enterpret's Machine Learning Intern opening. This is a small offline prototype for the evidence-integrity layer of a customer-feedback evaluation pipeline, not an Enterpret integration or a production-ready feature.

## Run

Python 3, standard library only:

```sh
python audit.py
python audit.py --test
```

The bundled synthetic examples produce one citation-check pass and two review findings: a cross-tenant reference and an invented quote. Ten tests cover valid citations, missing evidence, unknown IDs, tenant boundaries, invented and blank quotes, duplicate source IDs, repeated citations, empty inputs, and the semantic limitation below.

## Why this slice

Feedback summaries can look credible while citing a different tenant's ticket, an unknown source or a quote that does not exist. The checker checks exact quote containment and source identity, and leaves a per-claim review record that could sit beside a human or model-based rubric.

It uses only three synthetic records. No customer data, network calls, credentials or paid services are involved.

## Limits

A citation passing these checks does not prove the claim is true, entailed, representative, current or causally supported. The last test makes that explicit. Exact containment also rejects benign paraphrases and punctuation changes. Inputs are trusted, schema-conforming prototype data, not arbitrary hostile JSON. A production version would need schema validation, source permissions from the real authorization layer, freshness checks, human-labeled semantic evals and measured false-positive/negative rates.

This prototype is not endorsed by Enterpret and makes no measured product-quality claim.
