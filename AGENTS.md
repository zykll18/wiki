# Public Knowledge Governance

## Purpose

This repository demonstrates an LLM-maintained knowledge base. Raw evidence is
preserved; maintained knowledge is rewritten as evidence and judgment evolve.

## Layers

- `raw/`: immutable source material.
- `wiki/summaries/`: one-source ingestion decisions.
- `wiki/topics/`: reusable concepts and stable rules.
- `wiki/entities/`: tools, papers, products, and projects.
- `wiki/syntheses/`: current multi-source judgments.
- `index.md`: navigation.
- `log.md`: ingestion and maintenance history.

Default priority:

`synthesis > topic/entity > summary > raw`

## Required Ingestion Decision

Every summary must state:

- Primary topic
- Retention reason
- Excluded content
- Final storage layer
- Source reliability
- Verification boundary

Prefer updating an existing page over creating a parallel topic. Separate facts,
opinions, and unverified claims. Community signals can identify questions but
cannot establish facts without stronger evidence.

## Links and Writeback

Each summary links to at least one maintained page. Topics and syntheses link to
at least two related pages. After answering a query, explicitly choose no
writeback, topic/entity update, synthesis update, or conflict-register update.

## Public Data Boundary

Only deliberately authored public or fictional fixtures may enter this
repository. Real private conversations, journals, credentials, personal
identifiers, and machine-specific paths are forbidden.

