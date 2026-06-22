# Capture Pet macOS App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an unsigned Apple Silicon `Capture Pet.app` that remembers an Obsidian vault, captures copied AI conversations into its raw inbox, and can be launched by double-clicking.

**Architecture:** Keep filesystem persistence independent from Electron. A new settings module stores the selected vault in Electron's `userData` directory, while `main.js` resolves an environment override, a saved setting, or a native directory picker before creating the capture store. `electron-builder` packages only the runtime files into an unpacked `.app` and ZIP artifact.

**Tech Stack:** Electron, Node.js CommonJS, `node:test`, electron-builder, macOS arm64

---

## File Structure

- `capture-pet/lib/vault-settings.js`: validate, load, save, and resolve the configured vault path without importing Electron.
- `capture-pet/test/vault-settings.test.js`: unit tests for settings persistence and resolution priority.
- `capture-pet/main.js`: request the vault through Electron, create the capture store, and start the window safely.
- `capture-pet/package.json`: add packaging scripts and electron-builder metadata.
- `capture-pet/.gitignore`: exclude generated packaging artifacts.
- `capture-pet/README.md`: document first launch, unsigned-app opening, and build commands.
- `README.md`: describe Capture Pet as the capture layer in the Codex-to-Obsidian workflow.

### Task 1: Vault Settings Module

**Files:**
- Create: `capture-pet/lib/vault-settings.js`
- Create: `capture-pet/test/vault-settings.test.js`

- [ ] **Step 1: Write failing tests for vault resolution and persistence**

```js
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {
  loadSavedVault,
  saveVault,
  resolveVault
} = require("../lib/vault-settings");

function tempDirectory() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "capture-pet-settings-"));
}

test("environment override has priority over a saved vault", () => {
  const userDataPath = tempDirectory();
  const savedVault = tempDirectory();
  const environmentVault = tempDirectory();
  saveVault({ userDataPath, vaultRoot: savedVault });

  assert.equal(
    resolveVault({ environmentVault, userDataPath }),
    path.resolve(environmentVault)
  );
});

test("saved vault is used when no environment override exists", () => {
  const userDataPath = tempDirectory();
  const savedVault = tempDirectory();
  saveVault({ userDataPath, vaultRoot: savedVault });

  assert.equal(resolveVault({ userDataPath }), path.resolve(savedVault));
});

test("invalid or missing saved settings return null", () => {
  const userDataPath = tempDirectory();
  assert.equal(loadSavedVault({ userDataPath }), null);

  fs.writeFileSync(path.join(userDataPath, "settings.json"), "{broken");
  assert.equal(loadSavedVault({ userDataPath }), null);
});
```

- [ ] **Step 2: Run the new test and verify it fails**

Run:

```bash
node --test capture-pet/test/vault-settings.test.js
```

Expected: FAIL with `Cannot find module '../lib/vault-settings'`.

- [ ] **Step 3: Implement the settings module**

```js
const fs = require("node:fs");
const path = require("node:path");

const SETTINGS_FILE = "settings.json";

function settingsPath(userDataPath) {
  return path.join(userDataPath, SETTINGS_FILE);
}

function validDirectory(candidate) {
  if (!candidate || typeof candidate !== "string") return null;
  const resolved = path.resolve(candidate);
  try {
    return fs.statSync(resolved).isDirectory() ? resolved : null;
  } catch {
    return null;
  }
}

function loadSavedVault({ userDataPath }) {
  try {
    const settings = JSON.parse(
      fs.readFileSync(settingsPath(userDataPath), "utf8")
    );
    return validDirectory(settings.vaultRoot);
  } catch {
    return null;
  }
}

function saveVault({ userDataPath, vaultRoot }) {
  const resolved = validDirectory(vaultRoot);
  if (!resolved) throw new Error("Vault must be an existing directory.");
  fs.mkdirSync(userDataPath, { recursive: true });
  fs.writeFileSync(
    settingsPath(userDataPath),
    `${JSON.stringify({ vaultRoot: resolved }, null, 2)}\n`,
    "utf8"
  );
  return resolved;
}

function resolveVault({ environmentVault, userDataPath }) {
  return (
    validDirectory(environmentVault) ||
    loadSavedVault({ userDataPath }) ||
    null
  );
}

module.exports = {
  loadSavedVault,
  resolveVault,
  saveVault
};
```

- [ ] **Step 4: Run settings and storage tests**

Run:

```bash
node --test capture-pet/test/*.test.js
```

Expected: all tests pass.

- [ ] **Step 5: Commit the settings module**

```bash
git add capture-pet/lib/vault-settings.js capture-pet/test/vault-settings.test.js
git commit -m "feat: persist Capture Pet vault selection"
```

### Task 2: First-Launch Vault Picker

**Files:**
- Modify: `capture-pet/main.js`

- [ ] **Step 1: Refactor startup to resolve or request a vault**

Replace the eager repository-relative default with these imports and helpers:

```js
const {
  app,
  BrowserWindow,
  clipboard,
  dialog,
  globalShortcut,
  ipcMain,
  screen
} = require("electron");
const path = require("node:path");
const { createCaptureStore } = require("./lib/capture-store");
const { resolveVault, saveVault } = require("./lib/vault-settings");

function requestVaultRoot() {
  const userDataPath = app.getPath("userData");
  const configuredVault = resolveVault({
    environmentVault: process.env.LLM_WIKI_VAULT,
    userDataPath
  });
  if (configuredVault) return configuredVault;

  const selection = dialog.showOpenDialogSync({
    title: "Choose your Obsidian vault",
    buttonLabel: "Use This Vault",
    properties: ["openDirectory", "createDirectory"]
  });
  if (!selection?.[0]) return null;
  return saveVault({ userDataPath, vaultRoot: selection[0] });
}
```

Change `createWindow()` to accept `vaultRoot`:

```js
function createWindow(vaultRoot) {
  const store = createCaptureStore({ vaultRoot });
  // retain the existing BrowserWindow and IPC implementation
}
```

Change startup to stop cleanly when selection is cancelled:

```js
app.whenReady().then(() => {
  const vaultRoot = requestVaultRoot();
  if (!vaultRoot) {
    dialog.showErrorBox(
      "Capture Pet needs an Obsidian vault",
      "No folder was selected. Open Capture Pet again and choose your vault."
    );
    app.quit();
    return;
  }

  createWindow(vaultRoot);
  globalShortcut.register("Alt+Space", () => {
    if (!mainWindow) return;
    mainWindow.show();
    mainWindow.focus();
    mainWindow.moveTop();
  });
});
```

- [ ] **Step 2: Run syntax checks and tests**

Run:

```bash
npm --prefix capture-pet run check
npm --prefix capture-pet test
```

Expected: syntax checks exit 0 and all Node tests pass.

- [ ] **Step 3: Verify development startup with an explicit temporary vault**

Run:

```bash
rm -rf /tmp/capture-pet-dev-vault
mkdir -p /tmp/capture-pet-dev-vault
LLM_WIKI_VAULT=/tmp/capture-pet-dev-vault npm --prefix capture-pet start
```

Expected: the pet window appears without showing the vault picker.

- [ ] **Step 4: Commit Electron startup changes**

```bash
git add capture-pet/main.js
git commit -m "feat: choose Obsidian vault on first launch"
```

### Task 3: macOS Packaging Configuration

**Files:**
- Modify: `capture-pet/package.json`
- Modify: `capture-pet/package-lock.json`
- Modify: `capture-pet/.gitignore`

- [ ] **Step 1: Install electron-builder**

Run:

```bash
npm --prefix capture-pet install --save-dev electron-builder
```

Expected: `electron-builder` appears in `devDependencies` and the lockfile changes.

- [ ] **Step 2: Add build metadata and scripts**

Merge these fields into `capture-pet/package.json`:

```json
{
  "productName": "Capture Pet",
  "scripts": {
    "start": "electron .",
    "check": "node --check main.js && node --check preload.js && node --check lib/capture-store.js && node --check lib/vault-settings.js && node --check renderer/renderer.js",
    "test": "node --test test/*.test.js",
    "build:mac": "CSC_IDENTITY_AUTO_DISCOVERY=false electron-builder --mac dir zip --arm64"
  },
  "build": {
    "appId": "dev.zyk.capturepet",
    "productName": "Capture Pet",
    "asar": true,
    "directories": {
      "output": "dist"
    },
    "files": [
      "main.js",
      "preload.js",
      "lib/**/*",
      "renderer/**/*",
      "package.json"
    ],
    "mac": {
      "category": "public.app-category.productivity",
      "target": [
        {
          "target": "dir",
          "arch": ["arm64"]
        },
        {
          "target": "zip",
          "arch": ["arm64"]
        }
      ]
    }
  }
}
```

- [ ] **Step 3: Ignore generated artifacts**

Append to `capture-pet/.gitignore`:

```gitignore
dist/
```

- [ ] **Step 4: Run checks before packaging**

Run:

```bash
npm --prefix capture-pet run check
npm --prefix capture-pet test
```

Expected: all checks pass.

- [ ] **Step 5: Build the unsigned Apple Silicon application**

Run:

```bash
npm --prefix capture-pet run build:mac
```

Expected artifacts:

```text
capture-pet/dist/mac-arm64/Capture Pet.app
capture-pet/dist/Capture Pet-0.1.0-arm64-mac.zip
```

- [ ] **Step 6: Commit packaging configuration**

```bash
git add capture-pet/package.json capture-pet/package-lock.json capture-pet/.gitignore
git commit -m "build: package Capture Pet for macOS"
```

### Task 4: Packaged-App Verification

**Files:**
- No tracked files required.

- [ ] **Step 1: Prepare a clean temporary vault and clipboard**

Run:

```bash
rm -rf /tmp/capture-pet-packaged-vault
mkdir -p /tmp/capture-pet-packaged-vault
printf '%s' 'Fictional AI conversation about Python virtual environments.' | pbcopy
```

- [ ] **Step 2: Launch the packaged executable with the temporary vault**

Run:

```bash
LLM_WIKI_VAULT=/tmp/capture-pet-packaged-vault \
  "capture-pet/dist/mac-arm64/Capture Pet.app/Contents/MacOS/Capture Pet"
```

Expected: the packaged pet appears and remains responsive.

- [ ] **Step 3: Click the pet and inspect captured output**

After clicking the pet, run in another terminal:

```bash
find /tmp/capture-pet-packaged-vault/raw/inbox -type f -maxdepth 3 -print
cat /tmp/capture-pet-packaged-vault/raw/inbox/pending.md
```

Expected: one Markdown capture file exists and `pending.md` links to it.

- [ ] **Step 4: Confirm the application bundle was not modified**

Run:

```bash
find "capture-pet/dist/mac-arm64/Capture Pet.app" \
  -path '*/raw/inbox/*' -print
```

Expected: no output.

### Task 5: Documentation and Full Verification

**Files:**
- Modify: `capture-pet/README.md`
- Modify: `README.md`

- [ ] **Step 1: Document the installed-app workflow**

Add these points to `capture-pet/README.md`:

````markdown
## macOS App

Build the local Apple Silicon application:

```bash
npm install
npm run build:mac
```

Open `dist/mac-arm64/Capture Pet.app`. On first launch, choose your Obsidian
vault. Because this development build is unsigned, macOS may require
right-clicking the app and choosing **Open** the first time.

Copy an AI conversation, press `Option + Space`, and click the pet. The original
conversation is saved under `raw/inbox/captures/` and added to
`raw/inbox/pending.md`. Ask Codex to process the pending conversation into your
Obsidian knowledge pages.
````

- [ ] **Step 2: Clarify the system positioning in the root README**

Add this positioning near the beginning of both language sections:

```markdown
Capture Pet is the local capture layer, Codex is the required first supported
agent for summarization and writeback, and Obsidian is the maintained knowledge
interface. The current release focuses on preserving and organizing valuable AI
conversations rather than general web collection.
```

- [ ] **Step 3: Run the complete verification suite**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_demo.py .
python3 scripts/vault_maintenance.py .
python3 scripts/privacy_scan.py .
npm --prefix capture-pet run check
npm --prefix capture-pet test
test -d "capture-pet/dist/mac-arm64/Capture Pet.app"
test -f "capture-pet/dist/Capture Pet-0.1.0-arm64-mac.zip"
```

Expected:

- 47 Python tests pass.
- Demo validation reports 0 issues.
- Vault maintenance reports no lint issues.
- Privacy scan reports 0 findings.
- All Node tests and syntax checks pass.
- Both macOS artifacts exist.

- [ ] **Step 4: Commit documentation**

```bash
git add README.md capture-pet/README.md
git commit -m "docs: explain Capture Pet app workflow"
```
