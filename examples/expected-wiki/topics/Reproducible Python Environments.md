# Reproducible Python Environments

## Topic Overview

This topic explains how to isolate Python dependencies while keeping setup
reproducible across machines.

## Current Judgment

Create disposable virtual environments locally and declare dependencies in
version-controlled project files.

## Stable Rules

- Do not commit environment directories.
- Keep setup commands repository-relative.
- Treat local paths and client context as non-reusable information.

## Exceptions and Verification

- Platform-specific activation commands should be checked against
  [[Official Python venv Documentation]].

## Related Pages

- [[Python venv]]
- [[Source-Aware Environment Setup]]

## Supporting Sources

- [[Official Python venv Documentation]]
- [[Fictional Meeting Note]]

