/* Editor salvataggi PoP: The Lost Crown */
let state = null;
const pending = new Map(); // key -> {doc, path, type, value}

const $ = (sel) => document.querySelector(sel);
let ui = {};

function t(key, params = {}) {
  let text = ui[key] !== undefined ? ui[key] : key;
  for (const [k, v] of Object.entries(params)) text = text.replaceAll(`{${k}}`, String(v));
  return text;
}

function applyStatic() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-html]").forEach((node) => {
    node.innerHTML = t(node.dataset.i18nHtml);
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPh);
  });
  document.querySelectorAll("[data-i18n-label]").forEach((node) => {
    node.setAttribute("aria-label", t(node.dataset.i18nLabel));
  });
  document.documentElement.lang = state?.lang || "it";
}

function fillLanguages() {
  const sel = $("#lang");
  sel.innerHTML = "";
  for (const l of state.langs || []) {
    const opt = el("option", { value: l.code, text: l.name, title: l.name });
    sel.append(opt);
    if (l.code === state.lang) opt.selected = true;
  }
}

async function changeLanguage(code) {
  try {
    const data = await api("/api/lang", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lang: code }),
    });
    pending.clear();
    state = data.state;
    ui = state.ui || {};
    localStorage.setItem("popsave.lang", state.lang);
    fillLanguages();
    applyStatic();
    renderAll();
    hideBanner();
  } catch (err) {
    banner(t("err.generic", { msg: err.message }), true);
  }
}
const el = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k === "html") node.innerHTML = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else if (v !== null && v !== undefined) node.setAttribute(k, v);
  }
  for (const c of children) {
    if (c === null || c === undefined) continue;
    node.append(c.nodeType ? c : document.createTextNode(c));
  }
  return node;
};

const keyOf = (f) => `${f.doc}|${f.path}`;

async function api(path, opts) {
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || t("err.http", { code: res.status }));
  return data;
}

function toast(msg, kind = "") {
  const t = $("#toast");
  t.textContent = msg;
  t.className = `toast ${kind}`;
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.add("hidden"), 3200);
}

function banner(msg, isError = false) {
  const b = $("#banner");
  b.textContent = msg;
  b.className = `banner ${isError ? "error" : ""}`;
}

function hideBanner() {
  $("#banner").className = "banner hidden";
}

/* ---------------------------------------------------------------- render */
function renderSavePicker() {
  const saves = state.saves || { found: [], current: state.save_dir };
  $("#save-path").textContent = saves.current || state.save_dir;
  const sel = $("#save-select");
  sel.innerHTML = "";
  const found = saves.found || [];
  if (!found.length) {
    sel.append(el("option", { value: "", text: t("savepick.none") }));
  }
  for (const row of found) {
    const opt = el("option", { value: row.path, text: row.label, title: row.path });
    sel.append(opt);
    if (row.active) opt.selected = true;
  }
  $("#save-open").disabled = found.length === 0;
}

async function selectSave(path) {
  try {
    const data = await api("/api/select-save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    pending.clear();
    state = data.state;
    renderAll();
    hideBanner();
    toast(t("toast.folder", { path: state.save_dir }), "ok");
  } catch (err) {
    banner(t("err.open_folder", { msg: err.message }), true);
  }
}

function renderSummary() {
  const host = $("#summary");
  host.innerHTML = "";
  for (const row of state.summary) {
    host.append(el("div", { class: "card" },
      el("div", { class: "label", text: row.label }),
      el("div", { class: "value", text: String(row.value) })));
  }
  $("#title").textContent = "Prince of Persia: The Lost Crown";
  $("#subtitle").textContent = state.header.subtitle;
  $("#save-path").textContent = state.save_dir;
}

const ACTION_ICONS = { map: "\u25C8", travel: "\u2726", challenge: "\u2694" };

function renderActions() {
  const host = $("#actions");
  host.innerHTML = "";
  for (const a of state.actions || []) {
    host.append(el("div", { class: `action-card${a.done ? " done" : ""}` },
      el("div", { class: "action-icon", text: ACTION_ICONS[a.icon] || "\u25C6" }),
      el("div", { class: "action-body" },
        el("div", { class: "action-title" },
          el("span", { text: a.title }),
          el("span", { class: a.done ? "pill ok" : "pill", text: a.done ? t("action.done") : t("action.todo") })),
        el("p", { class: "action-desc", text: a.desc }),
        el("button", {
          class: a.done ? "btn small ghost" : "btn small primary",
          text: a.done ? t("action.reapply") : t("action.apply"),
          onclick: () => runAction(a),
        }))));
  }
}

function statusPill(done, onText, offText) {
  return el("span", { class: done ? "pill ok" : "pill warn", text: done ? onText : offText });
}

function worldSection(title, count, headers, rows) {
  const tbody = el("tbody");
  for (const row of rows) {
    const tr = el("tr");
    for (const cell of row) {
      if (cell && cell.nodeType) tr.append(el("td", {}, cell));
      else tr.append(el("td", { text: String(cell) }));
    }
    tbody.append(tr);
  }
  const table = el("table", {},
    el("thead", {}, el("tr", {}, ...headers.map((h) => el("th", { text: h })))),
    tbody);
  return el("div", { class: "section" },
    el("div", { class: "section-head" }, el("h3", { text: title }), el("span", { text: count })),
    el("div", { class: "tablewrap" }, table));
}

function renderWorld() {
  const host = $("#world");
  host.innerHTML = "";
  const travel = state.fast_travel || [];
  const challenges = state.challenges || [];
  const map = state.map_stats || { maps: 0, layers: 0, cells: 0 };

  if (travel.length) {
    host.append(worldSection(
      t("world.travel"),
      t("world.travel.count", { done: travel.filter((r) => r.unlocked).length, total: travel.length }),
      [t("world.header.point"), t("world.header.region"), t("world.header.level"), t("world.header.status")],
      travel.map((r) => [
        el("span", { class: "type", text: r.name }),
        r.region,
        el("span", { class: "muted", text: r.level }),
        statusPill(r.unlocked, t("world.unlocked"), t("world.locked")),
      ])));
  }

  if (challenges.length) {
    host.append(worldSection(
      t("world.challenge"),
      t("world.challenge.count", { done: challenges.filter((r) => r.done).length, total: challenges.length }),
      [t("world.header.lesson"), t("world.header.code"), t("world.header.status")],
      challenges.map((r) => [
        el("span", { text: r.name }),
        el("span", { class: "muted", text: r.code }),
        statusPill(r.done, t("world.completed"),
          r.status === "Locked" ? t("world.challenge_locked") : r.status),
      ])));
  }

  if (map.maps) {
    host.append(el("p", { class: "hint",
      text: t("world.map", { maps: map.maps, layers: map.layers,
        cells: map.cells.toLocaleString(state.lang || "it") }) }));
  }
}

async function runAction(a) {
  if (!confirm(t("confirm.action", { title: a.title, desc: a.desc }))) return;
  try {
    const data = await api("/api/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: a.id }),
    });
    pending.clear();
    state = data.state;
    renderAll();
    hideBanner();
    toast(t("toast.done", { log: data.log.join(" | ") }), "ok");
  } catch (err) {
    banner(t("err.generic", { msg: err.message }), true);
  }
}

function inputFor(f) {
  const key = keyOf(f);
  const changed = pending.has(key);
  let input;

  if (f.type === "bool") {
    input = el("input", { type: "checkbox" });
    input.checked = changed ? pending.get(key).value : !!f.value;
  } else if (f.type === "list") {
    input = el("textarea", { class: "list-input", spellcheck: "false" });
    const v = changed ? pending.get(key).value : f.value;
    input.value = Array.isArray(v) ? v.join(", ") : v;
  } else {
    input = el("input", {
      type: "text",
      inputmode: f.type === "int" || f.type === "percent" ? "numeric" : "text",
    });
    const v = changed ? pending.get(key).value : f.value;
    input.value = v === null || v === undefined ? "" : String(v);
  }
  if (changed) input.classList.add("changed");

  const track = () => {
    const raw = f.type === "bool" ? input.checked : input.value;
    const original = f.type === "list"
      ? JSON.stringify(f.value)
      : String(f.value);
    const current = f.type === "list"
      ? JSON.stringify(raw.split(",").map((s) => s.trim()).filter(Boolean))
      : String(raw);
    if (f.type === "bool" ? input.checked === !!f.value : current === original) {
      pending.delete(key);
      input.classList.remove("changed");
    } else {
      pending.set(key, { doc: f.doc, path: f.path, type: f.type, value: raw });
      input.classList.add("changed");
    }
    updatePending();
  };
  input.addEventListener("input", track);
  input.addEventListener("change", track);
  if (f.type === "list") input.addEventListener("input", growLists);
  return input;
}

function renderSections() {
  const host = $("#sections");
  host.innerHTML = "";
  for (const sec of state.sections) {
    const body = el("div", { class: "section-body" });
    let count = "";

    if (sec.fields) {
      const grid = el("div", { class: "fields" });
      for (const f of sec.fields) {
        const wrap = el("div", { class: "field" },
          el("label", { text: f.label }),
          inputFor(f),
          f.help ? el("span", { class: "help", text: f.help }) : null);
        grid.append(wrap);
      }
      body.append(grid);
    }

    if (sec.rows) {
      count = t("rows", { n: sec.rows.length });
      let search = null;
      if (sec.searchable) {
        search = el("input", { type: "text", class: "search", placeholder: t("table.search") });
        body.append(search);
      }
      if (sec.note) body.append(el("p", { class: "note", text: sec.note }));
      const tbody = el("tbody");
      const table = el("table", {},
        el("thead", {}, el("tr", {},
          el("th", { text: sec.flat ? t("table.option") : t("table.item") }),
          el("th", { text: t("table.value"), style: "width:170px" }))),
        tbody);
      const renderRows = () => {
        tbody.innerHTML = "";
        const q = (search?.value || "").toLowerCase();
        for (const row of sec.rows) {
          if (q && !row.name.toLowerCase().includes(q)) continue;
          const f = { doc: "save", path: row.path, type: row.type || "int", value: row.value };
          if (sec.id === "opzioni") f.doc = "options";
          const input = inputFor(f);
          tbody.append(el("tr", {},
            el("td", { class: sec.flat ? "" : "type", text: row.name }),
            el("td", { class: "num" }, input)));
        }
      };
      renderRows();
      if (search) search.addEventListener("input", renderRows);
      body.append(el("div", { class: "tablewrap" }, table));
    }

    // le righe sono gestite fuori: nessuna azione extra
    host.append(el("div", { class: "section", id: `sec-${sec.id}` },
      el("div", { class: "section-head" },
        el("h3", { text: sec.title }),
        el("span", { text: count })),
      body));
  }
}

function renderShots() {
  const host = $("#shots");
  host.innerHTML = "";
  if (!state.screenshots.length) {
    host.append(el("p", { class: "hint", text: t("shots.none") }));
    return;
  }
  for (const s of state.screenshots) {
    host.append(el("div", { class: "shot" },
      el("img", { src: `/api/screenshot?file=${encodeURIComponent(s.file)}`, loading: "lazy", alt: s.label }),
      el("span", { text: s.label })));
  }
}

function renderDocs() {
  const sel = $("#raw-doc");
  sel.innerHTML = "";
  for (const d of state.docs) {
    if (!d.file) continue;
    sel.append(el("option", { value: d.key, text: `${d.file}` }));
  }
}

function renderBackups() {
  const host = $("#backups");
  host.innerHTML = "";
  $("#backup-root").textContent = `${t("summary.folder")}: ${state.backup_root}`;
  if (!state.backups.length) {
    host.append(el("p", { class: "hint", text: t("backup.none") }));
    return;
  }
  for (const b of state.backups) {
    host.append(el("div", { class: "backup-row" },
      el("code", { text: b.name }),
      el("button", {
        class: "btn small ghost", text: t("backup.restore"),
        onclick: () => restoreBackup(b.name),
      })));
  }
}

function renderAll() {
  applyStatic();
  renderSavePicker();
  renderSummary();
  renderActions();
  renderWorld();
  renderSections();
  renderShots();
  renderDocs();
  renderBackups();
  updatePending();
  requestAnimationFrame(growLists);
}

/* le textarea degli elenchi si espandono, anche quando il pannello era nascosto */
function growLists() {
  document.querySelectorAll("textarea.list-input").forEach((area) => {
    const visible = area.offsetParent !== null;
    area.style.height = "auto";
    area.style.height = `${(visible ? area.scrollHeight : 0) + 4}px`;
  });
}

/* --------------------------------------------------------------- pending */
function updatePending() {
  const n = pending.size;
  $("#apply").disabled = n === 0;
  $("#pending-label").innerHTML = n === 0
    ? t("footer.nochanges")
    : t(n === 1 ? "footer.changes_one" : "footer.changes_many", { n });
}

async function applyChanges() {
  if (!pending.size) return;
  const changes = [];
  for (const item of pending.values()) {
    changes.push({ doc: item.doc, path: item.path, type: item.type, value: item.value });
  }
  try {
    const data = await api("/api/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ changes }),
    });
    pending.clear();
    state = data.state;
    renderAll();
    hideBanner();
    toast(t("toast.saved", { n: changes.length, backup: data.backup }), "ok");
  } catch (err) {
    banner(t("err.generic", { msg: err.message }), true);
  }
}

async function restoreBackup(name) {
  if (!confirm(t("backup.confirm", { name }))) return;
  try {
    const data = await api("/api/restore", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ backup: name }),
    });
    pending.clear();
    state = data.state;
    renderAll();
    toast(t("toast.restored"), "ok");
  } catch (err) {
    banner(t("err.generic", { msg: err.message }), true);
  }
}

/* ------------------------------------------------------------------ init */
function switchTab(name) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
  document.querySelectorAll(".tabpane").forEach((p) => p.classList.toggle("active", p.id === `tab-${name}`));
  requestAnimationFrame(growLists);
}

document.querySelectorAll(".tab").forEach((t) => {
  t.addEventListener("click", () => switchTab(t.dataset.tab));
});

$("#save-open").addEventListener("click", () => {
  const path = $("#save-select").value;
  if (path) selectSave(path);
});

$("#save-browse").addEventListener("click", async () => {
  const btn = $("#save-browse");
  btn.disabled = true;
  banner(t("savepick.choose_dialog"));
  try {
    const picked = await api("/api/browse-save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    if (picked.path) await selectSave(picked.path);
    else hideBanner();
  } catch (err) {
    banner(t("err.selection", { msg: err.message }), true);
  } finally {
    btn.disabled = false;
  }
});

$("#saves-help").addEventListener("click", () => {
  $("#saves-helpbox").classList.toggle("hidden");
});

$("#lang").addEventListener("change", (event) => changeLanguage(event.target.value));

$("#apply").addEventListener("click", applyChanges);
$("#reset").addEventListener("click", () => {
  pending.clear();
  renderSections();
  updatePending();
});

$("#raw-load").addEventListener("click", async () => {
  const doc = $("#raw-doc").value;
  try {
    const res = await fetch(`/api/raw?doc=${encodeURIComponent(doc)}`);
    if (!res.ok) throw new Error((await res.json()).error);
    $("#raw-text").value = await res.text();
    toast(t("toast.json_loaded"));
  } catch (err) {
    banner(t("err.generic", { msg: err.message }), true);
  }
});

$("#raw-apply").addEventListener("click", async () => {
  const doc = $("#raw-doc").value;
  const text = $("#raw-text").value;
  try {
    JSON.parse(text);
  } catch (err) {
    banner(t("err.json_invalid", { msg: err.message }), true);
    return;
  }
  if (!confirm(t("raw.confirm"))) return;
  try {
    const data = await api("/api/raw", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ docs: { [doc]: text } }),
    });
    pending.clear();
    state = data.state;
    renderAll();
    toast(t("toast.rewritten"), "ok");
  } catch (err) {
    banner(t("err.generic", { msg: err.message }), true);
  }
});

(async function init() {
  try {
    state = await api("/api/state");
    const stored = localStorage.getItem("popsave.lang");
    if (stored && stored !== state.lang) {
      const data = await api("/api/lang", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lang: stored }),
      });
      state = data.state;
    }
    ui = state.ui || {};
    fillLanguages();
    applyStatic();
    renderAll();
    banner(t("banner.close"));
  } catch (err) {
    banner(t("err.read", { msg: err.message }), true);
  }
})();
