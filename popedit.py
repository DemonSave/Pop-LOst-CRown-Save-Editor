#!/usr/bin/env python3
"""
popedit.py - editor dei salvataggi di Prince of Persia: The Lost Crown.

Uso:
    python popedit.py info                  # riepilogo leggibile del salvataggio
    python popedit.py extract -o estratti   # JSON + screenshot leggibili
    python popedit.py pack -i estratti      # ricompatta i JSON modificati
    python popedit.py set crystals=99999 playtime=2:00:00 completion=50
    python popedit.py web                   # editor web locale
    python popedit.py backups               # elenco backup
    python popedit.py restore <nome>        # ripristina un backup

La cartella del salvataggio e' opzionale: se omessa viene usata l'ultima
salvata dal gioco (lastSavedFolder.txt).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import i18n
import popsave
from popsave import (SaveGame, backup_root, default_save_dir, find_save_dirs,
                     format_duration, get_path, has_save_files, list_backups,
                     parse_duration, remember_save_dir, resolve_save_dir,
                     restore_backup)

# Percorsi validi sia da sorgente sia dentro l'eseguibile PyInstaller:
# gli asset sono nel bundle temporaneo (_MEIPASS), mentre i file generati
# (estratti, ...) vanno accanto all'exe.
FROZEN = getattr(sys, "frozen", False)
BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
APP_DIR = Path(sys.executable).resolve().parent if FROZEN else BUNDLE_DIR
WEB_DIR = BUNDLE_DIR / "web"


# --------------------------------------------------------------------------
# Riepilogo
# --------------------------------------------------------------------------
def cmd_info(args):
    save = SaveGame(args.save)
    print()
    print(f"  Salvataggio: {save.dir}")
    print("  " + "-" * 58)
    for row in save.summary():
        print(f"  {row['label']:<26} {row['value']}")
    print("  " + "-" * 58)

    prog = save.prog or {}
    up = prog.get("m_playerUpgradeProgressionData", {})
    print("\n  POTENZIAMENTI (0 = base)")
    for key, label in (("m_healthUpgrades", "Vita"), ("m_swordUpgrades", "Spada"),
                       ("m_bowUpgrades", "Arco"), ("m_quiverUpgrades", "Faretra"),
                       ("m_potionNumberUpgrades", "Numero pozioni"),
                       ("m_potionEffectUpgrades", "Effetto pozioni")):
        print(f"    {label:<20} {up.get(key, '?')}")

    stones = prog.get("m_playerStoneOfKnowledgeProgressionData", {})
    unlocked = stones.get("m_unlockedStoneOfKnowledges", [])
    levels = stones.get("m_stoneLevels", [])
    print("\n  PIETRE DELLA CONOSCENZA")
    for i, name in enumerate(unlocked):
        lvl = levels[i] if i < len(levels) else "?"
        print(f"    {i + 1:>2}. {name:<22} livello {lvl}")

    abilities = prog.get("m_playerAbilitiesProgressionData", {}).get("m_unlockedAbilities", [])
    print("\n  ABILITA'")
    print("    " + ", ".join(abilities))

    print("\n  INVENTARIO (solo oggetti con quantita' > 0)")
    for i, it in enumerate(save.inventory):
        if it.get("m_itemAmount", 0):
            print(f"    {it.get('m_itemType', '?'):<42} {it.get('m_itemAmount')}")

    opts = save.obj("options") or {}
    print("\n  OPZIONI DI GIOCO (id numerici interni)")
    for group, kind in (("m_gameOptionsTypeInt", "Int"), ("m_gameOptionsTypeFloat", "Float")):
        for entry in opts.get(group, []):
            print(f"    {kind:<5} tipo {entry.get('m_eGameOptionType'):>3} = {entry.get('m_value')}")
    print()


# --------------------------------------------------------------------------
# Estrazione / ricompattamento
# --------------------------------------------------------------------------
def cmd_extract(args):
    save = SaveGame(args.save)
    out = Path(args.out) if args.out else APP_DIR / "estratti" / save.dir.name
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cont in save.containers.items():
        if cont.kind == "json":
            target = out / (name + ".json")
            target.write_text(json.dumps(cont.json(), indent=2, ensure_ascii=False), encoding="utf-8")
            written.append(target.name)
        elif cont.kind == "jpeg":
            target = out / (name + ".jpg")
            target.write_bytes(cont.data)
            written.append(target.name)
    print(f"Estratti {len(written)} file in {out}")
    for name in written:
        print("  " + name)
    print("\nModifica i .json e poi esegui:  python popedit.py pack -i", out)


def cmd_pack(args):
    save = SaveGame(args.save)
    src = Path(args.input)
    if not src.is_dir():
        sys.exit(f"Cartella non trovata: {src}")
    touched = {}
    for name, cont in save.containers.items():
        if cont.kind != "json":
            continue
        f = src / (name + ".json")
        if not f.is_file():
            continue
        obj = json.loads(f.read_text(encoding="utf-8"))
        saved = save.prog if name == save.progression_file else (
            save._save_json if name == save.save_file else
            save._opt_json if name == save.options_file else cont.json())
        if obj == saved:
            continue
        touched[name] = obj

    if not touched:
        print("Nessuna modifica da applicare.")
        return
    backup = popsave.make_backup(save.dir)
    print(f"Backup creato in: {backup}")
    for name, obj in touched.items():
        cont = save.containers[name]
        data = cont.rebuild(obj)
        tmp = cont.path.with_suffix(cont.path.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(cont.path)
        print(f"  riscritto {name} ({len(data)} byte)")
    print("Fatto. Avvia il gioco e carica il salvataggio.")


# --------------------------------------------------------------------------
# set: modifica rapida da riga di comando
# --------------------------------------------------------------------------
def build_set_changes(save: SaveGame, pairs: list[str]) -> list[dict]:
    changes = []
    for pair in pairs:
        if "=" not in pair:
            sys.exit(f"Argomento non valido: {pair} (usa chiave=valore)")
        key, raw = pair.split("=", 1)
        key = key.strip().lower()
        if key in ("crystals", "cristalli"):
            idx = save.item_index("Crystal")
            if idx is None:
                sys.exit("Cristalli non trovati nell'inventario.")
            changes.append({"doc": "save", "path": f"{save.inv_path}[{idx}].m_itemAmount",
                            "value": int(raw), "type": "int"})
        elif key in ("playtime", "tempo"):
            changes.append({"doc": "progression", "path": "m_duration",
                            "value": parse_duration(raw), "type": "int"})
        elif key in ("completion", "completamento"):
            val = float(raw.rstrip("%"))
            changes.append({"doc": "progression", "path": "m_completion",
                            "value": val / 100 if val > 1 else val, "type": "float"})
        elif key in ("hp", "vita"):
            hp_path = save.loc.get("health")
            if not hp_path:
                sys.exit("Dati vita non trovati.")
            changes.append({"doc": "save", "path": f"{hp_path}.m_CurrentHP", "value": int(raw), "type": "int"})
        elif key in UPGRADE_KEYS:
            changes.append({"doc": "save", "path": f"{save.prog_path}.m_playerUpgradeProgressionData.{UPGRADE_KEYS[key]}",
                            "value": int(raw), "type": "int"})
        elif key in ("stones", "pietre"):
            base = f"{save.prog_path}.m_playerStoneOfKnowledgeProgressionData.m_stoneLevels"
            levels = save.prog["m_playerStoneOfKnowledgeProgressionData"]["m_stoneLevels"]
            for i in range(len(levels)):
                changes.append({"doc": "save", "path": f"{base}[{i}]", "value": int(raw), "type": "int"})
        else:
            sys.exit(f"Chiave sconosciuta: {key}")
    return changes


UPGRADE_KEYS = {
    "health_upgrades": "m_healthUpgrades", "health": "m_healthUpgrades",
    "sword": "m_swordUpgrades", "spada": "m_swordUpgrades",
    "bow": "m_bowUpgrades", "arco": "m_bowUpgrades",
    "quiver": "m_quiverUpgrades", "faretra": "m_quiverUpgrades",
    "potion_count": "m_potionNumberUpgrades", "pozioni": "m_potionNumberUpgrades",
    "potion_effect": "m_potionEffectUpgrades",
}


def cmd_set(args):
    save = SaveGame(args.save)
    log, backup = save.apply_changes(build_set_changes(save, args.pairs))
    print(f"Backup: {backup}")
    for row in log:
        print("  " + row)
    print("Fatto. Avvia il gioco e carica il salvataggio.")


# --------------------------------------------------------------------------
# Stato per l'interfaccia web
# --------------------------------------------------------------------------
def field(doc, path, label, ftype, value, **extra):
    d = {"doc": doc, "path": path, "label": label, "type": ftype, "value": value}
    d.update(extra)
    return d


def duration_to_input(seconds: int) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}"


def save_label(path: Path) -> str:
    parent = path.parent.name
    if parent.startswith("SaveSlot"):
        prefix = f"Slot {parent[8:]} - "
    elif parent:
        prefix = f"{parent} - "
    else:
        prefix = ""
    try:
        when = time.strftime("%d/%m/%Y %H:%M", time.localtime(path.stat().st_mtime))
    except OSError:
        when = "data sconosciuta"
    return f"{prefix}{path.name} ({when})"


def save_choices(current: Path) -> dict:
    """Salvataggi trovati, per il selettore della cartella nell'interfaccia."""
    dirs = {str(p.resolve()).lower(): p for p in find_save_dirs() if has_save_files(p)}
    dirs.setdefault(str(Path(current).resolve()).lower(), Path(current))
    rows = []
    for p in dirs.values():
        try:
            modified = p.stat().st_mtime
        except OSError:
            modified = 0
        rows.append({"path": str(p), "label": save_label(p), "modified": modified,
                     "active": p.resolve() == Path(current).resolve()})
    rows.sort(key=lambda r: (r["modified"], r["path"]), reverse=True)
    return {
        "current": str(Path(current)),
        "found": rows,
        "save_root": str(Path(os.environ.get("USERPROFILE") or Path.home()) / "OneDrive" / "DOCUMENTI"
                         / "My Games" / "Prince Of Persia The Lost Crown"),
    }


def pick_save_folder(initial: Path, lang: str = "it") -> str | None:
    """Apre la finestra di Windows per scegliere una cartella (solo locale)."""
    target = Path(tempfile.gettempdir()) / f"popsave_pick_{os.getpid()}_{time.time_ns()}.txt"
    script = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "$d = New-Object System.Windows.Forms.FolderBrowserDialog;"
        f"$d.Description = {popsave_quote(i18n.tr(lang, 'picker.title'))};"
        "$d.ShowNewFolderButton = $false;"
        f"if (Test-Path {popsave_quote(str(initial))}) {{ $d.SelectedPath = {popsave_quote(str(initial))} }};"
        "if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { "
        f"[IO.File]::WriteAllText({popsave_quote(str(target))}, $d.SelectedPath, [Text.Encoding]::UTF8) }}"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-STA", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-Command", script],
            capture_output=True, timeout=300,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if target.is_file():
            chosen = target.read_text(encoding="utf-8-sig").strip()
            return chosen or None
    except (OSError, subprocess.SubprocessError):
        return None
    finally:
        try:
            target.unlink(missing_ok=True)
        except OSError:
            pass
    return None


def popsave_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def lang_file() -> Path:
    return backup_root().parent / "last_lang.txt"


def remembered_lang() -> str:
    try:
        return i18n.normalize(lang_file().read_text(encoding="utf-8", errors="ignore"))
    except OSError:
        return i18n.DEFAULT_LANG


def remember_lang(lang: str) -> None:
    try:
        lang_file().write_text(i18n.normalize(lang), encoding="utf-8")
    except OSError:
        pass


def build_state(save: SaveGame, lang: str = "it") -> dict:
    lang = i18n.normalize(lang)
    t = lambda key, **kw: i18n.tr(lang, key, **kw)  # noqa: E731
    sections = []
    prog = save.prog or {}
    base = save.prog_path
    loc = i18n.normalize(lang)

    # --- progressione -----------------------------------------------------
    if save.progression_file:
        p = save.obj("progression") or {}
        sections.append({
            "id": "progressione", "title": t("section.progression"),
            "icon": "trend",
            "fields": [
                field("progression", "m_duration", t("field.playtime"), "duration",
                      duration_to_input(p.get("m_duration", 0)),
                      help=t("field.playtime.help")),
                field("progression", "m_completion", t("field.completion"), "percent",
                      round(float(p.get("m_completion", 0)) * 100, 2),
                      help=t("field.completion.help")),
                field("progression", "m_gameCompleted", t("field.game_completed"), "bool",
                      bool(p.get("m_gameCompleted", False))),
                field("progression", "m_currentQuestGameStage", t("field.quest"), "int",
                      int(p.get("m_currentQuestGameStage", 0))),
            ],
        })

    # --- personaggio ------------------------------------------------------
    if save.save_file and base:
        hp_path = save.loc.get("health", "")
        up = prog.get("m_playerUpgradeProgressionData", {})
        stones = prog.get("m_playerStoneOfKnowledgeProgressionData", {})
        abilities = prog.get("m_playerAbilitiesProgressionData", {})
        focus = prog.get("m_playerFocusProgressionData", {})
        inv_index = save.item_index("Crystal")

        fields = []
        if hp_path:
            fields += [
                field("save", f"{hp_path}.m_CurrentHP", t("field.hp"), "int",
                      int(get_path(save.obj("save"), f"{hp_path}.m_CurrentHP")), min=1, max=9999,
                      help=t("field.hp.help")),
                field("save", f"{hp_path}.m_CurrentHPNoLifeStoneBonus", t("field.hp_nobonus"), "int",
                      int(get_path(save.obj("save"), f"{hp_path}.m_CurrentHPNoLifeStoneBonus")), min=1, max=9999),
                field("save", f"{hp_path}.m_CurrentLifeStoneBonusHp", t("field.hp_bonus"), "int",
                      int(get_path(save.obj("save"), f"{hp_path}.m_CurrentLifeStoneBonusHp")), min=0, max=9999),
            ]
        fields += [
            field("save", f"{base}.m_playerFocusProgressionData.m_ability1", t("field.focus1"), "str",
                  focus.get("m_ability1", "")),
            field("save", f"{base}.m_playerFocusProgressionData.m_ability2", t("field.focus2"), "str",
                  focus.get("m_ability2", "")),
            field("save", f"{base}.m_playerAbilitiesProgressionData.m_unlockedAbilities",
                  t("field.abilities"), "list", abilities.get("m_unlockedAbilities", []),
                  help=t("field.abilities.help")),
            field("save", f"{base}.m_playerStoneOfKnowledgeProgressionData.m_unlockedStoneOfKnowledges",
                  t("field.stones"), "list", stones.get("m_unlockedStoneOfKnowledges", [])),
            field("save", f"{base}.m_playerStoneOfKnowledgeProgressionData.m_equipedStonesOfKnowledges",
                  t("field.stones_equipped"), "list", stones.get("m_equipedStonesOfKnowledges", [])),
            field("save", f"{base}.m_playerStoneOfKnowledgeProgressionData.m_maxStoneAmount",
                  t("field.stone_slots"), "int", int(stones.get("m_maxStoneAmount", 0)), min=0, max=12),
        ]

        if inv_index is not None:
            fields.insert(0, field("save", f"{save.inv_path}[{inv_index}].m_itemAmount",
                                   t("field.crystals"), "int",
                                   int(save.inventory[inv_index].get("m_itemAmount", 0)),
                                   min=0, max=99999999,
                                   help=t("field.crystals.help")))
        sections.append({"id": "personaggio", "title": t("section.character"), "icon": "user",
                         "fields": fields})

        up_fields = []
        for key, label_key in (("m_healthUpgrades", "field.health"), ("m_swordUpgrades", "field.sword"),
                               ("m_bowUpgrades", "field.bow"), ("m_quiverUpgrades", "field.quiver"),
                               ("m_potionNumberUpgrades", "field.potions"),
                               ("m_potionEffectUpgrades", "field.potion_effect"),
                               ("m_healthUpgradesDLC1", "field.health_dlc")):
            if key in up:
                up_fields.append(field("save", f"{base}.m_playerUpgradeProgressionData.{key}",
                                       t(label_key), "int", int(up[key]), min=0, max=6,
                                       help=t("field.upgrade.help")))
        sections.append({"id": "potenziamenti", "title": t("section.upgrades"), "icon": "upgrade",
                         "fields": up_fields})

        levels = stones.get("m_stoneLevels", [])
        rows = []
        names = stones.get("m_unlockedStoneOfKnowledges", [])
        for i, lvl in enumerate(levels):
            rows.append({
                "name": names[i] if i < len(names) else t("field.stone", n=i + 1),
                "path": f"{base}.m_playerStoneOfKnowledgeProgressionData.m_stoneLevels[{i}]",
                "value": int(lvl),
            })
        if rows:
            sections.append({"id": "pietre", "title": t("section.stones"), "icon": "stone", "rows": rows})

    # --- inventario -------------------------------------------------------
    if save.inventory:
        rows = []
        for i, it in enumerate(save.inventory):
            rows.append({
                "name": it.get("m_itemType", "?"),
                "path": f"{save.inv_path}[{i}].m_itemAmount",
                "value": int(it.get("m_itemAmount", 0)),
            })
        sections.append({"id": "inventario", "title": t("section.inventory"), "icon": "bag", "rows": rows,
                         "searchable": True})

    # --- opzioni ----------------------------------------------------------
    if save.options_file:
        opts = save.obj("options") or {}
        rows = []
        for group in ("m_gameOptionsTypeInt", "m_gameOptionsTypeFloat"):
            for i, e in enumerate(opts.get(group, [])):
                kind = t("field.integer") if group.endswith("Int") else t("field.decimal")
                rows.append({
                    "name": t("field.option", n=e.get("m_eGameOptionType"), kind=kind),
                    "path": f"{group}[{i}].m_value",
                    "value": e.get("m_value"),
                    "type": "float" if group.endswith("Float") else "int",
                })
        sections.append({"id": "opzioni", "title": t("section.options"), "icon": "sliders", "rows": rows,
                         "searchable": True, "flat": True,
                         "note": t("options.note")})

    level = (save.obj("progression") or {}).get("m_level", "?")
    return {
        "lang": loc,
        "langs": i18n.lang_choices(),
        "ui": i18n.ui_strings(loc),
        "save_dir": str(save.dir),
        "saves": save_choices(save.dir),
        "fast_travel": save.fast_travel_state(),
        "challenges": save.challenge_state(loc),
        "map_stats": save.map_stats(),
        "header": {
            "title": f"{save.dir.parent.name} / {save.dir.name}",
            "subtitle": f"{t('summary.level')} {level} - {format_duration(save.playtime())} - "
                        f"{save.completion() * 100:.1f}%",
        },
        "summary": save.summary(loc),
        "sections": sections,
        "screenshots": [{"file": n, "label": n.replace("GameScreenshot", "Screenshot ")
                         .split("Slot")[0]} for n in save.screenshots],
        "docs": [{"key": "progression", "file": save.progression_file},
                 {"key": "save", "file": save.save_file},
                 {"key": "options", "file": save.options_file}],
        "backups": [{"name": b.name, "time": b.stat().st_mtime} for b in list_backups(save.dir)],
        "backup_root": str(backup_root()),
    }


# --------------------------------------------------------------------------
# Server web
# --------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    save: SaveGame = None  # impostato in cmd_web
    lang: str = i18n.DEFAULT_LANG

    def log_message(self, fmt, *args):
        if "--verbose" in sys.argv:
            super().log_message(fmt, *args)

    # -- util -------------------------------------------------------------
    def _send(self, code, body: bytes, ctype="application/json; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj).encode("utf-8"))

    def _read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 40 * 1024 * 1024:
            raise ValueError(i18n.tr(Handler.lang, "err.too_big"))
        return json.loads(self.rfile.read(n) or b"{}")

    # -- routing ----------------------------------------------------------
    def do_GET(self):
        url = urlparse(self.path)
        path = url.path
        if path == "/":
            self._serve_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
        elif path.startswith("/static/"):
            name = Path(path).name
            ctype = {"js": "text/javascript; charset=utf-8", "css": "text/css; charset=utf-8",
                     "svg": "image/svg+xml"}.get(name.rsplit(".", 1)[-1], "application/octet-stream")
            self._serve_file(WEB_DIR / name, ctype)
        elif path == "/api/state":
            try:
                self._json(200, build_state(self.save, Handler.lang))
            except Exception as exc:  # pragma: no cover
                self._json(500, {"error": str(exc)})
        elif path == "/api/raw":
            doc = parse_qs(url.query).get("doc", [""])[0]
            try:
                obj = self.save.obj(doc)
                if obj is None:
                    raise ValueError(i18n.tr(Handler.lang, "err.doc"))
                self._send(200, json.dumps(obj, ensure_ascii=False, indent=1).encode("utf-8"))
            except Exception as exc:
                self._json(400, {"error": str(exc)})
        elif path == "/api/screenshot":
            name = parse_qs(url.query).get("file", [""])[0]
            cont = self.save.containers.get(name)
            if not cont or cont.kind != "jpeg":
                self._json(404, {"error": i18n.tr(Handler.lang, "err.screenshot")})
                return
            self._send(200, cont.data, "image/jpeg")
        elif path == "/api/saves":
            self._json(200, save_choices(self.save.dir))
        elif path == "/api/backups":
            self._json(200, {"backups": [{"name": b.name} for b in list_backups(self.save.dir)],
                             "root": str(backup_root())})
        else:
            self._json(404, {"error": i18n.tr(Handler.lang, "err.notfound")})

    def _serve_file(self, path: Path, ctype):
        if not path.is_file():
            self._json(404, {"error": i18n.tr(Handler.lang, "err.file")})
            return
        self._send(200, path.read_bytes(), ctype)

    def do_POST(self):
        url = urlparse(self.path)
        try:
            data = self._read_json()
        except Exception as exc:
            self._json(400, {"error": i18n.tr(Handler.lang, "err.bad_request", msg=exc)})
            return

        try:
            if url.path == "/api/apply":
                changes = data.get("changes", [])
                cleaned = []
                for ch in changes:
                    cleaned.append({"doc": ch["doc"], "path": ch["path"],
                                    "value": coerce(ch["value"], ch.get("type", "raw"))})
                log, backup = self.save.apply_changes(cleaned)
                Handler.save = SaveGame(self.save.dir)  # stato fresco per le richieste seguenti
                self._json(200, {"ok": True, "log": log, "backup": str(backup),
                                 "state": build_state(Handler.save, Handler.lang)})
            elif url.path == "/api/raw":
                docs = data.get("docs", {})
                log, backup = self.save.apply_raw(docs, Handler.lang)
                Handler.save = SaveGame(self.save.dir)
                self._json(200, {"ok": True, "log": log, "backup": str(backup),
                                 "state": build_state(Handler.save, Handler.lang)})
            elif url.path == "/api/restore":
                name = data.get("backup", "")
                matches = [b for b in list_backups(self.save.dir) if b.name == name]
                if not matches:
                    raise ValueError(i18n.tr(Handler.lang, "err.backup"))
                restore_backup(self.save.dir, matches[0])
                Handler.save = SaveGame(self.save.dir)
                self._json(200, {"ok": True, "state": build_state(Handler.save, Handler.lang)})
            elif url.path == "/api/select-save":
                new_dir = resolve_save_dir(data.get("path", ""), Handler.lang)
                Handler.save = SaveGame(new_dir)
                remember_save_dir(new_dir)
                self._json(200, {"ok": True, "state": build_state(Handler.save, Handler.lang)})
            elif url.path == "/api/browse-save":
                chosen = pick_save_folder(self.save.dir, Handler.lang)
                self._json(200, {"path": chosen})
            elif url.path == "/api/lang":
                Handler.lang = i18n.normalize(str(data.get("lang", "")))
                remember_lang(Handler.lang)
                self._json(200, {"ok": True, "state": build_state(Handler.save, Handler.lang)})
            else:
                self._json(404, {"error": i18n.tr(Handler.lang, "err.notfound")})
        except Exception as exc:
            self._json(400, {"error": str(exc)})


def coerce(value, ftype: str):
    if ftype == "int":
        return int(str(value).strip())
    if ftype == "float":
        return float(str(value).replace(",", ".").strip())
    if ftype == "bool":
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("1", "true", "si", "sì", "yes", "on")
    if ftype == "percent":
        return float(str(value).replace(",", ".").replace("%", "").strip()) / 100.0
    if ftype == "duration":
        return parse_duration(str(value))
    if ftype == "list":
        if isinstance(value, list):
            items = value
        else:
            items = [x.strip() for x in str(value).replace("\n", ",").split(",")]
        return [x for x in items if x]
    if ftype == "str":
        return str(value)
    return value


def cmd_web(args):
    save = SaveGame(args.save)
    Handler.save = save
    Handler.lang = remembered_lang()
    port = args.port
    server = None
    for candidate in range(port, port + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), Handler)
            port = candidate
            break
        except OSError:
            continue
    if server is None:
        sys.exit(f"Nessuna porta libera tra {port} e {port + 19}")
    url = f"http://127.0.0.1:{port}/"
    print(f"Editor su {url}")
    print(f"Salvataggio: {save.dir}")
    print("Premi CTRL+C per fermare il server.")
    if not args.no_open:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nChiuso.")


# --------------------------------------------------------------------------
# Backup
# --------------------------------------------------------------------------
def cmd_saves(args):
    current = Path(args.save).resolve() if args.save else None
    found = find_save_dirs()
    print("\n  DOVE SONO I SALVATAGGI")
    print("  " + "-" * 58)
    print("  Documenti\\My Games\\Prince Of Persia The Lost Crown\\<profilo>\\Saves\\")
    print("  SaveSlot0..3\\Save_<numero>\\PopSaveGameSlotNIndex0.AlkSave")
    print("  Se OneDrive sincronizza Documenti, il percorso inizia con OneDrive\\DOCUMENTI.")
    print("  Puoi scegliere la cartella Save_*, il SaveSlotN o la cartella del profilo.\n")
    if current:
        print(f"  Cartella attuale: {current}\n")
    if not found:
        print("  Nessun salvataggio trovato nei percorsi Documenti.")
        print("  Avvia il gioco almeno una volta o indica la cartella con --save.")
        return
    print(f"  {len(found)} salvataggi trovati:")
    for p in found:
        mark = "*" if current and p.resolve() == current else " "
        print(f"   {mark} {p}")
    print("\n  Per usarne uno:  python popedit.py info --save \"percorso\"")


def cmd_backups(args):
    save = SaveGame(args.save)
    items = list_backups(save.dir)
    print(f"Cartella backup: {backup_root()}")
    if not items:
        print("Nessun backup.")
    for b in items:
        files = len(list(b.iterdir()))
        print(f"  {b.name}  ({files} file)")


def cmd_restore(args):
    save = SaveGame(args.save)
    items = list_backups(save.dir)
    if not items:
        sys.exit("Nessun backup disponibile.")
    if args.name:
        matches = [b for b in items if b.name == args.name]
        if not matches:
            sys.exit(f"Backup non trovato: {args.name}")
        target = matches[0]
    else:
        target = items[0]
    restore_backup(save.dir, target)
    print(f"Ripristinato {target.name} in {save.dir}")


# --------------------------------------------------------------------------
def main():
    save_help = "cartella Save_* (default: ultima salvata dal gioco)"
    parser = argparse.ArgumentParser(description="Editor salvataggi Prince of Persia: The Lost Crown")
    parser.add_argument("--save", help=save_help)
    sub = parser.add_subparsers(dest="cmd")

    def add(name, help_text):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--save", default=argparse.SUPPRESS, help=save_help)
        return p

    add("info", "riepilogo del salvataggio")

    p_ex = add("extract", "estrai JSON e screenshot")
    p_ex.add_argument("-o", "--out")

    p_pack = add("pack", "ricompatta i JSON modificati")
    p_pack.add_argument("-i", "--input", required=True)

    p_set = add("set", "modifica rapida (chiave=valore)")
    p_set.add_argument("pairs", nargs="+")

    p_web = add("web", "editor web locale")
    p_web.add_argument("--port", type=int, default=8765)
    p_web.add_argument("--no-open", action="store_true")

    add("saves", "elenca i salvataggi trovati e spiega dove sono")
    add("backups", "elenco backup")
    p_re = add("restore", "ripristina un backup")
    p_re.add_argument("name", nargs="?")

    args = parser.parse_args()
    if not args.save:
        found = default_save_dir()
        if not found:
            dirs = find_save_dirs()
            if dirs:
                found = dirs[-1]
        if not found:
            sys.exit("Cartella di salvataggio non trovata: indica il percorso con --save \"...\"")
        args.save = str(found)

    commands = {"info": cmd_info, "extract": cmd_extract, "pack": cmd_pack, "set": cmd_set,
                "web": cmd_web, "saves": cmd_saves,
                "backups": cmd_backups, "restore": cmd_restore}
    if not args.cmd:
        # Doppio clic sull'exe: apri direttamente l'editor nel browser.
        args.cmd = "web" if FROZEN else "info"
        if args.cmd == "web":
            args.port = 8765
            args.no_open = False
    commands[args.cmd](args)


if __name__ == "__main__":
    main()
