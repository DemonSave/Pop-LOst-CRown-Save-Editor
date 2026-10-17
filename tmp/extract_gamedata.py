#!/usr/bin/env python3
"""Rigenera popdata.py dai bundle Addressables del gioco.

Serve solo quando il gioco viene aggiornato. Richiede UnityPy e l'installazione
Steam (percorso rilevato automaticamente, oppure POP_GAME_DIR).

    py -m pip install --user UnityPy
    py tmp/extract_gamedata.py

Non modifica nulla nel gioco: legge i bundle e riscrive ../popdata.py.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

try:
    import UnityPy
except ImportError:
    sys.exit("UnityPy non installato: py -m pip install --user UnityPy")

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "popdata.py"

REGIONS = [
    ("CIT_LOW", "Città Bassa"), ("CIT_UPP", "Città Alta"),
    ("CIT_OLD", "Vecchia Strada Reale"), ("CIT_DEP", "Profondità della Città"),
    ("HYR_AUT", "Foresta Ircana (autunno)"), ("HYR_SOM", "Foresta Ircana (Soma)"),
    ("SAC_SAC", "Archivi Sacri"), ("NEC_TOW", "Torre del Silenzio"),
    ("END_PIT", "Fossa delle Sabbie Eterne"), ("VAL_RAG", "Mare Infernale"),
    ("VAL_SUN", "Baia del Sole"), ("RAD_", "DLC — Mente di Radjen"),
    ("CU3", "DLC"), ("KIN_", "Monte Qaf"), ("CRO_", "Crocevia dei Tempi"),
]

LESSON_NAMES = {
    "GroundedAttacks": ("Attacchi standard", "Standard Attacks"),
    "Launchers": ("Lanci", "Launchers"),
    "Aerials": ("Attacchi in aria", "Aerial Attacks"),
    "Charged": ("Attacchi con carica", "Charged Attacks"),
    "NMEs": ("Reazioni nemiche", "Enemies Reactions"),
    "Defense": ("Opzioni di difesa", "Defensive Options"),
    "Movement": ("Mosse avanzate", "Advanced Movements"),
    "Parry": ("Parata", "Parry"),
    "Athra": ("Onda di Athra", "Athra Surge"),
    "Bow": ("Arco e chakram", "Bow & Chakram"),
    "Teleport": ("Ombra di Simurgh", "Shadow of the Simurgh"),
    "Scarf": ("Trama del mondo", "Fabric of the World"),
    "Airdash": ("Scatto di Simurgh", "Rush of the Simurgh"),
}


def find_streaming_assets() -> Path:
    env = os.environ.get("POP_GAME_DIR")
    candidates = []
    if env:
        candidates.append(Path(env))
    candidates += [
        Path(r"C:\Program Files (x86)\Steam\steamapps\common\Prince of Persia The Lost Crown"),
        Path(r"C:\Program Files\Steam\steamapps\common\Prince of Persia The Lost Crown"),
    ]
    for game in candidates:
        aa = game / "TheLostCrown_Data" / "StreamingAssets" / "aa" / "StandaloneWindows64"
        if aa.is_dir():
            return aa
    sys.exit("Installazione non trovata: imposta POP_GAME_DIR sulla cartella del gioco")


def monobehaviours(path: Path):
    env = UnityPy.load(str(path))
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            yield obj.read_typetree()
        except Exception:
            continue


def read_tables(aa: Path):
    tables = {}
    for tt in monobehaviours(aa / "data_scriptableobjects_localization_assets_all.bundle"):
        lines = tt.get("oasisLines")
        if not isinstance(lines, dict):
            continue
        ids = lines.get("m_keys", [])
        texts = lines.get("m_values", [])
        tables[tt.get("m_Name")] = {k: (v or {}).get("text") for k, v in zip(ids, texts)}
    return tables


def fast_travel(aa: Path):
    positions = {}
    meta_path = aa / "scriptablesingleton__scenemetadatamanager_assets_all.bundle"
    for tt in monobehaviours(meta_path):
        if str(tt.get("m_Name", "")).startswith("FastTravelMetadataItem"):
            data = tt.get("FastTravelPositions") or {}
            for key, pos in zip(data.get("m_keys", []), data.get("m_values", [])):
                positions[str(key).lower()] = pos

    # path_id -> typetree, per risolvere i PPtr verso i LevelData
    by_id = {}
    env = UnityPy.load(str(aa / "worlddata_mainworld_assets_all.bundle"))
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            by_id[obj.path_id] = obj.read_typetree()
        except Exception:
            continue

    rows = []
    for tt in by_id.values():
        if tt.get("m_portalType") != 1 or not isinstance(tt.get("m_GUID"), str):
            continue
        level = by_id.get((tt.get("m_level") or {}).get("m_PathID")) or {}
        scene = (level.get("m_sceneRef") or {}).get("m_SceneName") or level.get("m_Name", "")
        code = re.sub(r"^(MainWorld_FastTravel_|FastTravel_)", "", str(tt.get("m_Name", "")))
        code = re.sub(r"(_\d+| \d+)$", "", code)
        region = next((label for prefix, label in REGIONS if scene.startswith(prefix)), "Monte Qaf")
        rows.append({
            "guid": tt["m_GUID"],
            "level": scene,
            "level_guid": level.get("m_GUID"),
            "code": code,
            "region": region,
            "portal": tt.get("m_PortalComponentGUID"),
            "pos": positions.get(str(tt.get("m_PortalComponentGUID", "")).lower()),
        })
    rows.sort(key=lambda r: (r["region"], r["code"]))
    return rows


def lessons(aa: Path, tables):
    italian = tables.get("OasisLocalizationTable_Italian", {})
    english = tables.get("OasisLocalizationTable_English", {})
    rows = []
    for tt in monobehaviours(aa / "mandatory_gamemanager_assets_all.bundle"):
        name = str(tt.get("m_Name", ""))
        guid = tt.get("m_GUID")
        if not (name.startswith("ArtabanLesson_") and isinstance(guid, str)):
            continue
        code = name.split("_", 1)[1]
        loc_id = ((tt.get("m_buttonMenuData") or {}).get("m_buttonTextData") or {}).get("m_locId")
        it = italian.get(loc_id) or LESSON_NAMES.get(code, (code, code))[0]
        en = english.get(loc_id) or LESSON_NAMES.get(code, (code, code))[1]
        rows.append({"guid": guid, "code": name, "name_it": it, "name_en": en, "_loc": loc_id or 0})
    rows.sort(key=lambda r: r["_loc"])
    for row in rows:
        row.pop("_loc", None)
    return rows


def main():
    aa = find_streaming_assets()
    print(f"bundle: {aa}")
    tables = read_tables(aa)
    travel = fast_travel(aa)
    temple = lessons(aa, tables)
    print(f"viaggi rapidi: {len(travel)} | lezioni: {len(temple)}")

    head = '''"""
Dati di gioco estratti dai bundle Addressables di Prince of Persia: The Lost Crown.

Sorgenti (installazione Steam, build con DLC1):
  StreamingAssets/aa/StandaloneWindows64/worlddata_mainworld_assets_all.bundle
      -> PortalData (m_portalType == 1 = viaggio rapido), LevelData (scena/nome)
  StreamingAssets/aa/StandaloneWindows64/scriptablesingleton__scenemetadatamanager_assets_all.bundle
      -> posizioni dei punti di viaggio rapido (FastTravelPositions)
  StreamingAssets/aa/StandaloneWindows64/mandatory_gamemanager_assets_all.bundle
      -> lezioni di Artaban (m_GUID + locId)
  StreamingAssets/aa/StandaloneWindows64/data_scriptableobjects_localization_assets_all.bundle
      -> nomi localizzati delle lezioni (italiano/inglese)

File generato da tmp/extract_gamedata.py: non modificare a mano.
"""

'''
    body = f"REGIONS = {REGIONS!r}\n\nFAST_TRAVEL = [\n"
    body += "".join(f"    {row!r},\n" for row in travel)
    body += "]\n\nARTABAN_LESSONS = [\n"
    body += "".join(f"    {row!r},\n" for row in temple)
    body += "]\n"
    OUT.write_text(head + body, encoding="utf-8", newline="\n")
    print(f"scritto {OUT}")


if __name__ == "__main__":
    main()
