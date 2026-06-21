const pet = document.getElementById("pet");
const pacman = document.getElementById("pacman");
const statusText = document.getElementById("statusText");
const toast = document.getElementById("toast");

const api = window.capturePet;

function setStatus(message, isError = false) {
  statusText.textContent = message;
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  pet.classList.remove("ok", "error", "eating");
  pet.classList.add(isError ? "error" : "ok");
  window.setTimeout(() => {
    pet.classList.remove("ok", "error");
    toast.classList.remove("show");
  }, 1100);
}

function guessTitleFromBody(text) {
  const firstUsefulLine = text
    .split("\n")
    .map((line) => line.trim())
    .find((line) => line && !/^(\d{1,2}:\d{2}|user:|ai:)/i.test(line));
  return firstUsefulLine ? firstUsefulLine.slice(0, 42) : "";
}

async function captureText(text) {
  const trimmed = text.trim();
  if (!trimmed) {
    setStatus("空内容", true);
    return;
  }

  const entry = {
    title: guessTitleFromBody(trimmed) || "Inbox Capture",
    source: "Capture Pet",
    type: "inbox",
    topicHint: "",
    body: trimmed
  };

  try {
    pet.classList.add("eating");
    const result = await api.saveEntry(entry);
    setStatus(result.skippedDuplicate ? "重复跳过" : "已吃掉", Boolean(result.skippedDuplicate));
  } catch (error) {
    setStatus(error.message || "保存失败。", true);
  } finally {
    window.setTimeout(() => pet.classList.remove("eating"), 420);
  }
}

async function captureClipboard() {
  if (!api) {
    setStatus("预览模式", true);
    return;
  }
  const text = await api.readClipboard();
  await captureText(text);
}

function extractDropText(event) {
  const transfer = event.dataTransfer;
  const filePaths = Array.from(transfer.files || [])
    .map((file) => file.path || file.name)
    .filter(Boolean);

  const uriList = transfer.getData("text/uri-list");
  const plainText = transfer.getData("text/plain");
  const htmlText = transfer.getData("text/html");

  const parts = [];
  if (uriList) parts.push(uriList);
  if (plainText && plainText !== uriList) parts.push(plainText);
  if (!plainText && htmlText) parts.push(htmlText.replace(/<[^>]*>/g, " "));
  if (filePaths.length) parts.push(["Dropped files:", ...filePaths].join("\n"));
  return parts.join("\n\n");
}

if (!api) {
  setStatus("浏览器预览", true);
} else {
  api.onToggleExpanded(() => captureClipboard());
}

pacman.addEventListener("click", captureClipboard);

pet.addEventListener("contextmenu", (event) => {
  event.preventDefault();
  api?.quit();
});

["dragenter", "dragover"].forEach((eventName) => {
  pet.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    pet.classList.add("hungry");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  pet.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    pet.classList.remove("hungry");
  });
});

pet.addEventListener("drop", (event) => captureText(extractDropText(event)));

document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "v") {
    captureClipboard();
  }
});
