const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("capturePet", {
  readClipboard: () => ipcRenderer.invoke("clipboard:readText"),
  saveEntry: (entry) => ipcRenderer.invoke("entry:save", entry),
  getVaultRoot: () => ipcRenderer.invoke("app:getVaultRoot"),
  hideWindow: () => ipcRenderer.send("window:hide"),
  quit: () => ipcRenderer.send("window:quit"),
  onToggleExpanded: (callback) => {
    ipcRenderer.on("toggle-expanded", callback);
  }
});
