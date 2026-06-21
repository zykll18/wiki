const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function slugify(value) {
  const normalized = String(value || "")
    .trim()
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[^\p{Letter}\p{Number}]+/gu, "-")
    .replace(/^-+|-+$/g, "");
  return normalized || "untitled";
}

function targetDirForType(type) {
  const mapping = {
    inbox: "raw/inbox/captures",
    conversation: "raw/conversations",
    paper: "raw/papers",
    video: "raw/videos",
    tweet: "raw/tweets",
    web: "raw/web"
  };
  return mapping[type] || mapping.inbox;
}

function datePart(date) {
  return date.toISOString().slice(0, 10);
}

function uniquePath(dirPath, basename) {
  let candidate = path.join(dirPath, `${basename}.md`);
  let index = 2;
  while (fs.existsSync(candidate)) {
    candidate = path.join(dirPath, `${basename}-${index}.md`);
    index += 1;
  }
  return candidate;
}

function createCaptureStore({ vaultRoot, now = () => new Date(), duplicateWindowMs = 30000 }) {
  if (!vaultRoot) throw new Error("vaultRoot is required.");
  const root = path.resolve(vaultRoot);
  let lastCapture = { digest: "", savedAt: 0, relativePath: "" };

  function appendPending(relativePath) {
    const pendingPath = path.join(root, "raw", "inbox", "pending.md");
    ensureDir(path.dirname(pendingPath));
    if (!fs.existsSync(pendingPath)) {
      fs.writeFileSync(pendingPath, "# Pending Inbox\n\n", "utf8");
    }
    const line = `- [ ] ${relativePath}\n`;
    const existing = fs.readFileSync(pendingPath, "utf8");
    if (!existing.includes(line)) fs.appendFileSync(pendingPath, line, "utf8");
    return pendingPath;
  }

  function saveEntry(entry = {}) {
    const body = String(entry.body || "").trim();
    if (!body) throw new Error("Capture body is empty.");

    const capturedAt = now();
    const normalized = {
      title: String(entry.title || "Inbox Capture").trim() || "Inbox Capture",
      source: String(entry.source || "Capture Pet"),
      type: String(entry.type || "inbox"),
      topicHint: String(entry.topicHint || ""),
      body
    };
    const bodyDigest = crypto.createHash("sha1").update(body).digest("hex");
    const capturedMs = capturedAt.getTime();
    if (lastCapture.digest === bodyDigest && capturedMs - lastCapture.savedAt < duplicateWindowMs) {
      return {
        relativePath: lastCapture.relativePath,
        pendingPath: path.join(root, "raw", "inbox", "pending.md"),
        skippedDuplicate: true
      };
    }

    const lines = [
      `Title: ${normalized.title}`,
      `Source: ${normalized.source}`,
      `Type: ${normalized.type}`
    ];
    if (normalized.topicHint) lines.push(`Topic Hint: ${normalized.topicHint}`);
    lines.push(`Captured: ${capturedAt.toISOString()}`, "", normalized.body);
    const content = `${lines.join("\n")}\n`;
    const digest = crypto.createHash("sha1").update(content).digest("hex").slice(0, 8);
    const targetDir = path.join(root, targetDirForType(normalized.type));
    ensureDir(targetDir);
    const targetPath = uniquePath(targetDir, `${datePart(capturedAt)}-capture-${digest}`);
    fs.writeFileSync(targetPath, content, "utf8");
    const relativePath = path.relative(root, targetPath).split(path.sep).join("/");
    const pendingPath = appendPending(relativePath);
    lastCapture = { digest: bodyDigest, savedAt: capturedMs, relativePath };
    return { path: targetPath, relativePath, pendingPath, skippedDuplicate: false };
  }

  return { saveEntry };
}

module.exports = { createCaptureStore, slugify, targetDirForType };
