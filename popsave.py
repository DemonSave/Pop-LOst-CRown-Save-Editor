"""
popsave.py - Lettura e riscrittura dei salvataggi di
Prince of Persia: The Lost Crown (contenitori Ubisoft Anvil "Alk").

Formato (sintesi, dettagli in ANALISI_FORMATO.md):

    +0x000  4   magic "wv\\x19P"
    +0x004  ... header di 1074 byte (0x432), in gran parte zeri
    +0x41E  4   id del contenuto (NON un checksum: resta identico tra salvataggi)
    +0x422  8   dimensione del payload decompresso
    +0x42A  8   dimensione dello stream gzip
    +0x432  ... stream gzip (JSON)  oppure record + JPEG per gli screenshot

Payload JSON:
    u8  lunghezza nome, nome ASCII, u8 versione (1), u32 lunghezza JSON, JSON UTF-8

I file sono quindi solo compressi con gzip: nessuna crittografia.
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import struct
import time
import zlib
from dataclasses import dataclass, field
from pathlib import Path

import i18n
import popdata

MAGIC = b"wv\x19P"
GZIP_MAGIC = b"\x1f\x8b\x08"
HEADER_SIZE = 0x432
OFF_CONTENT_ID = 0x41E
OFF_USIZE = 0x422
OFF_CSIZE = 0x42A

SAVE_GAME_FILE = "PopSaveGameSlot{slot}Index0.AlkSave"
PROGRESSION_FILE = "ProgressionSlot{slot}Index0.AlkContent"
OPTIONS_FILE = "GameOptionsSlot{slot}Index0.AlkContent"


# --------------------------------------------------------------------------
# JSON serialization: identica a quella del gioco (compatto, esponente "E")
# --------------------------------------------------------------------------
_EXPONENT = re.compile(r"(?<=[0-9])e(?=[+-]?[0-9])")


def _uppercase_exponents(text: str) -> str:
    """Rende maiuscolo l'esponente dei numeri ('9.53e-07' -> '9.53E-07'),
    esattamente come scrive il gioco, senza toccare le stringhe."""
    out = []
    chunk = []
    in_str = False
    esc = False

    def flush():
        if chunk:
            out.append(_EXPONENT.sub("E", "".join(chunk)))
            chunk.clear()

    for ch in text:
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                flush()
                out.append(ch)
                in_str = True
            else:
                chunk.append(ch)
    flush()
    return "".join(out)


def dumps_json(obj) -> bytes:
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=True)
    return _uppercase_exponents(text).encode("utf-8")


# --------------------------------------------------------------------------
# Container
# --------------------------------------------------------------------------
@dataclass
class Container:
    path: Path
    raw: bytes
    kind: str                      # "json" | "jpeg"
    gz_index: int = 0
    gz_header: bytes = b""
    content_id: int = 0
    outer_usize: int = 0
    outer_csize: int = 0
    name: str = ""
    version: int = 0
    data: bytes = b""              # JSON o JPEG

    # -- lettura ----------------------------------------------------------
    @classmethod
    def load(cls, path: str | Path) -> "Container":
        path = Path(path)
        raw = path.read_bytes()
        if not raw.startswith(MAGIC):
            raise ValueError(f"{path.name}: non e' un contenitore Alk (magic errato)")
        if len(raw) < HEADER_SIZE + 8:
            raise ValueError(f"{path.name}: file troppo corto")

        if raw[HEADER_SIZE:HEADER_SIZE + 3] == GZIP_MAGIC:
            gz_index = HEADER_SIZE
            decomp = zlib.decompressobj(31)
            try:
                payload = decomp.decompress(raw[gz_index:])
            except zlib.error as exc:
                raise ValueError(f"{path.name}: gzip non valido ({exc})") from exc
            if not payload:
                raise ValueError(f"{path.name}: payload vuoto")
            name_len = payload[0]
            name = payload[1:1 + name_len].decode("ascii", "replace")
            version = payload[1 + name_len]
            json_len = struct.unpack_from("<I", payload, 2 + name_len)[0]
            data = payload[6 + name_len:6 + name_len + json_len]
            content_id, outer_usize, outer_csize = struct.unpack_from("<IQQ", raw, OFF_CONTENT_ID)
            return cls(path, raw, "json", gz_index, raw[gz_index:gz_index + 10],
                       content_id, outer_usize, outer_csize, name, version, data)

        # screenshot: record non compresso subito dopo l'header
        name_len = raw[HEADER_SIZE]
        name = raw[HEADER_SIZE + 1:HEADER_SIZE + 1 + name_len].decode("ascii", "replace")
        version = raw[HEADER_SIZE + 1 + name_len]
        data_len = struct.unpack_from("<I", raw, HEADER_SIZE + 2 + name_len)[0]
        data = raw[HEADER_SIZE + 6 + name_len:HEADER_SIZE + 6 + name_len + data_len]
        content_id = struct.unpack_from("<I", raw, OFF_CONTENT_ID)[0]
        return cls(path, raw, "jpeg", 0, b"", content_id, 0, 0, name, version, data)

    # -- accesso ----------------------------------------------------------
    def json(self):
        if self.kind != "json":
            raise TypeError(f"{self.path.name}: non contiene JSON")
        return json.loads(self.data)

    @property
    def text(self) -> str:
        return self.data.decode("utf-8")

    # -- riscrittura ------------------------------------------------------
    def rebuild(self, obj_or_text) -> bytes:
        """Restituisce i byte completi del file con il nuovo contenuto."""
        if self.kind != "json":
            raise TypeError(f"{self.path.name}: riscrittura non supportata")
        if isinstance(obj_or_text, (bytes, str)):
            body = obj_or_text.encode("utf-8") if isinstance(obj_or_text, str) else obj_or_text
            json.loads(body)  # validazione
        else:
            body = dumps_json(obj_or_text)

        name_bytes = self.name.encode("ascii")
        payload = (bytes([len(name_bytes)]) + name_bytes + bytes([self.version])
                   + struct.pack("<I", len(body)) + body)

        comp = zlib.compressobj(9, zlib.DEFLATED, -15, 8, 0)
        raw_deflate = comp.compress(payload) + comp.flush()
        gz = (self.gz_header + raw_deflate
              + struct.pack("<II", zlib.crc32(payload) & 0xFFFFFFFF, len(payload) & 0xFFFFFFFF))

        header = bytearray(self.raw[:self.gz_index])
        struct.pack_into("<Q", header, self.gz_index - 16, len(payload))
        struct.pack_into("<Q", header, self.gz_index - 8, len(gz))
        return bytes(header) + gz


# --------------------------------------------------------------------------
# Percorsi (es. "m_list[1].m_entities[0].m_frames[0]")
# --------------------------------------------------------------------------
_TOKEN = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def parse_path(path: str) -> list:
    tokens = []
    for m in _TOKEN.finditer(path):
        if m.group(1) is not None:
            tokens.append(m.group(1))
        else:
            tokens.append(int(m.group(2)))
    return tokens


def get_path(obj, path: str):
    cur = obj
    for tok in parse_path(path):
        cur = cur[tok]
    return cur


def set_path(obj, path: str, value):
    tokens = parse_path(path)
    if not tokens:
        raise ValueError("percorso vuoto")
    cur = obj
    for tok in tokens[:-1]:
        cur = cur[tok]
    cur[tokens[-1]] = value


def find_path(obj, type_suffix: str, path: str = "", max_depth: int = 40):
    """Trova il primo oggetto con "@type" che termina con type_suffix.
    Restituisce (percorso, oggetto) oppure (None, None)."""
    if max_depth < 0:
        return None, None
    if isinstance(obj, dict):
        t = obj.get("@type")
        if isinstance(t, str) and t.endswith(type_suffix):
            return path, obj
        for k, v in obj.items():
            found, node = find_path(v, type_suffix, f"{path}.{k}" if path else str(k), max_depth - 1)
            if found is not None:
                return found, node
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found, node = find_path(v, type_suffix, f"{path}[{i}]", max_depth - 1)
            if found is not None:
                return found, node
    return None, None


# --------------------------------------------------------------------------
# Salvataggio
# --------------------------------------------------------------------------
class SaveGame:
    """Una cartella Save_*/ con i suoi contenitori."""

    def __init__(self, save_dir: str | Path):
        self.dir = Path(save_dir)
        if not self.dir.is_dir():
            raise FileNotFoundError(f"Cartella non trovata: {self.dir}")
        self.containers: dict[str, Container] = {}
        for p in sorted(self.dir.iterdir()):
            if p.is_file() and p.suffix in (".AlkContent", ".AlkSave"):
                try:
                    self.containers[p.name] = Container.load(p)
                except ValueError:
                    continue

        self.save_file = self._pick("PopSaveGame", ".AlkSave")
        self.progression_file = self._pick("Progression", ".AlkContent")
        self.options_file = self._pick("GameOptions", ".AlkContent")
        self.screenshots = sorted(
            (n for n in self.containers if "GameScreenshot" in n),
            key=lambda n: int(re.search(r"GameScreenshot(\d+)", n).group(1)),
        )

        self._save_json = self.containers[self.save_file].json() if self.save_file else None
        self._prog_json = self.containers[self.progression_file].json() if self.progression_file else None
        self._opt_json = self.containers[self.options_file].json() if self.options_file else None

        loc = {}
        if self._save_json is not None:
            loc["progression"] = find_path(self._save_json, "PlayerProgressionSubComponent+PlayerProgressionSaveData")[0]
            loc["health"] = find_path(self._save_json, "PlayerHealthStateInfo+PlayerHealthStateInfoSaveData")[0]
            loc["loadout"] = find_path(self._save_json, "PlayerLoadoutSubComponent+PlayerLoadoutSaveData")[0]
            loc["gear"] = find_path(self._save_json, "PlayerGearSubComponent+PlayerGearSaveData")[0]
            loc["checkpoint"] = find_path(self._save_json, "PlayerCheckpointSubComponent+CheckpointSaveData")[0]
            loc["fasttravel"] = find_path(self._save_json, "FastTravelStatusSaveDataFrame")[0]
            loc["stats"] = find_path(self._save_json, "GameStatsRecorder+GameStatsDataFrame")[0]
            loc["challenges"] = find_path(self._save_json, "ChallengeManagerSaveDataFrame")[0]
            loc["blackboard"] = find_path(self._save_json, "BlackboardRecorder+BlackboardSaveDataFrame")[0]
            loc["loot"] = find_path(self._save_json, "LootRecorder+LootSaveDataFrame")[0]
            loc["poi"] = find_path(self._save_json, "PointOfInterestRecorder+PointOfInterestSaveDataFrame")[0]
            loc["map"] = find_path(self._save_json, "PlayerMapSubComponent+PlayerMapSaveData")[0]
        self.loc = loc

        # il componente e' un wrapper: i dati veri stanno in .m_progression
        self.prog_path = f"{loc['progression']}.m_progression" if loc.get("progression") else ""
        self.map_prog_path = f"{self.prog_path}.m_playerMapProgressionData" if self.prog_path else ""
        self.prog = get_path(self._save_json, self.prog_path) if self.prog_path else None
        self.inventory = (self.prog or {}).get("m_playerInventoryProgressionData", {}).get("m_inventory", [])
        self.inv_path = f"{self.prog_path}.m_playerInventoryProgressionData.m_inventory"

    def _pick(self, prefix: str, suffix: str):
        for name in self.containers:
            if name.startswith(prefix) and name.endswith(suffix):
                return name
        return None

    # -- helper -----------------------------------------------------------
    def doc(self, key: str) -> str | None:
        return {"save": self.save_file, "progression": self.progression_file,
                "options": self.options_file}.get(key)

    def obj(self, key: str):
        return {"save": self._save_json, "progression": self._prog_json,
                "options": self._opt_json}.get(key)

    def item_index(self, item_type: str):
        for i, it in enumerate(self.inventory):
            if it.get("m_itemType") == item_type:
                return i
        return None

    def crystals(self) -> int:
        i = self.item_index("Crystal")
        return int(self.inventory[i].get("m_itemAmount", 0)) if i is not None else 0

    def playtime(self) -> int:
        return int((self._prog_json or {}).get("m_duration", 0))

    def completion(self) -> float:
        return float((self._prog_json or {}).get("m_completion", 0.0))

    def summary(self, lang: str = "it") -> list[dict]:
        p = self._prog_json or {}
        up = (self.prog or {}).get("m_playerUpgradeProgressionData", {})
        hp = get_path(self._save_json, self.loc["health"]) if self.loc.get("health") else {}
        unlocked = (self.prog or {}).get("m_playerStoneOfKnowledgeProgressionData", {}).get("m_unlockedStoneOfKnowledges", [])
        abilities = (self.prog or {}).get("m_playerAbilitiesProgressionData", {}).get("m_unlockedAbilities", [])
        stage = p.get("m_gameStage", {})
        t = lambda key, **kw: i18n.tr(lang, key, **kw)  # noqa: E731
        return [
            {"label": t("summary.folder"), "value": self.dir.name},
            {"label": t("summary.level"), "value": p.get("m_level", "?")},
            {"label": t("summary.date"), "value": p.get("m_date", "?")},
            {"label": t("summary.playtime"), "value": format_duration(self.playtime())},
            {"label": t("summary.completion"), "value": f"{self.completion() * 100:.2f}%"},
            {"label": t("summary.stage"), "value": str(stage.get("activeStage", "?"))},
            {"label": t("summary.completed"),
             "value": t("summary.yes") if p.get("m_gameCompleted") else t("summary.no")},
            {"label": t("summary.hp"),
             "value": t("summary.hp_value", hp=hp.get("m_CurrentHP", "?"),
                         base=hp.get("m_CurrentHPNoLifeStoneBonus", "?"),
                         bonus=hp.get("m_CurrentLifeStoneBonusHp", "?"))},
            {"label": t("summary.crystals"), "value": str(self.crystals())},
            {"label": t("summary.stones"), "value": t("summary.stones_value", n=len(unlocked))},
            {"label": t("summary.abilities"), "value": str(len(abilities))},
            {"label": t("summary.upgrades"),
             "value": t("summary.upgrades_value", h=up.get("m_healthUpgrades", "?"),
                         s=up.get("m_swordUpgrades", "?"), b=up.get("m_bowUpgrades", "?"),
                         q=up.get("m_quiverUpgrades", "?"))},
            {"label": t("summary.items"), "value": str(len(self.inventory))},
            {"label": t("summary.screenshots"), "value": str(len(self.screenshots))},
        ]

    # -- mappa, viaggi rapidi e sfide --------------------------------------
    def map_layers(self):
        """Genera ((indice mappa, parte, settore), layer) per ogni bitmap della mappa.

        Ogni cella della mappa usa 2 bit (stato 0-3), quindi il numero di parole
e' ceil(m_nbCells * 2 / 32)."""
        if not self.map_prog_path:
            return
        prog = get_path(self._save_json, self.map_prog_path)
        for i, mappa in enumerate(prog.get("m_mapProgressionDatas", [])):
            for j, parte in enumerate(mappa.get("m_data", [])):
                for k, layer in enumerate(parte.get("m_data", [])):
                    if (isinstance(layer, dict) and isinstance(layer.get("m_data"), list)
                            and isinstance(layer.get("m_nbCells"), int)):
                        yield (i, j, k), layer

    def map_stats(self) -> dict:
        maps, layers, cells, words = set(), 0, 0, 0
        for (i, _j, _k), layer in self.map_layers():
            maps.add(i)
            nb = layer["m_nbCells"]
            if len(layer["m_data"]) == math.ceil(nb * 2 / 32):
                layers += 1
                cells += nb
                words += len(layer["m_data"])
        return {"maps": len(maps), "layers": layers, "cells": cells, "words": words}

    def fast_travel_state(self) -> list[dict]:
        frame = get_path(self._save_json, self.loc["fasttravel"]) if self.loc.get("fasttravel") else {}
        unlocked = set(frame.get("m_unlockedGuids", []))
        rows = []
        for p in popdata.FAST_TRAVEL:
            rows.append({
                "guid": p["guid"],
                "name": p["code"],
                "region": p["region"],
                "level": p["level"],
                "unlocked": p["guid"] in unlocked,
            })
        return rows

    def challenge_state(self, lang: str = "it") -> list[dict]:
        frame = get_path(self._save_json, self.loc["challenges"]) if self.loc.get("challenges") else {}
        guids = frame.get("m_challengesGUID", [])
        completions = frame.get("m_challengesCompletions", [])
        lessons = {x["guid"].lower(): x for x in popdata.ARTABAN_LESSONS}
        rows = []
        for i, guid in enumerate(guids):
            lesson = lessons.get(str(guid).lower())
            status = completions[i] if i < len(completions) else "?"
            rows.append({
                "guid": guid,
                "name": i18n.lesson_name(lang, lesson["name_it"], lesson["name_en"]) if lesson
                        else i18n.tr(lang, "field.stone", n=i + 1),
                "code": lesson["code"] if lesson else "",
                "status": status,
                "done": status == "Done",
            })
        return rows

    # -- applica modifiche ------------------------------------------------
    def apply_changes(self, changes: list[dict]) -> list[str]:
        touched: dict[str, Container] = {}
        log = []
        for ch in changes:
            key = ch["doc"]
            path = ch["path"]
            value = ch["value"]
            obj = self.obj(key)
            if obj is None:
                raise ValueError(f"Documento non disponibile: {key}")
            old = get_path(obj, path)
            set_path(obj, path, value)
            log.append(f"{key}: {path} {old!r} -> {value!r}")
            name = self.doc(key)
            touched[name] = self.containers[name]
        backup = self._write(touched)
        return log, backup

    def apply_raw(self, texts: dict[str, str], lang: str = "it") -> list[str]:
        touched = {}
        log = []
        for key, text in texts.items():
            obj = self.obj(key)
            if obj is None:
                raise ValueError(f"Documento non disponibile: {key}")
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON non valido in {key}: {exc}") from exc
            if not isinstance(parsed, dict):
                raise ValueError(f"JSON in {key}: atteso un oggetto")
            # sostituisce il contenuto mantenendo lo stesso oggetto in memoria
            obj.clear()
            obj.update(parsed)
            touched[self.doc(key)] = self.containers[self.doc(key)]
            log.append(i18n.tr(lang, "log.raw", key=key, n=len(text)))
        backup = self._write(touched)
        return log, backup

    def _write(self, touched: dict[str, Container]):
        if not touched:
            return None
        backup_dir = make_backup(self.dir)
        for name, cont in touched.items():
            new_bytes = cont.rebuild(self._json_for(name))
            tmp = cont.path.with_suffix(cont.path.suffix + ".tmp")
            tmp.write_bytes(new_bytes)
            os.replace(tmp, cont.path)
            cont.raw = new_bytes  # aggiorna lo stato in memoria
            # ricarica i riferimenti interni
            fresh = Container.load(cont.path)
            self.containers[name] = fresh
        # riallinea gli oggetti in memoria (json ricaricato)
        if self.save_file in touched:
            self._save_json = self.containers[self.save_file].json()
            self.prog = get_path(self._save_json, self.prog_path)
            self.inventory = self.prog["m_playerInventoryProgressionData"]["m_inventory"]
        if self.progression_file in touched:
            self._prog_json = self.containers[self.progression_file].json()
        if self.options_file in touched:
            self._opt_json = self.containers[self.options_file].json()
        return backup_dir

    def _json_for(self, name: str):
        if name == self.save_file:
            return self._save_json
        if name == self.progression_file:
            return self._prog_json
        if name == self.options_file:
            return self._opt_json
        return self.containers[name].json()


# --------------------------------------------------------------------------
# Backup
# --------------------------------------------------------------------------
def backup_root() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    root = Path(base) / "PoPSaveTool" / "backups"
    root.mkdir(parents=True, exist_ok=True)
    return root


def backup_key(save_dir: Path) -> str:
    return save_dir.name


def make_backup(save_dir: Path) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    dest = backup_root() / f"{backup_key(save_dir)}__{stamp}"
    n = 1
    while dest.exists():
        dest = backup_root() / f"{backup_key(save_dir)}__{stamp}_{n}"
        n += 1
    dest.mkdir(parents=True)
    for p in save_dir.iterdir():
        if p.is_file():
            shutil.copy2(p, dest / p.name)
    return dest


def list_backups(save_dir: Path) -> list[Path]:
    key = backup_key(save_dir)
    if not backup_root().exists():
        return []
    items = [d for d in backup_root().iterdir() if d.is_dir() and d.name.startswith(key + "__")]
    return sorted(items, key=lambda d: d.stat().st_mtime, reverse=True)


def restore_backup(save_dir: Path, backup: Path) -> None:
    make_backup(save_dir)  # conserva lo stato attuale
    for p in backup.iterdir():
        if p.is_file():
            shutil.copy2(p, save_dir / p.name)


# --------------------------------------------------------------------------
# Utility
# --------------------------------------------------------------------------
def format_duration(seconds: int) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}"


def parse_duration(text: str) -> int:
    text = str(text).strip()
    if text.isdigit():
        return int(text)
    parts = text.split(":")
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"durata non valida: {text}")
    parts = [int(p) for p in parts]
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, s = parts
    return h * 3600 + m * 60 + s


SAVE_FILE_GLOB = "PopSaveGame*Index*.AlkSave"


def has_save_files(path: Path) -> bool:
    """True se la cartella contiene almeno un file PopSaveGame*.AlkSave."""
    try:
        return path.is_dir() and any(path.glob(SAVE_FILE_GLOB))
    except OSError:
        return False


def _documents_roots() -> list[Path]:
    """Le cartelle Documenti possibili, inclusa la redirezione OneDrive."""
    home = Path(os.environ.get("USERPROFILE") or Path.home())
    return [
        home / "OneDrive" / "DOCUMENTI", home / "OneDrive" / "Documents",
        home / "Documents", home / "Documenti",
    ]


def save_choice_file() -> Path:
    """Dove viene ricordata l'ultima cartella scelta nell'editor."""
    return backup_root().parent / "last_save.txt"


def remembered_save_dir() -> Path | None:
    f = save_choice_file()
    try:
        if not f.is_file():
            return None
        p = Path(f.read_text(encoding="utf-8", errors="ignore").strip())
    except OSError:
        return None
    return p if has_save_files(p) else None


def remember_save_dir(path: Path) -> None:
    try:
        save_choice_file().write_text(str(Path(path)), encoding="utf-8")
    except OSError:
        pass


def resolve_save_dir(raw: str | Path, lang: str = "it") -> Path:
    """Accetta una cartella Save_*, un SaveSlotN, un profilo o la cartella giochi."""
    text = str(raw).strip().strip('"')
    if not text:
        raise ValueError(i18n.tr(lang, "err.no_folder"))
    path = Path(text).expanduser()
    if not path.is_dir():
        raise ValueError(i18n.tr(lang, "err.folder_missing", path=path))
    if has_save_files(path):
        return path

    children = [c for c in path.iterdir() if has_save_files(c)]
    if children:
        # SaveSlotN con piu' salvataggi: usa il piu' recente.
        return max(children, key=_mtime)

    deep: dict[str, Path] = {}
    for base in (path, path / "Saves"):
        if not base.is_dir():
            continue
        for p in list(base.glob("*/Saves/*/Save_*")) + list(base.glob("Saves/*/Save_*")):
            if has_save_files(p):
                deep.setdefault(str(p.resolve()).lower(), p)
    if len(deep) == 1:
        return next(iter(deep.values()))
    if deep:
        raise ValueError(i18n.tr(lang, "err.multi_save", n=len(deep)))
    raise ValueError(i18n.tr(lang, "err.no_save"))


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def find_save_dirs() -> list[Path]:
    """Elenca i salvataggi trovati in Documenti (i piu' recenti prima)."""
    found: dict[str, Path] = {}

    def add(p: Path) -> None:
        if not has_save_files(p):
            return
        try:
            key = str(p.resolve()).lower()
        except OSError:
            return
        found.setdefault(key, p)

    for base in _documents_roots():
        game = base / "My Games" / "Prince Of Persia The Lost Crown"
        if not game.is_dir():
            continue
        for p in game.glob("*/Saves/*/Save_*"):
            add(p)
        # L'ultima cartella usata dal gioco puo' stare fuori dagli schemi.
        for marker in game.glob("*/Saves/SaveSlot*/lastSavedFolder.txt"):
            try:
                add(marker.parent / marker.read_text(errors="ignore").strip())
            except OSError:
                continue

    remembered = remembered_save_dir()
    if remembered is not None:
        add(remembered)
    return sorted(found.values(), key=lambda p: (_mtime(p), str(p)), reverse=True)


def default_save_dir() -> Path | None:
    """Ultima cartella scelta nell'editor, poi lastSavedFolder.txt del gioco."""
    chosen = remembered_save_dir()
    if chosen is not None:
        return chosen
    for base in _documents_roots():
        saves = base / "My Games" / "Prince Of Persia The Lost Crown"
        if not saves.is_dir():
            continue
        slot_dirs = sorted(saves.glob("*/Saves/*"))
        best = None
        for slot in slot_dirs:
            marker = slot / "lastSavedFolder.txt"
            if not marker.is_file():
                continue
            name = marker.read_text(errors="ignore").strip()
            target = slot / name
            save_file = f"PopSaveGameSlot{_slot_number(slot.name)}Index0.AlkSave"
            if (target / save_file).exists():
                mtime = (target).stat().st_mtime
                if best is None or mtime > best[0]:
                    best = (mtime, target)
        if best:
            return best[1]
        found = sorted(saves.glob("*/Saves/*/Save_*"))
        if found:
            return found[-1]
    return None


def _slot_number(name: str) -> str:
    m = re.search(r"(\d+)$", name or "")
    return m.group(1) if m else "0"
