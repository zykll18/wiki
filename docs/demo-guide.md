# Five-Minute Demo

This demo shows the actual first-version workflow: copy an AI conversation,
capture it locally, then ask Codex to organize it for Obsidian.

## 1. Verify the Repository

```bash
python3 scripts/validate_demo.py .
python3 scripts/vault_maintenance.py .
python3 scripts/privacy_scan.py .
python3 -m unittest discover -s tests -v
npm --prefix capture-pet test
```

## 2. Create an Isolated Demo Vault

```bash
rm -rf /tmp/ai-conversation-obsidian-demo
mkdir -p /tmp/ai-conversation-obsidian-demo
```

Use only fictional text during a public demonstration.

## 3. Start Capture Pet

```bash
npm --prefix capture-pet install
LLM_WIKI_VAULT="/tmp/ai-conversation-obsidian-demo" \
  npm --prefix capture-pet start
```

## 4. Copy a Fictional AI Conversation

Example:

```text
User: Why should a Python virtual environment not be committed to Git?

Assistant: A virtual environment contains machine-specific paths and installed
artifacts. Keep dependency declarations in version control and recreate the
environment when needed.
```

Click Capture Pet. Then inspect:

```bash
find /tmp/ai-conversation-obsidian-demo/raw/inbox -type f
cat /tmp/ai-conversation-obsidian-demo/raw/inbox/pending.md
```

The complete conversation should exist in `raw/inbox/captures/` and be listed
in the pending queue.

## 5. Ask Codex to Process It

Open the demo vault as a Codex project and send:

```text
Process the conversations in raw/inbox/pending.md.
Follow AGENTS.md. Preserve the raw source, create a source summary, update an
existing topic before creating a new one, and record the result in log.md.
```

Explain the boundary during the demo:

- Capture Pet captures.
- Codex understands and organizes.
- Obsidian presents the maintained knowledge.
- The original conversation remains available for traceability.

## 6. Show the Included Static Fixture

The repository also contains a deliberately authored public fixture:

1. `raw/public-sources/official-python-venv.md`
2. `wiki/summaries/Official Python venv Documentation.md`
3. `wiki/topics/Reproducible Python Environments.md`
4. `wiki/syntheses/Source-Aware Environment Setup.md`

This fixture demonstrates the same knowledge layers without publishing a real
private AI conversation.

![Capture Pet demo preview](images/capture-pet-demo.svg)

![Knowledge flow preview](images/demo-wiki.svg)

---

# 五分钟演示

1. 启动一个临时 Vault。
2. 运行 Capture Pet。
3. 复制一段虚构 AI 技术对话并点击 Pet。
4. 展示原文已经进入 `raw/inbox/captures/` 和 pending 队列。
5. 在 Codex 中要求它按照 `AGENTS.md` 处理 pending 对话。
6. 在 Obsidian 中展示 summary、topic 或 synthesis。

演示时应明确：Pet 只负责捕获，Codex 负责整理，Obsidian 负责长期阅读和维护。
