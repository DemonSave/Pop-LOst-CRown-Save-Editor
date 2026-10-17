# Analisi dei salvataggi di Prince of Persia: The Lost Crown

## In una frase

Non c'è nulla di cifrato: ogni file `.AlkSave` / `.AlkContent` è un piccolo
intestazione binaria da 1074 byte seguita da un normale flusso **gzip** che
contiene un **file JSON di testo**. Gli screenshot sono invece JPEG non compressi.
Conoscendo i nomi delle voci JSON si può leggere — e modificare — ogni valore
del salvataggio.

## 1. Cosa NON sono

- Non sono cifrati: nessuna chiave, nessun AES, nessuna offuscazione.
- Non hanno un checksum di integrità: il campo a `0x41E` che sembra un CRC è in
  realtà un **identificatore del tipo di contenuto** (vedi §6).
- Non dipendono dal percorso o dal nome del file: il gioco legge il contenuto,
  non l'hash del file.

## 2. Struttura del contenitore (`.AlkSave`, `.AlkContent`)

```
offset   dim  contenuto
0x0000    4   magic "wv\x19P"  (77 76 19 50)
0x0004    4   0x00000004        (versione del contenitore)
0x0008    4   tipo/flags del contenuto (0x02, 0x19, 0x20...)
0x000C    4   1 o 3
0x0010    …   area descrittiva, in pratica tutti zeri
0x041E    4   ID DEL CONTENUTO  (NON un checksum)
0x0422    8   dimensione del payload decompresso
0x042A    8   dimensione dello stream gzip (header + dati + trailer)
0x0432    …   payload
```

Il payload ha due forme:

**A. File di dati (JSON, compresso gzip)** — `GameOptions`, `Progression`,
`PopSaveGame`:

```
0x00  1   magic gzip 1F 8B 08
0x08  1   XFL = 0
0x09  1   OS  = variabile (3, 10...) — irrilevante
…          deflate dei byte sottostanti
ultimi 8    CRC32 + ISIZE del flusso gzip
```

…e i byte decompressi sono:

```
u8   lunghezza del nome (es. 0x0B = 11)
…    nome ASCII   ("GameOptions", "Progression", "LoadSaveManager")
u8   versione (sempre 1)
u32  lunghezza del JSON
…    JSON UTF-8, formato compatto (senza spazi), con esponenti maiuscoli (9.53E-07)
```

Il nome interno è più corto del nome file: `PopSaveGameSlot3Index0.AlkSave`
contiene un record chiamato **`LoadSaveManager`**, `Progression…AlkContent`
contiene **`Progression`**, e così via.

**B. Screenshot (JPEG non compresso)** — `GameScreenshot*`:

```
0x0432  1   lunghezza nome (0x0A)
0x0433 10   "Screenshot"
0x043D  1   versione (0)
0x043E  4   lunghezza dei dati JPEG
0x0442  …   JPEG (FF D8 FF E0 4A 46 49 46 … FF D9)
```

Nessun gzip qui: i byte dell'immagine sono salvati così come sono, quindi basta
ritagliare il file per ottenere una foto `.jpg` perfettamente valida.

## 3. Elenco dei file di questo salvataggio

| file | tipo | nome interno | ID a 0x41E | dati |
|---|---|---|---|---|
| `PopSaveGameSlot3Index0.AlkSave` | JSON gzip | `LoadSaveManager` | `0xE84D6ADE` | 793.275 byte |
| `ProgressionSlot3Index0.AlkContent` | JSON gzip | `Progression` | `0xF18B7569` | 443 byte |
| `GameOptionsSlot3Index0.AlkContent` | JSON gzip | `GameOptions` | `0x13639916` | 1.542 byte |
| `GameScreenshot0..12Slot3Index0.AlkContent` | JPEG | `Screenshot` | variabile | 45–190 KB |

### Che cosa contengono

- **`PopSaveGame…AlkSave` — lo stato del mondo.** Il JSON ha 4 chiavi:
  `m_list` (87 “scene”), `m_worldDataGUID`, `m_levelDataGUID`, `m_version`.
  Ogni scena ha un nome leggibile (`CIT_LOW_01_Design`, `SAC_SAC_01_Prison_Design`,
  `HYR_AUT_07_ForestShaman_Design`…), un GUID e una lista di entità; ogni entità
  ha una lista di *frame* con componenti tipizzati (`@type`).
  Le scene `GameManager` ed `EntitiesManager` contengono i dati globali e il
  personaggio.
- **`Progression`** — la scheda mostrata nel menu “Carica partita”: tempo di gioco,
  percentuale di completamento, capitolo, data, modalità speedrun/permadeath.
- **`GameOptions`** — le opzioni di gioco, salvate come coppie
  `{m_value, m_eGameOptionType}` (l'id numerico non ha un nome nel file).
- **`GameScreenshot*`** — le 13 anteprime salvate (una per salvataggio manuale/automatico).

## 4. Dove sono i valori del personaggio

Tutto nel file `PopSaveGame…AlkSave`, nel percorso:

```
m_list[1]  (scena "EntitiesManager")
 └─ m_entities[0]
     └─ m_frames[0]  (DynamicComponentEntityDataFrame)
         └─ m_dataList[]
              [0] PlayerGearSubComponent          armi disponibili
              [1] PlayerMapSubComponent           mappa svelata, portali, tesori
              [2] GuardGaugeSubComponent          barra Athra
              [4] PlayerCheckpointSubComponent    ultimo checkpoint (livello + x,y,z)
              [5] InventorySubComponent           (vuoto in questo salvataggio)
              [6] PlayerHealthSubComponent        punti vita
              [7] PlayerProgressionSubComponent   ⭐ il pezzo importante
              [8] PlayerLoadoutSubComponent       equipaggiamento e abilità Focus
```

Dentro `[7]` il campo `m_progression` contiene i moduli:

| modulo | che cosa contiene |
|---|---|
| `m_playerInventoryProgressionData.m_inventory` | l'elenco oggetti (`m_itemType` + `m_itemAmount`): 47 voci. **La moneta è `Crystal`** |
| `m_playerUpgradeProgressionData` | livelli potenziamenti: vita, spada, arco, faretra, numero pozioni, effetto pozioni |
| `m_playerAbilityProgressionData.m_unlockedAbilities` | abilità sbloccate (`AirDash`, `BowAim`, `MiniMap`, …) |
| `m_playerStoneOfKnowledgeProgressionData` | pietre sbloccate, pietre equipaggiate, `m_stoneLevels` (livello 1–3 di ogni pietra), slot disponibili |
| `m_playerFocusProgressionData` | abilità Focus 1 e 2, livello della barra Athra |
| `m_playerSkinProgressionData` | skin e chroma sbloccati |
| `m_playerMapProgressionData` | bitmask delle stanze rivelate (codice compatto, difficile da modificare a mano) |
| `m_playerHealthProgressionData` | vita corrente “di progressione” |

Altri dati globali utili nelle scene `GameManager`:

| componente | significato |
|---|---|
| `GameStatsRecorder+GameStatsDataFrame` | statistiche di gioco (`m_gameStatsSaves`: coppie hash/valore) e i contatori per livello (`m_worldItemCounters`: quanti forzieri, Xerxes, LoreItem… raccolti in ogni area) |
| `FastTravelStatusSaveDataFrame.m_unlockedGuids` | punti di viaggio rapido sbloccati |
| `ChallengeManagerSaveDataFrame` | prove del tempio e sfide boss (stati `Done`/`Locked`, tempi) |
| `BlackboardRecorder` | variabili globali con nome leggibile (`CIT_UPP_04_DATALAYER_MANAGER` = 1…) |
| `LootRecorder`, `RepopulateRecorder`, `PointOfInterestRecorder` | bottino raccolto, respawn, punti d'interesse scoperti |
| `QuestSaveDataFrame` | stato di tutte le quest (`m_elementName`, `m_currentState`, `m_currentCount`) |

Nel profilo (cartella `SaveSlot0`, non è un salvataggio ma le impostazioni
condivise) si trovano inoltre `Settings` (tutte le opzioni con tipo leggibile),
`Tracking` (statistiche di carriera: amuleti, lore, tempi) e `GameRunTypeInfo`.

## 5. Prova che il campo a `0x41E` non è un checksum

1. `Progression` del salvataggio `…770410439` e `…918773693` hanno contenuti
   **diversi** (data, completamento) ma lo stesso valore `0xF18B7569`.
2. `GameOptions` dei due salvataggi è identico e ha lo stesso ID `0x13639916`.
3. Gli screenshot 0–9 condividono ID consecutivi (`0xEEB6B110`, `…0F`, `…0E`…),
   comportamento incompatibile con un hash.
4. Il campo è un identificatore del tipo di contenuto: **non va ricalcolato**
   quando si modificano i dati (e infatti i tool esistenti lo lasciano intatto).

## 6. Come si riscrive un file (la pipeline usata dal tool)

1. Copia di backup dell'intera cartella (in `%LOCALAPPDATA%\PoPSaveTool\backups`).
2. Si ricostruisce il payload: `lunghezza nome + nome + versione + u32 lunghezza + JSON`.
3. Il JSON viene riserializzato in modo compatto; un accorgimento rende gli
   esponenti maiuscoli come fa il gioco, così **un file non modificato
   ridiventa identico byte per byte**.
4. Compressione con `zlib` livello 9, deflate grezzo, preceduta dai **10 byte di
   intestazione gzip originali** del file (mtime/XFL/OS restano quelli del gioco)
   e seguita da CRC32 + ISIZE calcolati.
5. Si aggiornano le due dimensioni nell'intestazione (`0x422` e `0x42A`); l'ID a
   `0x41E` resta invariato.
6. Scrittura atomica (file temporaneo e `os.replace`).

## 7. Verifiche effettuate

Lo script `tests/selfcheck.py` lavora su una copia del salvataggio e controlla:

- ricompattando senza modifiche, il JSON interno è **identico carattere per
  carattere** e il payload decompresso coincide con l'originale (tutti e 3 i
  documenti);
- le dimensioni dichiarate nell'intestazione corrispondono a payload e flusso gzip;
- il flusso è un gzip valido (leggibile da `gzip`);
- applicando modifiche (cristalli, tempo di gioco, completamento, potenziamenti)
  i valori si rileggono correttamente e i file restano consistenti;
- gli screenshot non vengono toccati.

Esito: **tutte le verifiche superate** sul salvataggio reale.

### Limiti dichiarati

- Non è stato possibile **provare il caricamento nel gioco** (serve avviare il
  gioco). La struttura del formato è riprodotta fedelmente, ma il primo
  caricamento va fatto con calma e con il backup a portata di mano.
- Non è implementata la riscrittura degli screenshot (vengono solo estratti in JPEG).
- Le stringhe hash delle statistiche (`GameStatsRecorder`) non hanno ancora nomi
  leggibili; i contatori `m_worldItemCounters` e il `Blackboard` invece usano
  chiavi già leggibili nel JSON.
- I salvataggi cloud (Ubisoft Connect/Steam) possono sovrascrivere le modifiche:
  conviene disattivare la sincronizzazione o giocare offline dopo la modifica.

## 8. Azioni pronte (mappa, viaggi rapidi, sfide)

### 8.1 Mappa: le bitmap in `m_playerMapProgressionData`

La nebbia della mappa **non** è in `PlayerMapSubComponent`: è nella progressione
del giocatore, dentro `PlayerProgressionSubComponent.m_progression`:

```
m_playerMapProgressionData
└─ m_mapProgressionDatas[]          11 aree
   └─ m_data[2]                     due parti per area
      └─ m_data[]                   settori (layer)
         ├─ m_nbCells                numero di celle del settore
         └─ m_data[]                 parole da 32 bit, 2 bit per cella
```

Ogni cella usa **2 bit** (stati 0–3): per questo `m_nbCells = 1248` corrisponde a
78 parole (`1248 × 2 / 32`). Nel salvataggio analizzato ci sono 11 aree, 336
settori e 445.904 celle. L'azione `reveal_map` scrive `0xFFFFFFFF` in ogni parola
(tutte le celle a stato 3) **senza cambiare il numero di parole**, e imposta
`m_isComplete = true` e `m_displayMapLegend = true` in `PlayerMapSubComponent`.

### 8.2 Viaggi rapidi: `PortalData` di tipo 1

`FastTravelStatusSaveDataFrame.m_unlockedGuids` contiene i GUID (32 hex) dei
`Alkawa.Engine.PortalData` con `m_portalType == 1`. Nel bundle
`worlddata_mainworld_assets_all.bundle` ci sono esattamente **23** portal di
questo tipo, con nome (`MainWorld_FastTravel_<livello>`) e riferimento al
`LevelData` (quindi alla scena, es. `CIT_LOW_07_Up`). Le posizioni per la mappa
sono in `FastTravelMetadataItem.FastTravelPositions`, indicizzate dal
`m_PortalComponentGUID`. L'azione fusiona i 23 GUID con quelli già presenti,
senza duplicati e senza rimuovere nulla.

### 8.3 Sfide del tempio: le lezioni di Artaban

`ChallengeManagerSaveDataFrame` ha 13 `m_challengesGUID` e altrettanti
`m_challengesCompletions` (`Done`/`Locked`). I GUID corrispondono agli asset
`ArtabanLesson_*` nel bundle `mandatory_gamemanager_assets_all.bundle`; i nomi
italiani vengono dai locId 15524–15634 della tabella di localizzazione
(`data_scriptableobjects_localization_assets_all.bundle`): Attacchi standard,
Lanci, Attacchi in aria, Attacchi con carica, Reazioni nemiche, Opzioni di
difesa, Mosse avanzate, Parata, Onda di Athra, Arco e chakram, Ombra di Simurgh,
Trama del mondo, Scatto di Simurgh. L'azione porta tutte le voci a `Done`.

### 8.4 Estrazione dei dati di gioco

Gli elenchi sono in `popdata.py`. Sono stati estratti con UnityPy dai bundle
Addressables (`StreamingAssets/aa/StandaloneWindows64/…`) e sono **statici**:
valgono per la build analizzata. Per rigenerarli: `pip install UnityPy` e
`python tmp/extract_gamedata.py` (lo script legge l'installazione Steam).

## 9. Riepilogo di questo salvataggio

| voce | valore |
|---|---|
| Cartella | `SaveSlot3\Save_134359460918773693` (ultima salvata, da `lastSavedFolder.txt`) |
| Livello | `90a0ea3a0469f064d8e44e9d7b0d4950` |
| Data | 08/10/2026 17:14:51 |
| Tempo di gioco | 3:45:52 |
| Completamento | 20,57 % |
| Capitolo | `Abducted_Prince` (completati: `Persia_Attacked`, `Lost_In_MountQaf`) |
| Punti vita | 100 (80 base + 20 LifeStone) |
| Cristalli (moneta) | 1.484 |
| Pietre sbloccate | 11, tutte a livello 1 |
| Abilità | 10 (`AirDash`, `BowAim`, `ChakramAim`, `MiniMap`, `Vision`, 4 Focus, `AirDodgeBack`) |
| Potenziamenti | vita 1, spada 1, arco 0, faretra 1, pozioni numero 0, effetto 1 |
| Inventario | 47 voci |
| Viaggi rapidi | 3 |
| Scene salvate | 87 |
| Screenshot | 13 |
