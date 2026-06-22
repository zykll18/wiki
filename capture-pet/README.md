# Capture Pet

Capture Pet is the local capture layer for the AI-conversation-to-Obsidian
workflow.

Copy a useful technical conversation, click the pet, and the complete text is
saved to:

```text
raw/inbox/captures/
raw/inbox/pending.md
```

Capture Pet does not call Codex or summarize the conversation. After capture,
ask Codex to process the pending inbox according to the repository's
`AGENTS.md`.

## Install and Run

```bash
npm install
LLM_WIKI_VAULT="/absolute/path/to/your/Obsidian/vault" npm start
```

The environment variable is required when the target Obsidian vault is outside
the parent repository.

Capture Pet currently runs as an Electron development application. It is not
yet a signed or notarized macOS release.

## Controls

- `Option/Alt + Space`: show and focus the window.
- Click the character: capture clipboard text.
- Drag text, links, or file paths onto it: capture dropped content.
- `Cmd/Ctrl + V`: capture clipboard text.
- Right-click: quit.

## After Capture

Tell Codex:

```text
Process raw/inbox/pending.md according to AGENTS.md.
Preserve the raw conversation, create a summary, update existing topics before
creating new ones, and record the result in log.md.
```

## Privacy

- All captured content is written locally.
- Capture Pet does not upload data.
- The complete source is preserved for traceability.
- Use fictional content for public screenshots and demos.

---

# Capture Pet 中文说明

Capture Pet 是“AI 对话沉淀到 Obsidian”工作流中的本地捕获入口。

复制一段有价值的技术对话并点击 Pet，完整原文会保存到：

```text
raw/inbox/captures/
raw/inbox/pending.md
```

Capture Pet 不会调用 Codex，也不会自行总结。捕获完成后，需要让 Codex 按照
仓库中的 `AGENTS.md` 处理 pending inbox。

## 安装与运行

```bash
npm install
LLM_WIKI_VAULT="/你的/Obsidian/Vault/绝对路径" npm start
```

当前 Capture Pet 是 Electron 开发版，还不是已签名、公证的 macOS 安装包。

## 操作

- `Option/Alt + Space`：显示并聚焦窗口。
- 点击角色：捕获剪贴板文本。
- 拖入文本、链接或文件路径：捕获拖入内容。
- `Cmd/Ctrl + V`：捕获剪贴板文本。
- 右键：退出。

## 捕获之后

告诉 Codex：

```text
按照 AGENTS.md 处理 raw/inbox/pending.md。
保留原始对话，生成 summary，优先更新已有 topic，并在 log.md 记录处理结果。
```

## 隐私

- 所有内容只写入本地。
- Capture Pet 不上传数据。
- 完整原文会保留，以便追溯。
- 公开截图和演示只能使用虚构内容。
