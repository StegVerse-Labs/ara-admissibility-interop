---
layout: default
title: Machine-Readable Publication Bridge
---

# Machine-Readable Publication Bridge

Machine-readable publication and commit-time admissibility solve adjacent problems.

Machine-readable publication asks:

> What content was published, where is it located, and how can software discover and cite it?

Commit-time admissibility asks:

> May this actor rely on this artifact for this specific action, target, scope, and moment?

The second question depends on the first. This repository therefore treats accessible publication metadata as an interoperability input, not as a competing publication model.

## Lifecycle

```text
Research content
    ↓
Machine-readable publication metadata
    ↓
Robot or agent discovery
    ↓
Artifact and evidence resolution
    ↓
Requested citation, publication, integration, or execution
    ↓
Commitment candidate
    ↓
Standing determination
    ↓
ALLOW | DENY | FAIL-CLOSED
```

## Minimal publication surface

A citation-friendly page can expose several complementary forms of metadata:

- human-readable citation text;
- BibTeX or another exportable citation representation;
- structured metadata such as JSON-LD;
- canonical artifact and evidence URLs;
- stable identifiers and versions;
- content digests where integrity verification matters;
- robot-accessible links to machine-readable manifests.

This repository does not prescribe one universal web-publication standard. It defines how resolved publication metadata can be transformed into a bounded request for reliance.

## Example HTML publication metadata

The following is illustrative rather than normative:

```html
<link rel="canonical" href="https://example.org/research/artifact-17">
<link rel="alternate"
      type="application/x-bibtex"
      href="https://example.org/research/artifact-17/citation.bib">
<link rel="describedby"
      type="application/json"
      href="https://example.org/research/artifact-17/artifact-manifest.json">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "identifier": "artifact-17",
  "name": "Example machine-readable research artifact",
  "url": "https://example.org/research/artifact-17",
  "version": "1.0.0"
}
</script>
```

## Conversion into a commitment candidate

Publication metadata becomes operationally relevant when an actor requests a concrete use. The transformation is:

| Published field | Commitment-candidate field |
| --- | --- |
| Stable identifier and canonical URL | `artifact_reference` |
| Citation or reliance operation | `requested_action` |
| Requesting human, agent, repository, or system | `actor` |
| Claim, paper, dataset, publication, or system affected | `target` |
| Permitted use and limitations | `scope` and `claim_boundary` |
| Linked logic, code, traces, reviews, and receipts | `evidence_references` |
| Current policy and delegation | `policy_reference` and `delegation_reference` |
| Time and operating environment | `execution_context` and `validity_window` |

A worked machine-readable example is available at [`../admissibility/examples/machine-readable-publication-citation-candidate.json`](../admissibility/examples/machine-readable-publication-citation-candidate.json).

## Important distinction

Discoverability does not itself establish truth, authority, current validity, or permission to rely on an artifact.

Likewise, admissibility evaluation cannot repair content that is inaccessible, unidentified, or impossible to resolve. A useful interoperability path therefore requires both:

1. publication metadata that machines can discover and interpret; and
2. a bounded standing decision for the proposed downstream use.

## Collaboration question

This prototype is intended to support an open design question:

> Does converting machine-readable publication metadata into an explicit, reviewable commitment candidate provide a useful downstream layer for agent-native research and automated citation systems?

The repository welcomes critique of the mapping, missing publication fields, overly restrictive assumptions, and cases where no standing decision should be required.