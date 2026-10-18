# Analysis of Prince of Persia: The Lost Crown save files

## In one sentence

Nothing is encrypted: every `.AlkSave` / `.AlkContent` file is a small
1074-byte binary header followed by an ordinary **gzip** stream containing a
plain-text **JSON file**. Screenshots, on the other hand, are uncompressed JPEGs.
Once you know the JSON key names you can read — and modify — every value in the
save.

## 1. What they are NOT

- They are not encrypted: no key, no AES, no obfuscation.
- They have no integrity checksum: the field at `0x41E` that looks like a CRC is
  actually a **content type identifier** (see §6).
- They do not depend on the file path or name: the game reads the content, not
  the file hash.

## 2. Container structure (`.AlkSave`, `.AlkContent`)

```
offset   size  content
0x0000    4   magic "wv\x19P"  (77 76 19 50)
0x0004    4   0x00000004        (container version)
0x0008    4   content type/flags (0x02, 0x19, 0x20...)
0x000C    4   1 or 3
0x0010    …   descriptive area, in practice all zeros
0x041E    4   CONTENT ID  (NOT a checksum)
0x0422    8   uncompressed payload size
0x042A    8   gzip stream size (header + data + trailer)
0x0432    …   payload
```

The payload comes in two flavours:

**A. Data files (JSON, gzip-compressed)** — `GameOptions`, `Progression`,
`PopSaveGame`:

```
0x00  1   gzip magic 1F 8B 08
0x08  1   XFL = 0
0x09  1   OS  = variable (3, 10...) — irrelevant
…          deflate of the bytes below
last 8     CRC32 + ISIZE of the gzip stream
```

…and the decompressed bytes are:

```
u8   name length (e.g. 0x0B = 11)
…    ASCII name   ("GameOptions", "Progression", "LoadSaveManager")
u8   version (always 1)
u32  JSON length
…    JSON UTF-8, compact format (no spaces), with uppercase exponents (9.53E-07)
```

The internal name is shorter than the file name: `PopSaveGameSlot3Index0.AlkSave`
contains a record called **`LoadSaveManager`**, `Progression…AlkContent`
contains **`Progression`**, and so on.

**B. Screenshots (uncompressed JPEG)** — `GameScreenshot*`:

```
0x0432  1   name length (0x0A)
0x0433 10   "Screenshot"
0x043D  1   version (0)
0x043E  4   JPEG data length
0x0442  …   JPEG (FF D8 FF E0 4A 46 49 46 … FF D9)
```

No gzip here: the image bytes are stored exactly as they are, so simply
trimming the file yields a perfectly valid `.jpg` photo.

## 3. Files in this save

| file | type | internal name | ID at 0x41E | data |
|---|---|---|---|---|
| `PopSaveGameSlot3Index0.AlkSave` | JSON gzip | `LoadSaveManager` | `0xE84D6ADE` | 793,275 bytes |
| `ProgressionSlot3Index0.AlkContent` | JSON gzip | `Progression` | `0xF18B7569` | 443 bytes |
| `GameOptionsSlot3Index0.AlkContent` | JSON gzip | `GameOptions` | `0x13639916` | 1,542 bytes |
| `GameScreenshot0..12Slot3Index0.AlkContent` | JPEG | `Screenshot` | variable | 45–190 KB |

### What they contain

- **`PopSaveGame…AlkSave` — the state of the world.** The JSON has 4 keys:
  `m_list` (87 “scenes”), `m_worldDataGUID`, `m_levelDataGUID`, `m_version`.
  Every scene has a readable name (`CIT_LOW_01_Design`, `SAC_SAC_01_Prison_Design`,
  `HYR_AUT_07_ForestShaman_Design`…), a GUID and a list of entities; every entity
  has a list of *frames* with typed components (`@type`).
  The `GameManager` and `EntitiesManager` scenes hold the global data and the
  character.
- **`Progression`** — the card shown in the “Load game” menu: playtime,
  completion percentage, chapter, date, speedrun/permadeath mode.
- **`GameOptions`** — the game options, saved as pairs
  `{m_value, m_eGameOptionType}` (the numeric id has no name in the file).
- **`GameScreenshot*`** — the 13 saved thumbnails (one per manual/automatic save).

## 4. Where the character values live

All in the `PopSaveGame…AlkSave` file, at the path:

```
m_list[1]  (scene "EntitiesManager")
 └─ m_entities[0]
     └─ m_frames[0]  (DynamicComponentEntityDataFrame)
         └─ m_dataList[]
              [0] PlayerGearSubComponent          available weapons
              [1] PlayerMapSubComponent           revealed map, portals, treasures
              [2] GuardGaugeSubComponent          Athra bar
              [4] PlayerCheckpointSubComponent    last checkpoint (level + x,y,z)
              [5] InventorySubComponent           (empty in this save)
              [6] PlayerHealthSubComponent        health points
              [7] PlayerProgressionSubComponent   ⭐ the important part
              [8] PlayerLoadoutSubComponent       equipment and Focus abilities
```

Inside `[7]` the `m_progression` field holds the modules:

| module | what it contains |
|---|---|
| `m_playerInventoryProgressionData.m_inventory` | the item list (`m_itemType` + `m_itemAmount`): 47 entries. **The currency is `Crystal`** |
| `m_playerUpgradeProgressionData` | upgrade levels: health, sword, bow, quiver, potion count, potion effect |
| `m_playerAbilityProgressionData.m_unlockedAbilities` | unlocked abilities (`AirDash`, `BowAim`, `MiniMap`, …) |
| `m_playerStoneOfKnowledgeProgressionData` | unlocked stones, equipped stones, `m_stoneLevels` (level 1–3 for each stone), available slots |
| `m_playerFocusProgressionData` | Focus abilities 1 and 2, Athra bar level |
| `m_playerSkinProgressionData` | unlocked skins and chromas |
| `m_playerMapProgressionData` | bitmask of revealed rooms (compact encoding, hard to edit by hand) |
| `m_playerHealthProgressionData` | current “progression” health |

Other useful global data in the `GameManager` scenes:

| component | meaning |
|---|---|
| `GameStatsRecorder+GameStatsDataFrame` | gameplay statistics (`m_gameStatsSaves`: hash/value pairs) and per-level counters (`m_worldItemCounters`: how many chests, Xerxes, LoreItems… collected in each area) |
| `FastTravelStatusSaveDataFrame.m_unlockedGuids` | unlocked fast-travel points |
| `ChallengeManagerSaveDataFrame` | temple trials and boss challenges (`Done`/`Locked` states, times) |
| `BlackboardRecorder` | global variables with readable names (`CIT_UPP_04_DATALAYER_MANAGER` = 1…) |
| `LootRecorder`, `RepopulateRecorder`, `PointOfInterestRecorder` | collected loot, respawns, discovered points of interest |
| `QuestSaveDataFrame` | state of every quest (`m_elementName`, `m_currentState`, `m_currentCount`) |

In the profile (the `SaveSlot0` folder — not a save, but the shared settings)
you also find `Settings` (all options with readable types), `Tracking` (career
statistics: amulets, lore, times) and `GameRunTypeInfo`.

## 5. Proof that the field at `0x41E` is not a checksum

1. `Progression` from saves `…770410439` and `…918773693` have **different**
   contents (date, completion) but the same value `0xF18B7569`.
2. `GameOptions` from the two saves is identical and has the same ID `0x13639916`.
3. Screenshots 0–9 share consecutive IDs (`0xEEB6B110`, `…0F`, `…0E`…), a
   behaviour incompatible with a hash.
4. The field is a content type identifier: it **must not be recomputed** when
   the data is modified (and in fact the existing tools leave it untouched).

## 6. How a file is rewritten (the pipeline used by the tool)

1. Backup copy of the whole folder (in `%LOCALAPPDATA%\PoPSaveTool\backups`).
2. The payload is rebuilt: `name length + name + version + u32 length + JSON`.
3. The JSON is re-serialized compactly; a trick makes the exponents uppercase
   the way the game does, so **an unmodified file becomes byte-for-byte
   identical** to the original.
4. Compression with `zlib` level 9, raw deflate, preceded by the **10 original
   gzip header bytes** of the file (mtime/XFL/OS stay the game's own) and
   followed by the computed CRC32 + ISIZE.
5. The two sizes in the header are updated (`0x422` and `0x42A`); the ID at
   `0x41E` is left unchanged.
6. Atomic write (temporary file and `os.replace`).

## 7. Checks performed

The `tests/selfcheck.py` script works on a copy of the save and verifies:

- repacking without changes leaves the internal JSON **identical character for
  character** and the decompressed payload matching the original (all 3
  documents);
- the sizes declared in the header match the payload and the gzip stream;
- the stream is valid gzip (readable by `gzip`);
- after applying changes (crystals, playtime, completion, upgrades) the values
  read back correctly and the files stay consistent;
- screenshots are left untouched.

Result: **all checks passed** on the real save.

### Declared limitations

- It was not possible to **test loading in the game** (that requires launching
  the game). The format structure is reproduced faithfully, but the first load
  should be done carefully, with the backup at hand.
- Rewriting screenshots is not implemented (they are only extracted as JPEG).
- The statistics hash strings (`GameStatsRecorder`) do not have readable names
  yet; `m_worldItemCounters` and the `Blackboard`, on the other hand, already use
  readable keys in the JSON.
- Cloud saves (Ubisoft Connect/Steam) can overwrite the changes: disable
  syncing or play offline after modifying.

## 8. Ready-made actions (map, fast travel, challenges)

### 8.1 Map: the bitmaps in `m_playerMapProgressionData`

The map fog is **not** in `PlayerMapSubComponent`: it is in the player's
progression, inside `PlayerProgressionSubComponent.m_progression`:

```
m_playerMapProgressionData
└─ m_mapProgressionDatas[]          11 areas
   └─ m_data[2]                     two parts per area
      └─ m_data[]                   sectors (layers)
         ├─ m_nbCells                number of cells in the sector
         └─ m_data[]                 32-bit words, 2 bits per cell
```

Each cell uses **2 bits** (states 0–3): this is why `m_nbCells = 1248`
corresponds to 78 words (`1248 × 2 / 32`). The analysed save contains 11 areas,
336 sectors and 445,904 cells. Each word holds 32 bits, so 16 cells, and the number
of words per sector must stay `ceil(m_nbCells * 2 / 32)`.

> Note: the old `reveal_map` action filled every word with `0xFFFFFFFF` (all cells
> at state 3) and set `m_isComplete = true` and `m_displayMapLegend = true` in
> `PlayerMapSubComponent`. It has been **removed**: in-game testing left the map
> stuck and no longer visible, so the tool now only reads these bitmaps.

### 8.2 Fast travel: `PortalData` of type 1

`FastTravelStatusSaveDataFrame.m_unlockedGuids` holds the GUIDs (32 hex chars)
of the `Alkawa.Engine.PortalData` entries with `m_portalType == 1`. The bundle
`worlddata_mainworld_assets_all.bundle` contains exactly **23** portals of this
type, with a name (`MainWorld_FastTravel_<level>`) and a reference to the
`LevelData` (hence to the scene, e.g. `CIT_LOW_07_Up`). The map positions are in
`FastTravelMetadataItem.FastTravelPositions`, indexed by
`m_PortalComponentGUID`. The action merges the 23 GUIDs with the ones already
present, without duplicates and without removing anything.

### 8.3 Temple challenges: Artaban's lessons

`ChallengeManagerSaveDataFrame` has 13 `m_challengesGUID` entries and as many
`m_challengesCompletions` (`Done`/`Locked`). The GUIDs correspond to the
`ArtabanLesson_*` assets in the `mandatory_gamemanager_assets_all.bundle`; the
Italian names come from locIds 15524–15634 of the localization table
(`data_scriptableobjects_localization_assets_all.bundle`): Attacchi standard,
Lanci, Attacchi in aria, Attacchi con carica, Reazioni nemiche, Opzioni di
difesa, Mosse avanzate, Parata, Onda di Athra, Arco e chakram, Ombra di Simurgh,
Trama del mondo, Scatto di Simurgh. The action sets every entry to `Done`.

### 8.4 Extracting the game data

The lists are in `popdata.py`. They were extracted with UnityPy from the
Addressables bundles (`StreamingAssets/aa/StandaloneWindows64/…`) and are
**static**: they hold for the analysed build. To regenerate them:
`pip install UnityPy` and `python tmp/extract_gamedata.py` (the script reads the
Steam installation).

## 9. Summary of this save

| item | value |
|---|---|
| Folder | `SaveSlot3\Save_134359460918773693` (last saved, from `lastSavedFolder.txt`) |
| Level | `90a0ea3a0469f064d8e44e9d7b0d4950` |
| Date | 08/10/2026 17:14:51 |
| Playtime | 3:45:52 |
| Completion | 20.57 % |
| Chapter | `Abducted_Prince` (completed: `Persia_Attacked`, `Lost_In_MountQaf`) |
| Health points | 100 (80 base + 20 LifeStone) |
| Crystals (currency) | 1,484 |
| Unlocked stones | 11, all at level 1 |
| Abilities | 10 (`AirDash`, `BowAim`, `ChakramAim`, `MiniMap`, `Vision`, 4 Focus, `AirDodgeBack`) |
| Upgrades | health 1, sword 1, bow 0, quiver 1, potion count 0, potion effect 1 |
| Inventory | 47 entries |
| Fast travels | 3 |
| Saved scenes | 87 |
| Screenshots | 13 |
