# Privacy Model

## Assets

Private conversations, credentials, identifiers, local paths, and Git history.

## Threats

- Copying a private vault and deleting sensitive files too late
- Publishing identifiers in examples, screenshots, or commit metadata
- Committing environment files or application state

## Allowlist Migration

Public artifacts are created or copied individually from a reviewed allowlist.
Private raw trees and project journals are never imported.

## Scanner Coverage

The scanner detects common credentials, email addresses, macOS home paths, and
the forbidden private-journal directory.

## Scanner Limitations

Pattern matching cannot infer every sensitive context. Zero findings do not
replace manual review.

## Git-History Rule

Sensitive data must never enter a commit, even temporarily.

## Release Checklist

1. Run privacy and vault validators.
2. Inspect tracked files and commit metadata.
3. Review screenshots and image metadata.
4. Test from a clean clone.

