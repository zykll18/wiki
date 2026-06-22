# Capture Pet macOS App Design

## Goal

Package Capture Pet as a locally installable macOS application for project
demonstrations. The first release targets the current Apple Silicon Mac and is
not signed, notarized, or distributed through the App Store.

## User Experience

1. The user opens `Capture Pet.app`.
2. On first launch, the app asks the user to select an Obsidian vault.
3. The selected vault path is stored in Electron's local application settings.
4. The pet appears as a small always-on-top window.
5. The user copies an AI conversation and either clicks the pet or presses
   `Option + Space` to bring it forward.
6. Capture Pet writes the complete conversation into
   `raw/inbox/captures/` and adds it to `raw/inbox/pending.md`.
7. A short status message confirms that the capture was saved or skipped as a
   duplicate.

The app only captures source material. Codex remains responsible for reviewing
the pending queue, summarizing useful conversations, and writing maintained
knowledge into the Obsidian vault.

## Packaging

- Use `electron-builder` to generate an unpacked `.app` and a ZIP artifact.
- Build for `macOS arm64`.
- Use an explicit application identifier and product name.
- Disable code signing discovery for the local demonstration build.
- Exclude tests, development documents, and unrelated repository data from the
  application bundle.
- Keep generated artifacts under `capture-pet/dist/` and out of Git.

## Vault Configuration

Vault resolution follows this priority:

1. `LLM_WIKI_VAULT`, when explicitly supplied during development.
2. A previously selected vault stored in app settings.
3. A native directory picker shown at startup.

If the picker is cancelled and no valid vault exists, the app displays an error
and exits without writing files. The packaged application must never default to
writing inside its own application bundle.

## Boundaries

- All captured content remains local.
- This release does not automatically invoke Codex.
- This release does not install or configure Obsidian.
- This release does not include Apple Developer signing, notarization, auto
  updates, login-item startup, or a DMG installer.
- Gatekeeper may require the user to right-click the unsigned app and choose
  Open on first launch.

## Verification

- Existing storage unit tests continue to pass.
- Add tests for vault-setting persistence and resolution.
- Run JavaScript syntax checks.
- Build the Apple Silicon `.app`.
- Launch the packaged executable with a temporary vault.
- Capture fictional clipboard text.
- Confirm creation of a raw capture and pending-queue entry.
- Confirm no content is written inside the `.app` bundle.

