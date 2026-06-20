# Public Portfolio Repository Design

Date: 2026-06-20  
Status: Approved design, awaiting implementation-plan approval

## 1. Objective

Create a standalone, interview-ready public repository named
`llm-maintained-knowledge-base`.

The repository will demonstrate how an LLM can maintain a long-lived knowledge
base instead of merely archiving conversations. It must present a complete,
testable knowledge flow:

```text
raw source
  -> source summary
  -> topic or entity
  -> multi-source synthesis
  -> query and writeback
```

The public repository is a productized extraction of the private Obsidian
vault. It is not a sanitized clone of the private repository.

## 2. Audience and Presentation Goal

Primary audience:

- Software engineering interviewers
- AI application and agent engineering interviewers
- Developers evaluating knowledge-management architecture

The repository should communicate its value within five minutes:

1. What problem it solves
2. How the knowledge layers differ
3. How data moves through the system
4. How privacy and source reliability are handled
5. How the implementation is tested

The main README will be bilingual. English appears first, followed by a
complete Chinese version.

## 3. Repository Strategy

Use selective migration rather than copying and deleting.

Only reusable source code, tests, governance rules, and intentionally created
examples will enter the public repository. Private raw data, personal wiki
pages, historical journals, local application state, credentials, and
machine-specific paths will never be copied into it.

This strategy is preferred because deletion-based sanitization has an
unacceptable risk of leaving private content in Git history.

## 4. Proposed Structure

```text
llm-maintained-knowledge-base/
├── README.md
├── LICENSE
├── AGENTS.md
├── .gitignore
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── privacy-model.md
│   ├── demo-guide.md
│   ├── images/
│   └── superpowers/
│       ├── specs/
│       └── plans/
├── examples/
│   ├── raw/
│   │   ├── public-sources/
│   │   └── fictional-private-data/
│   └── expected-wiki/
├── wiki/
│   ├── summaries/
│   ├── topics/
│   ├── entities/
│   └── syntheses/
├── capture-pet/
├── scripts/
│   ├── import_chat_memo.py
│   ├── search_last30days.py
│   ├── search_agent_reach.py
│   └── vault_maintenance.py
├── tests/
└── requirements-dev.txt
```

The final layout may add small supporting files, but it must retain these
responsibility boundaries.

## 5. Public Demonstration Data

The demo combines two source categories.

### 5.1 Public-source case

Use a public paper, official documentation, or another clearly attributable
source. The example demonstrates:

- Source metadata
- A single-source summary
- A topic or entity update
- A synthesis that distinguishes evidence from interpretation

The selected source must allow redistribution of the included excerpt or use
only metadata and original paraphrasing.

### 5.2 Fictional private-data case

Use fabricated personal notes or conversations to demonstrate:

- Low-information raw material
- Privacy-sensitive content
- A decision to retain only raw, create only a summary, or reject promotion
- Explicit removal of identifiers before public storage

No fictional identity may be easily confused with a real person.

### 5.3 Example integrity

Every example must declare:

- Primary topic
- Why the source is retained
- Which content is not promoted
- Final storage layer
- Source reliability
- Verification boundary

## 6. Core Components

### 6.1 Governance rules

`AGENTS.md` defines:

- Layer responsibilities
- Ingestion decisions
- Source reliability
- Fact, opinion, and unverified-claim separation
- Conflict handling
- Cross-link requirements
- Query writeback

The public version should preserve the rigor of the private rules while
removing references to personal pages and local workflows.

### 6.2 Maintenance scripts

Python scripts remain standard-library-first where practical.

They demonstrate:

- Chat export ingestion and deduplication
- Pending-source detection
- Broken-link and missing-source checks
- Weak-link and orphan detection
- Rewrite and merge candidates
- External search-result normalization

Machine-specific paths must be replaced with arguments, configuration, or
portable defaults.

### 6.3 Capture Pet

The Electron application remains a complete source component.

Its public role is to show the capture edge of the system:

```text
desktop capture -> raw inbox -> pending queue -> semantic ingestion
```

It must not include:

- Personal icons or identifying assets without redistribution permission
- Absolute paths
- Existing captured content
- Secrets or local account configuration

The application README must explain installation, launch, storage location,
and its relationship to the knowledge pipeline.

### 6.4 Documentation

Documentation includes:

- Bilingual project README
- Architecture and data-flow explanation
- Privacy threat model
- Reproducible demonstration guide
- Screenshots of Capture Pet and representative wiki pages
- Testing and verification instructions

Architecture diagrams should use Mermaid where possible so they remain
reviewable and version-controlled.

## 7. Privacy and Security Model

The public repository must use an allowlist migration model.

Allowed:

- Reviewed source files
- Reviewed tests
- Rewritten governance rules
- Deliberately created demo data
- Generated screenshots containing demo data only

Forbidden:

- The private `raw/` tree
- Project Journal history
- Personal wiki pages
- Names, emails, application numbers, account identifiers, or private URLs
- API keys, cookies, tokens, passwords, SSH details, and `.env` files
- Obsidian workspace state
- Absolute local paths

Required controls:

- Root `.gitignore`
- Secret-pattern scanner
- Personal-data scanner for known identifiers and local paths
- Pre-commit or test command that runs the scanners
- Final full-repository scan before the first public push

The public repository must be created from new files so private content never
enters Git history, even temporarily.

## 8. README Design

The English section appears first. The Chinese section provides equivalent
content rather than a short summary.

Both sections cover:

- Problem statement
- Key idea
- Architecture
- Features
- Demonstration walkthrough
- Capture Pet
- Setup
- Test commands
- Privacy model
- Current limitations
- Roadmap

The first screen should show:

- Repository name
- One-sentence value proposition
- Architecture diagram
- Verification status
- A link to the five-minute demo

Avoid unsupported performance claims. Use measured test counts and explicitly
described capabilities.

## 9. Error Handling and Portability

Scripts must:

- Fail with actionable error messages
- Avoid silently modifying source material
- Treat missing optional external tools as a reported capability gap
- Use repository-relative paths by default
- Avoid assuming macOS except where Capture Pet startup helpers are explicitly
  documented as platform-specific

External integrations such as Agent-Reach and last30days must remain optional.
Core demonstration and tests must run without network access or external
credentials.

## 10. Testing Strategy

Required automated coverage:

- Import and deduplication
- Same-source update behavior
- Pending raw detection
- Broken wiki links
- Missing raw references
- Orphan and weak-link detection
- Rewrite and merge candidate detection
- Demo fixture validity
- Secret and personal-data scanning
- Portable path behavior

Required manual verification:

- Run the five-minute demo from a clean checkout
- Launch Capture Pet
- Capture a fictional note
- Confirm pending queue insertion
- Process the demo through the expected wiki layers
- Render and inspect README screenshots

## 11. Implementation Phases

### Phase 1: Repository foundation

- Add repository metadata, license, ignore rules, and directory skeleton
- Add the bilingual README framework
- Add privacy scanners before migrating substantive content

### Phase 2: Selective source migration

- Migrate and normalize Python scripts
- Migrate tests
- Migrate Capture Pet
- Remove machine-specific assumptions

### Phase 3: Demonstration knowledge base

- Create public-source fixtures
- Create fictional privacy fixtures
- Create expected summaries, topics, entities, and syntheses
- Add the reproducible demo guide

### Phase 4: Portfolio presentation

- Add architecture and privacy documentation
- Generate demo-only screenshots
- Finish bilingual README
- Verify the five-minute reviewer path

### Phase 5: Release verification

- Run all tests
- Run secret and personal-data scans
- Inspect Git history
- Confirm no private-vault files were ever committed
- Prepare the repository for a new public GitHub remote

## 12. Acceptance Criteria

The repository is ready for public release only when:

- It contains no private raw conversations or Project Journal content
- It contains no credentials, personal identifiers, or absolute user paths
- The bilingual README explains the system in five minutes
- The complete example demonstrates every knowledge layer
- Capture Pet starts successfully from documented commands
- Core scripts work without network credentials
- All automated tests pass
- Privacy and secret scans return no findings
- Architecture and privacy documentation are complete
- The initial Git history contains only reviewed public artifacts

## 13. Out of Scope

The first public release will not include:

- A hosted web application
- Cloud synchronization
- User accounts or multi-user authorization
- Automatic publishing of the private vault
- Full compatibility with every AI chat export format
- Claims that community search results are verified facts

These can be evaluated after the interview-ready repository is complete.
