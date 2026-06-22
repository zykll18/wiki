# AI Conversation Positioning Design

## Goal

Reposition the public repository around one concrete problem: valuable
technical knowledge learned in AI conversations is difficult to remember and
expensive to organize manually in Obsidian.

## Product Story

The first supported workflow is:

1. Discuss a technical problem with an AI assistant.
2. Copy the valuable conversation.
3. Click Capture Pet to save the full conversation into the local raw inbox.
4. Ask Codex to process the pending conversation.
5. Codex summarizes, classifies, merges, and writes maintained knowledge into
   the user's Obsidian vault.
6. The original conversation remains available for traceability.

## Positioning

This repository is a Codex-driven local workflow for turning AI conversations
into maintained Obsidian knowledge. It is not currently an Obsidian plugin, a
standalone Codex Skill, or a fully automatic background service.

Codex is the first required supported agent runtime. Capture Pet handles local
capture only; it does not perform summarization. Obsidian is the interface for
reading and maintaining the resulting notes.

## Documentation Scope

- Rewrite the root README around the conversation-to-Obsidian problem and flow.
- Rewrite the architecture document around Capture Pet, raw inbox, Codex, and
  Obsidian.
- Rewrite the demo guide to demonstrate copying a fictional AI conversation,
  capturing it, and asking Codex to process the pending inbox.
- Update the Capture Pet README so its role and limitations are explicit.
- Keep existing general-purpose adapters in the repository, but stop presenting
  them as the product's primary purpose.

## Accuracy Boundaries

- Do not claim that clicking Capture Pet automatically invokes Codex.
- Do not claim that Capture Pet is already a signed or notarized macOS app.
- Do not claim that the included static Python `venv` fixture was generated from
  a real private AI conversation.
- State that processing is currently initiated by a user instruction to Codex.

