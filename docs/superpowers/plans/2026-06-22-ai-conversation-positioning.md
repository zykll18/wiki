# AI Conversation Positioning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the public documentation explain a single AI-conversation-to-Obsidian workflow accurately and consistently.

**Architecture:** Documentation follows the actual runtime boundary: Capture Pet writes copied conversations to `raw/inbox`, Codex processes pending material according to `AGENTS.md`, and Obsidian displays the maintained Markdown knowledge. Existing validation and privacy tools remain supporting infrastructure.

**Tech Stack:** Markdown, Mermaid, Codex, Electron, Obsidian

---

### Task 1: Rewrite Product Positioning

**Files:**
- Modify: `README.md`

- [ ] Replace the generic AI-era information pitch with the AI conversation memory problem.
- [ ] Add the exact Capture Pet → raw → Codex → Obsidian workflow.
- [ ] Add current requirements, setup, daily usage, boundaries, validation, and privacy sections.
- [ ] Keep English and Chinese sections aligned.

### Task 2: Align Supporting Documentation

**Files:**
- Modify: `docs/architecture.md`
- Modify: `docs/demo-guide.md`
- Modify: `capture-pet/README.md`

- [ ] Update the architecture diagram and component responsibilities.
- [ ] Update the demo to start from a copied fictional AI conversation.
- [ ] Explain that the user must explicitly ask Codex to process the pending inbox.
- [ ] Explain that Capture Pet is currently run with Electron and is not a signed macOS release.

### Task 3: Verify Documentation

**Files:**
- No additional files.

- [ ] Run `python3 scripts/validate_demo.py .`.
- [ ] Run `python3 scripts/vault_maintenance.py .`.
- [ ] Run `python3 scripts/privacy_scan.py .`.
- [ ] Search documentation for obsolete primary positioning around community search.
- [ ] Run `git diff --check`.
- [ ] Commit the documentation update.

