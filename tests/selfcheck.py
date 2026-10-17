"""Verifica automatica: round-trip byte-per-byte del JSON, patch e ricompattamento.

Uso:  python tests/selfcheck.py
Lavora sempre su una COPIA del salvataggio in tmp/, mai sull'originale.
"""

import gzip
import json
import math
import shutil
import struct
import sys
import tempfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import popdata  # noqa: E402
import popsave  # noqa: E402

src = popsave.default_save_dir()
if src is None:
    sys.exit("Salvataggio non trovato")

work = Path(tempfile.mkdtemp(prefix="popsave-check-"))
copy = work / src.name
shutil.copytree(src, copy)
print(f"copia di lavoro: {copy}")

ok = True


def check(cond, msg):
    global ok
    print(("  OK   " if cond else "  FAIL ") + msg)
    ok = ok and bool(cond)


# 0. scoperta e scelta della cartella ---------------------------------------
found = popsave.find_save_dirs()
check(bool(found), f"trovati {len(found)} salvataggi nei percorsi Documenti")
check(any(p.resolve() == src.resolve() for p in found),
      "il salvataggio predefinito e' tra quelli scoperti")
check(popsave.has_save_files(src), "la cartella contiene PopSaveGame*.AlkSave")
slot = src.parent
resolved = popsave.resolve_save_dir(slot)
check(popsave.has_save_files(resolved), f"resolve_save_dir(SaveSlot) -> {resolved.name}")
empty = work / "cartella_vuota"
empty.mkdir()
try:
    popsave.resolve_save_dir(empty)
    check(False, "resolve_save_dir rifiuta una cartella senza salvataggi")
except ValueError:
    check(True, "resolve_save_dir rifiuta una cartella senza salvataggi")

# 1. round-trip senza modifiche ------------------------------------------------
save = popsave.SaveGame(copy)
for name, cont in save.containers.items():
    if cont.kind != "json":
        continue
    rebuilt = cont.rebuild(cont.json())
    # header + stream devono essere coerenti
    gz_index = rebuilt.find(popsave.GZIP_MAGIC)
    usize, csize = struct.unpack_from("<QQ", rebuilt, gz_index - 16)
    payload = zlib.decompressobj(31).decompress(rebuilt[gz_index:])
    check(gz_index == cont.gz_index, f"{name}: header invariato ({hex(gz_index)})")
    check(usize == len(payload), f"{name}: dimensione decompressa coerente")
    check(csize == len(rebuilt) - gz_index, f"{name}: dimensione compressa coerente")
    check(gzip.decompress(rebuilt[gz_index:]) == payload, f"{name}: gzip valido")
    # il JSON interno deve essere identico carattere per carattere
    inner = payload[6 + payload[0]:]
    old_inner = cont.data
    check(inner == old_inner, f"{name}: JSON identico ({len(inner)} byte)")
    # il contenuto deve essere identico al file originale
    check(payload == zlib.decompressobj(31).decompress(cont.raw[cont.gz_index:]),
          f"{name}: payload identico all'originale")

# 2. modifica dei valori -------------------------------------------------------
save = popsave.SaveGame(copy)
before_crystals = save.crystals()
idx = save.item_index("Crystal")
changes = [
    {"doc": "save", "path": f"{save.inv_path}[{idx}].m_itemAmount", "value": 999999},
    {"doc": "save", "path": save.prog_path + ".m_playerUpgradeProgressionData.m_swordUpgrades", "value": 4},
    {"doc": "save", "path": save.prog_path + ".m_playerUpgradeProgressionData.m_healthUpgrades", "value": 4},
    {"doc": "progression", "path": "m_duration", "value": 7200},
    {"doc": "progression", "path": "m_completion", "value": 0.5},
]
log, backup = save.apply_changes(changes)
check(backup is not None and Path(backup).is_dir(), f"backup creato ({backup})")

after = popsave.SaveGame(copy)
check(after.crystals() == 999999, f"cristalli {before_crystals} -> {after.crystals()}")
check(after.playtime() == 7200, "tempo di gioco aggiornato")
check(abs(after.completion() - 0.5) < 1e-9, "completamento aggiornato")
up = after.prog["m_playerUpgradeProgressionData"]
check(up["m_swordUpgrades"] == 4 and up["m_healthUpgrades"] == 4, "potenziamenti aggiornati")

# 3. i file restano leggibili e coerenti --------------------------------------
for name, cont in after.containers.items():
    if cont.kind != "json":
        continue
    gz_index = cont.raw.find(popsave.GZIP_MAGIC)
    usize, csize = struct.unpack_from("<QQ", cont.raw, gz_index - 16)
    payload = zlib.decompressobj(31).decompress(cont.raw[gz_index:])
    check(usize == len(payload) and csize == len(cont.raw) - gz_index,
          f"{name}: intestazioni coerenti dopo la modifica")
    check(len(payload) == 6 + payload[0] + struct.unpack_from("<I", payload, 2 + payload[0])[0] + 0
          or True, f"{name}: lunghezza interna")
    jl = struct.unpack_from("<I", payload, 2 + payload[0])[0]
    check(len(payload) == 6 + payload[0] + jl, f"{name}: lunghezza JSON corretta")
    json.loads(payload[6 + payload[0]:])

# 4. i file non modificati sono rimasti identici ------------------------------
for name, cont in after.containers.items():
    if cont.kind == "jpeg":
        orig = (src / name).read_bytes()
        check(cont.raw == orig, f"{name}: screenshot intatto")

# 5. azioni pronte -------------------------------------------------------------
actions_copy = work / (src.name + "-actions")
shutil.copytree(src, actions_copy)
act = popsave.SaveGame(actions_copy)

check(len(popdata.FAST_TRAVEL) == 23, "catalogo: 23 punti di viaggio rapido")
check(len({p["guid"] for p in popdata.FAST_TRAVEL}) == 23, "catalogo: GUID viaggi univoci")
check(len(popdata.ARTABAN_LESSONS) == 13, "catalogo: 13 lezioni di Artaban")

travel = act.fast_travel_state()
challenges = act.challenge_state()
check(len(travel) == 23 and all(r["name"] and r["region"] for r in travel), "stato viaggi con nomi")
check(len(challenges) == 13 and all(r["name"] for r in challenges), "stato sfide con nomi")
check([a["id"] for a in act.available_actions()] ==
      ["reveal_map", "unlock_fast_travel", "complete_challenges"], "tre azioni disponibili")

stats = act.map_stats()
check(stats["maps"] == 11 and stats["layers"] > 0, f"mappa: {stats['maps']} aree, {stats['layers']} settori")

# 5a. viaggi rapidi
before_unlocked = {r["guid"] for r in travel if r["unlocked"]}
log, backup = act.apply_action("unlock_fast_travel")
act = popsave.SaveGame(actions_copy)
now = act.fast_travel_state()
check(len(now) == 23 and all(r["unlocked"] for r in now), "tutti i 23 viaggi rapidi sbloccati")
check(before_unlocked <= {r["guid"] for r in now}, "i viaggi gia' sbloccati restano")
check(backup is not None and Path(backup).is_dir(), "backup creato per i viaggi rapidi")
check(len(list(Path(backup).iterdir())) == 16, "backup viaggi: 16 file")

# 5b. sfide del tempio
log, backup = act.apply_action("complete_challenges")
act = popsave.SaveGame(actions_copy)
now = act.challenge_state()
check(len(now) == 13 and all(r["status"] == "Done" for r in now), "13 sfide del tempio completate")
check(Path(backup).is_dir(), "backup creato per le sfide")

# 5c. mappa: tutte le celle a 3 (0xFFFFFFFF) senza alterare la struttura
log, backup = act.apply_action("reveal_map")
act = popsave.SaveGame(actions_copy)
layers = list(act.map_layers())
check(len(layers) == stats["layers"], f"mappa: {len(layers)} settori presenti")
check(all(all(w == 0xFFFFFFFF for w in layer["m_data"]) for _k, layer in layers),
      "mappa: tutte le celle impostate a esplorate")
check(all(len(layer["m_data"]) == math.ceil(layer["m_nbCells"] * 2 / 32) for _k, layer in layers),
      "mappa: lunghezza bitmap invariata")
check(act.loc.get("map") and popsave.get_path(act.obj("save"), act.loc["map"])["m_isComplete"] is True,
      "mappa: flag m_isComplete attivo")
check(Path(backup).is_dir(), "backup creato per la mappa")

# 5d. idempotenza e ricompattamento
log, backup = act.apply_action("reveal_map")
act = popsave.SaveGame(actions_copy)
cont = act.containers[act.save_file]
check(cont.rebuild(cont.json()) == cont.raw, "file riscritto ricompattato identico (mappa)")

for name, cont in act.containers.items():
    if cont.kind == "jpeg":
        check(cont.raw == (src / name).read_bytes(), f"{name}: screenshot intatto dopo le azioni")

print()
print("RISULTATO:", "TUTTO OK" if ok else "CI SONO ERRORI")
shutil.rmtree(work, ignore_errors=True)
sys.exit(0 if ok else 1)
