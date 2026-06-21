# Five-Minute Demo

## Verify

```bash
python3 scripts/validate_demo.py .
python3 scripts/vault_maintenance.py .
python3 scripts/privacy_scan.py .
python3 -m unittest discover -s tests -v
npm --prefix capture-pet test
```

## Follow the Knowledge Flow

1. Open `raw/public-sources/official-python-venv.md`.
2. Compare it with `wiki/summaries/Official Python venv Documentation.md`.
3. Open the fictional private note and confirm its summary excludes identity details.
4. Read the topic and entity pages.
5. Finish at `wiki/syntheses/Source-Aware Environment Setup.md`.
6. Inspect `Query and Writeback Workflow.md`.

## Try Capture Pet

```bash
cd capture-pet
npm install
LLM_WIKI_VAULT="/tmp/llm-wiki-public-demo" npm start
```

Capture fictional text and inspect `raw/inbox/captures/` and
`raw/inbox/pending.md`.

![Capture Pet demo preview](images/capture-pet-demo.svg)

![Demo knowledge flow](images/demo-wiki.svg)
