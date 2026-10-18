# PoP Save Tool — editor per Prince of Persia: The Lost Crown

*Italiano · [English](README.en.md)*

Legge, mostra e **modifica** i salvataggi del gioco (`PopSaveGame*.AlkSave`,
`Progression*.AlkContent`, `GameOptions*.AlkContent`, screenshot).
I file non sono cifrati: sono JSON compressi con gzip (dettagli in
[ANALISI_FORMATO.md](ANALISI_FORMATO.md); versione inglese:
[ANALISI_FORMATO.en.md](ANALISI_FORMATO.en.md)).

Requisiti: **Python 3.8+** (nessuna libreria esterna). L'interfaccia web è
disponibile in italiano, inglese, tedesco, spagnolo e francese.

## Versione eseguibile per Windows

`dist/PoPSaveEditor-win64.zip` contiene l'exe autonomo (nessun Python da
installare) con i README e le guide rapide. Si scompatta ovunque e si fa doppio
clic su `PoPSaveEditor.exe`: parte l'editor web su `127.0.0.1:8765` (porta
successiva se occupata). Da riga di comando funziona allo stesso modo dello
script, es. `PoPSaveEditor.exe info`.

Per ricostruirlo (Windows, Python 3.14 testato):

```bash
python -m pip install pyinstaller
python -m PyInstaller PoPSaveEditor.spec --noconfirm
powershell -Command "Compress-Archive -Path 'dist\PoPSaveEditor-win64\*' -DestinationPath 'dist\PoPSaveEditor-win64.zip' -Force"
```

## Installer Windows

`dist/PoPSaveEditor-Setup.exe` installa l'editor **per l'utente corrente**,
senza privilegi di amministratore:

- cartella predefinita `%LOCALAPPDATA%\Programs\PoPSaveEditor` (modificabile);
- scorciatoia nel menu Start, collegamento sul desktop opzionale;
- voce in **App e funzionalità** di Windows, con disinstallazione;
- l'uninstaller rimuove programma, scorciatoie e voce di registro, ma **non**
tocca i salvataggi del gioco ne' i backup in `%LOCALAPPDATA%\PoPSaveTool`.

Doppio clic per l'installazione guidata. Dalla riga di comando:

```bash
PoPSaveEditor-Setup.exe --silent                 # installazione silenziosa
PoPSaveEditor-Setup.exe --uninstall               # disinstallazione guidata
PoPSaveEditor-Setup.exe --uninstall --silent      # disinstallazione silenziosa
```

`/S` funziona come `--silent` da `cmd.exe` e PowerShell (in Git Bash usare la
forma lunga, che non viene riscritta come percorso). L'exe non è firmato
digitalmente: SmartScreen può chiedere una conferma.

Per ricostruire l'installer (dopo aver ricostruito `dist/PoPSaveEditor.exe` e i
documenti in `dist/PoPSaveEditor-win64`):

```bash
python -m PyInstaller PoPSaveEditor-Setup.spec --noconfirm
```

## Avvio rapido (interfaccia grafica nel browser)

```bash
python popedit.py web
```

Apre `http://127.0.0.1:8765` con:

- **Panoramica** – riepilogo leggibile del salvataggio e scelta della cartella
- **Modifica** – tabelle con nomi leggibili di viaggi rapidi e sfide, più i valori
  modificabili: cristalli, punti vita, potenziamenti, abilità, pietre della
  conoscenza, inventario, opzioni di gioco
- **Screenshot** – le 13 anteprime salvate dal gioco, visualizzabili
- **JSON** – il contenuto grezzo di ogni file, per modifiche libere
- **Backup** – elenco dei backup con ripristino con un clic

La lingua dell'interfaccia si cambia dal selettore nella barra in alto
(Italiano, English, Deutsch, Español, Français); la scelta viene ricordata. I dati
di gioco (nomi degli oggetti, codici dei livelli, nomi delle regioni) non vengono
tradotti.

Il server ascolta solo su `127.0.0.1`, quindi non è raggiungibile dall'esterno.
Chiudi il gioco prima di applicare le modifiche.

## Dove sono i salvataggi (e come sceglierli)

Il gioco salva in Documenti, in una cartella per profilo:

```
Documenti\My Games\Prince Of Persia The Lost Crown\<profilo>\Saves\
    SaveSlot0\Save_<numero>\PopSaveGameSlot0Index0.AlkSave
    SaveSlot1\Save_<numero>\...
    SaveSlot2\Save_<numero>\...
    SaveSlot3\Save_<numero>\...
```

Se OneDrive sincronizza Documenti, il percorso inizia con
`OneDrive\DOCUMENTI` (o `OneDrive\Documents`). Il file principale è
`PopSaveGameSlot<N>Index0.AlkSave`; accanto ci sono `Progression*.AlkContent`,
`GameOptions*.AlkContent` e gli screenshot.

Nella scheda **Panoramica** il riquadro **Cartella dei salvataggi** mostra il
percorso attivo, elenca i salvataggi trovati e permette di:

- aprire un altro salvataggio dal menu a tendina;
- usare **Sfoglia...** per scegliere una cartella con la finestra di Windows
  (accetta la cartella `Save_...`, il `SaveSlotN` o quella del profilo; con più
  salvataggi viene preso il più recente);
- leggere **Dove sono?** con il percorso completo e le note su OneDrive/cloud.

La scelta viene ricordata in `%LOCALAPPDATA%\PoPSaveTool\last_save.txt` e
riproposta al successivo avvio; se la cartella sparisce, il tool torna a quella
indicata dal gioco in `lastSavedFolder.txt`.

Da riga di comando l'elenco si ottiene con `python popedit.py saves`; con
`--save "percorso"` si sceglie una cartella specifica per quel comando.

Attenzione: se usi i salvataggi cloud di Ubisoft/Steam, disattiva la
sincronizzazione per questo gioco mentre modifichi, altrimenti il cloud può
sovrascrivere le modifiche (o viceversa).

## Riga di comando

```bash
python popedit.py info                        # riepilogo del salvataggio più recente
python popedit.py info --save "percorso"      # su un salvataggio specifico
python popedit.py saves                       # elenca i salvataggi e dove sono

python popedit.py extract -o estratti         # JSON leggibili + screenshot .jpg
python popedit.py pack -i estratti            # ricompatta i JSON modificati

python popedit.py set crystals=99999 playtime=2:00:00 completion=75
python popedit.py set hp=500 sword=4 bow=4 quiver=4 stones=3

python popedit.py backups                     # elenca i backup
python popedit.py restore                     # ripristina l'ultimo backup
```

Chiavi accettate da `set`: `crystals` (moneta), `playtime` (`HH:MM:SS` o secondi),
`completion` (percentuale o 0–1), `hp`, `sword`, `bow`, `quiver`, `potion_count`,
`potion_effect`, `health_upgrades`, `stones` (livello di tutte le pietre).

### Azioni rapide: rimosse

Le tre azioni automatiche (`reveal_map`, `unlock_fast_travel`,
`complete_challenges`) **non fanno più parte del progetto**: nei test in gioco il
riempimento forzato delle bitmap della mappa lasciava la mappa bloccata e non più
visibile, e anche gli altri due interventi di massa possono lasciare il
salvataggio in uno stato che il gioco non gradisce.

Ora l'editor **legge** soltanto mappa, viaggi rapidi e sfide (tabelle nella
scheda Modifica) e scrive solo i valori che scegli tu, uno per uno. I nomi
leggibili (regione/livello per i viaggi, nome della lezione per le sfide) vengono
da `popdata.py` (incluso nei sorgenti), estratto dai bundle del gioco.

Se hai usato una versione precedente e la mappa non si vede più, apri la scheda
**Backup** e ripristina il backup creato prima di quell'azione (oppure copia a
mano la cartella del salvataggio che avevi conservato).

Se `--save` è omesso, il tool usa l'ultima cartella indicata dal gioco in
`lastSavedFolder.txt` (per esempio `…\SaveSlot3\Save_134359460918773693`).

## Sicurezza

- **Ogni scrittura crea prima un backup completo** in
  `%LOCALAPPDATA%\PoPSaveTool\backups\<cartella_salvataggio>__<data-ora>`.
- Il ripristino salva a sua volta lo stato attuale, quindi si può sempre tornare indietro.
- La scrittura è atomica (file temporaneo + sostituzione) e aggiorna le
  dimensioni nell'intestazione del contenitore.
- Un file non modificato viene ricompattato **identico** all'originale.

Consiglio: prima di provare, copia a mano la cartella del salvataggio e, se usi
i salvataggi cloud di Ubisoft/Steam, disattiva la sincronizzazione per quel gioco.

## Struttura

```
pop-save-tool/
├─ popsave.py            libreria: lettura/scrittura dei contenitori, backup, patch
├─ popdata.py            dati di gioco estratti (23 viaggi, 13 lezioni)
├─ i18n.py               traduzioni (IT, EN, DE, ES, FR)
├─ popedit.py            interfaccia a riga di comando e server web
├─ installer.py          installer Windows per-utente
├─ web/                  interfaccia web (HTML/CSS/JS)
├─ tests/selfcheck.py    verifica automatica su una copia del salvataggio
├─ estratti/             copia leggibile del salvataggio analizzato (JSON + JPG)
├─ README.en.md          documentazione in inglese
├─ dist/                 exe, zip, installer e guide rapide (LEGGIMI.txt)
├─ ANALISI_FORMATO.md    analisi completa del formato, in italiano
└─ ANALISI_FORMATO.en.md la stessa analisi in inglese
```

Per rieseguire le verifiche: `python tests/selfcheck.py` (lavora su una copia
temporanea, non tocca l'originale). Il test controlla anche che le azioni rapide
non esistano più, che le traduzioni siano complete e che la lettura di mappa,
viaggi rapidi e sfide non scriva nulla nel salvataggio.

`popdata.py` è già incluso: per usare l'editor non servono altre librerie.
Solo per rigenerarlo dai bundle serve `pip install UnityPy` (vedi
`tmp/extract_gamedata.py`).
