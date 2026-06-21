const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const { createCaptureStore } = require("../lib/capture-store");

test("saves a capture and adds one pending entry", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "capture-pet-"));
  const store = createCaptureStore({
    vaultRoot: root,
    now: () => new Date("2026-06-20T10:00:00Z")
  });

  const result = store.saveEntry({ body: "A fictional note" });

  assert.match(result.relativePath, /^raw\/inbox\/captures\/2026-06-20-capture-/);
  const pending = fs.readFileSync(path.join(root, "raw", "inbox", "pending.md"), "utf8");
  assert.equal(pending.match(/raw\/inbox\/captures/g).length, 1);
});

test("skips the same body inside the duplicate window", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "capture-pet-"));
  let current = new Date("2026-06-20T10:00:00Z");
  const store = createCaptureStore({ vaultRoot: root, now: () => current });

  store.saveEntry({ body: "same note" });
  current = new Date("2026-06-20T10:00:10Z");
  const duplicate = store.saveEntry({ body: "same note" });

  assert.equal(duplicate.skippedDuplicate, true);
});

test("rejects an empty capture", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "capture-pet-"));
  const store = createCaptureStore({ vaultRoot: root });

  assert.throws(() => store.saveEntry({ body: "  " }), /empty/i);
});
