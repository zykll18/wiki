# Capture Pet

Capture Pet is a small Electron desktop inbox for the public knowledge-base
demo. It saves clipboard or dropped text into `raw/inbox/captures/` and adds the
new source to `raw/inbox/pending.md`.

## Install and Run

```bash
npm install
npm start
```

The parent repository is the default vault. To use another vault:

```bash
LLM_WIKI_VAULT="/path/to/vault" npm start
```

## Controls

- `Option/Alt + Space`: show and focus the window.
- Click the character: capture clipboard text.
- Drag text, links, or file paths onto it: capture dropped content.
- `Cmd/Ctrl + V`: capture clipboard text.
- Right-click: quit.

## Privacy

Capture Pet writes locally. It does not upload data. Use only demo data when
creating public screenshots, and run the repository privacy scanner before
committing.

---

# Capture Pet 中文说明

Capture Pet 是公开知识库演示中的 Electron 桌面收集入口。它把剪贴板或拖入
的文本保存到 `raw/inbox/captures/`，并追加到 `raw/inbox/pending.md`。

## 安装与运行

```bash
npm install
npm start
```

默认使用上级仓库作为 vault。指定其他目录：

```bash
LLM_WIKI_VAULT="/path/to/vault" npm start
```

## 操作

- `Option/Alt + Space`：显示并聚焦窗口。
- 点击角色：捕获剪贴板文本。
- 拖入文本、链接或文件路径：捕获拖入内容。
- `Cmd/Ctrl + V`：捕获剪贴板文本。
- 右键：退出。

## 隐私

Capture Pet 只写入本地，不上传数据。制作公开截图时只能使用演示数据，提交
前必须运行仓库隐私扫描器。
