const { app, BrowserWindow, clipboard, globalShortcut, ipcMain, screen } = require("electron");
const path = require("node:path");
const { createCaptureStore } = require("./lib/capture-store");

let mainWindow;

function createWindow() {
  const configuredVault = process.env.LLM_WIKI_VAULT;
  const defaultVault = path.resolve(__dirname, "..");
  const vaultRoot = configuredVault ? path.resolve(configuredVault) : defaultVault;
  const store = createCaptureStore({ vaultRoot });
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    width: 132,
    height: 132,
    x: width - 220,
    y: Math.max(80, Math.floor(height * 0.22)),
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  ipcMain.handle("clipboard:readText", () => clipboard.readText());
  ipcMain.handle("entry:save", (_event, entry) => store.saveEntry(entry));
  ipcMain.handle("app:getVaultRoot", () => vaultRoot);
  ipcMain.on("window:hide", () => mainWindow?.hide());
  ipcMain.on("window:quit", () => app.quit());

  mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  mainWindow.setAlwaysOnTop(true, "screen-saver");
  mainWindow.loadFile(path.join(__dirname, "renderer", "index.html"));
  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    mainWindow.focus();
    mainWindow.moveTop();
  });
}

app.whenReady().then(() => {
  createWindow();
  globalShortcut.register("Alt+Space", () => {
    if (!mainWindow) return;
    mainWindow.show();
    mainWindow.focus();
    mainWindow.moveTop();
  });
});

app.on("will-quit", () => globalShortcut.unregisterAll());
