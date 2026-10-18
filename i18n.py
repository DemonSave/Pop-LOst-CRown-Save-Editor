"""Traduzioni dell'editor (italiano, inglese, tedesco, spagnolo, francese).

Le stringhe sono tuple nell'ordine IT, EN, DE, ES, FR. I testi di gioco
(nomi degli oggetti, codici dei livelli) non vengono tradotti.
"""

from __future__ import annotations

LANGS = [("it", "Italiano"), ("en", "English"), ("de", "Deutsch"),
         ("es", "Español"), ("fr", "Français")]
DEFAULT_LANG = "it"
_ORDER = ["it", "en", "de", "es", "fr"]

S = {
    # -- interfaccia fissa -------------------------------------------------
    "ui.loading": ("Caricamento...", "Loading...", "Wird geladen...", "Cargando...", "Chargement..."),
    "ui.tab.overview": ("Panoramica", "Overview", "Übersicht", "Resumen", "Aperçu"),
    "ui.tab.edit": ("Modifica", "Edit", "Bearbeiten", "Editar", "Modifier"),
    "ui.tab.shots": ("Screenshot", "Screenshots", "Screenshots", "Capturas", "Captures"),
    "ui.tab.raw": ("JSON", "JSON", "JSON", "JSON", "JSON"),
    "ui.tab.backup": ("Backup", "Backups", "Backups", "Copias", "Sauvegardes"),
    "ui.language": ("Lingua", "Language", "Sprache", "Idioma", "Langue"),
    "ui.banner.close": (
        "Chiudi il gioco prima di applicare le modifiche. Viene creato un backup automatico a ogni salvataggio. "
        "Qui sopra puoi cambiare la cartella dei salvataggi.",
        "Close the game before applying changes. A backup is created automatically on every save. "
        "You can change the save folder above.",
        "Schließe das Spiel, bevor du Änderungen anwendest. Bei jedem Speichern wird automatisch ein Backup erstellt. "
        "Oben kannst du den Speicherordner ändern.",
        "Cierra el juego antes de aplicar los cambios. Se crea una copia de seguridad automática en cada guardado. "
        "Arriba puedes cambiar la carpeta de guardado.",
        "Ferme le jeu avant d'appliquer les modifications. Une sauvegarde est créée automatiquement à chaque "
        "enregistrement. Tu peux changer le dossier de sauvegarde ci-dessus."),
    "ui.hint.gzip": (
        "I file sono compressi con gzip e contengono JSON: nessuna crittografia. Ogni modifica crea prima un backup automatico.",
        "Files are gzip-compressed JSON: no encryption. Every change creates an automatic backup first.",
        "Die Dateien sind gzip-komprimiertes JSON: keine Verschlüsselung. Jede Änderung erstellt zuerst ein Backup.",
        "Los archivos son JSON comprimido con gzip: sin cifrado. Cada cambio crea antes una copia de seguridad.",
        "Les fichiers sont du JSON compressé en gzip : aucun chiffrement. Chaque modification crée d'abord une sauvegarde."),
    "ui.rows": ("{n} voci", "{n} items", "{n} Einträge", "{n} elementos", "{n} éléments"),
    # -- selettore cartella ------------------------------------------------
    "ui.savepick.title": ("Cartella dei salvataggi", "Save folder", "Speicherordner", "Carpeta de guardado",
                          "Dossier de sauvegarde"),
    "ui.savepick.help": ("Dove sono?", "Where are they?", "Wo sind sie?", "¿Dónde están?", "Où sont-ils ?"),
    "ui.savepick.open": ("Apri", "Open", "Öffnen", "Abrir", "Ouvrir"),
    "ui.savepick.browse": ("Sfoglia...", "Browse...", "Durchsuchen...", "Examinar...", "Parcourir..."),
    "ui.savepick.none": ("Nessun salvataggio trovato", "No saves found", "Keine Spielstände gefunden",
                         "No se encontraron partidas", "Aucune sauvegarde trouvée"),
    "ui.savepick.select": ("Salvataggi trovati", "Found saves", "Gefundene Spielstände", "Partidas encontradas",
                           "Sauvegardes trouvées"),
    "ui.savepick.intro": (
        "I salvataggi stanno in <code>Documenti\\My Games\\Prince Of Persia The Lost Crown\\&lt;profilo&gt;\\Saves\\SaveSlot&lt;N&gt;\\Save_&lt;numero&gt;\\</code> e il file principale si chiama <code>PopSaveGameSlot&lt;N&gt;Index0.AlkSave</code>.",
        "Saves live in <code>Documents\\My Games\\Prince Of Persia The Lost Crown\\&lt;profile&gt;\\Saves\\SaveSlot&lt;N&gt;\\Save_&lt;number&gt;\\</code> and the main file is <code>PopSaveGameSlot&lt;N&gt;Index0.AlkSave</code>.",
        "Spielstände liegen in <code>Dokumente\\My Games\\Prince Of Persia The Lost Crown\\&lt;Profil&gt;\\Saves\\SaveSlot&lt;N&gt;\\Save_&lt;Nummer&gt;\\</code>; die Hauptdatei heißt <code>PopSaveGameSlot&lt;N&gt;Index0.AlkSave</code>.",
        "Las partidas están en <code>Documentos\\My Games\\Prince Of Persia The Lost Crown\\&lt;perfil&gt;\\Saves\\SaveSlot&lt;N&gt;\\Save_&lt;número&gt;\\</code> y el archivo principal es <code>PopSaveGameSlot&lt;N&gt;Index0.AlkSave</code>.",
        "Les sauvegardes se trouvent dans <code>Documents\\My Games\\Prince Of Persia The Lost Crown\\&lt;profil&gt;\\Saves\\SaveSlot&lt;N&gt;\\Save_&lt;numéro&gt;\\</code> et le fichier principal est <code>PopSaveGameSlot&lt;N&gt;Index0.AlkSave</code>."),
    "ui.savepick.oneDrive": (
        "Se OneDrive sincronizza Documenti, il percorso inizia con <code>OneDrive\\DOCUMENTI</code>; il pulsante <strong>Sfoglia...</strong> apre la finestra di Windows per cercarla.",
        "If OneDrive syncs Documents, the path starts with <code>OneDrive\\DOCUMENTS</code>; <strong>Browse...</strong> opens the Windows folder picker.",
        "Wenn OneDrive den Ordner Dokumente synchronisiert, beginnt der Pfad mit <code>OneDrive\\DOKUMENTE</code>; <strong>Durchsuchen...</strong> öffnet den Windows-Ordnerdialog.",
        "Si OneDrive sincroniza Documentos, la ruta empieza por <code>OneDrive\\DOCUMENTOS</code>; <strong>Examinar...</strong> abre el selector de carpetas de Windows.",
        "Si OneDrive synchronise Documents, le chemin commence par <code>OneDrive\\DOCUMENTS</code> ; <strong>Parcourir...</strong> ouvre le sélecteur de dossiers Windows."),
    "ui.savepick.pick": (
        "Puoi scegliere la cartella <code>Save_...</code>, il <code>SaveSlotN</code> o l'intera cartella del profilo: se ci sono piu' salvataggi viene usato il piu' recente.",
        "You can pick the <code>Save_...</code> folder, the <code>SaveSlotN</code> or the whole profile folder: if there are several saves, the newest is used.",
        "Du kannst den Ordner <code>Save_...</code>, den <code>SaveSlotN</code> oder den gesamten Profilordner wählen; bei mehreren Spielständen wird der neueste verwendet.",
        "Puedes elegir la carpeta <code>Save_...</code>, el <code>SaveSlotN</code> o la carpeta del perfil: si hay varias partidas se usa la más reciente.",
        "Tu peux choisir le dossier <code>Save_...</code>, le <code>SaveSlotN</code> ou le dossier du profil : s'il y a plusieurs sauvegardes, la plus récente est utilisée."),
    "ui.savepick.cloud": (
        "Con i salvataggi cloud di Ubisoft/Steam attivi, disattiva la sincronizzazione per questo gioco mentre modifichi, per non farti sovrascrivere le modifiche.",
        "With Ubisoft/Steam cloud saves enabled, turn off syncing for this game while editing so your changes are not overwritten.",
        "Deaktiviere bei aktiven Ubisoft/Steam-Cloud-Speicherständen die Synchronisierung für dieses Spiel, damit deine Änderungen nicht überschrieben werden.",
        "Con las partidas en la nube de Ubisoft/Steam activas, desactiva la sincronización de este juego mientras editas para que no se sobrescriban los cambios.",
        "Avec les sauvegardes cloud Ubisoft/Steam activées, désactive la synchronisation de ce jeu pendant les modifications pour éviter tout écrasement."),
    "ui.savepick.remember": (
        "La scelta viene ricordata e riproposta al prossimo avvio.",
        "Your choice is remembered and restored next time.",
        "Die Auswahl wird gespeichert und beim nächsten Start wieder vorgeschlagen.",
        "La elección se recuerda y se propone la próxima vez.",
        "Le choix est mémorisé et reproposé au prochain démarrage."),
    "ui.savepick.choose_dialog": (
        "Scegli la cartella nella finestra di Windows (puo' aprirsi dietro al browser).",
        "Pick the folder in the Windows dialog (it may open behind the browser).",
        "Wähle den Ordner im Windows-Dialog (er kann hinter dem Browser erscheinen).",
        "Elige la carpeta en la ventana de Windows (puede abrirse detrás del navegador).",
        "Choisis le dossier dans la fenêtre Windows (elle peut s'ouvrir derrière le navigateur)."),
    "ui.toast.folder": ("Cartella attiva: {path}", "Active folder: {path}", "Aktiver Ordner: {path}",
                        "Carpeta activa: {path}", "Dossier actif : {path}"),
    "ui.err.open_folder": ("Impossibile aprire la cartella: {msg}", "Cannot open the folder: {msg}",
                           "Ordner kann nicht geöffnet werden: {msg}", "No se puede abrir la carpeta: {msg}",
                           "Impossible d'ouvrir le dossier : {msg}"),
    "ui.err.selection": ("Selezione non riuscita: {msg}", "Selection failed: {msg}", "Auswahl fehlgeschlagen: {msg}",
                         "Error al seleccionar: {msg}", "Échec de la sélection : {msg}"),
    # -- riepilogo ---------------------------------------------------------
    "summary.folder": ("Cartella", "Folder", "Ordner", "Carpeta", "Dossier"),
    "summary.level": ("Livello attuale", "Current level", "Aktuelles Level", "Nivel actual", "Niveau actuel"),
    "summary.date": ("Data salvataggio", "Save date", "Speicherdatum", "Fecha de guardado", "Date de sauvegarde"),
    "summary.playtime": ("Tempo di gioco", "Playtime", "Spielzeit", "Tiempo de juego", "Temps de jeu"),
    "summary.completion": ("Completamento", "Completion", "Fortschritt", "Progreso", "Progression"),
    "summary.stage": ("Capitolo / stage", "Chapter / stage", "Kapitel / Stage", "Capítulo / fase", "Chapitre / stage"),
    "summary.completed": ("Game completato", "Game completed", "Spiel abgeschlossen", "Juego completado", "Jeu terminé"),
    "summary.hp": ("Punti vita", "Health", "Lebenspunkte", "Puntos de vida", "Points de vie"),
    "summary.crystals": ("Cristalli (moneta)", "Crystals (currency)", "Kristalle (Währung)", "Cristales (moneda)",
                         "Cristaux (monnaie)"),
    "summary.stones": ("Pietre della Conoscenza", "Stones of Knowledge", "Steine des Wissens", "Piedras del Saber",
                       "Pierres du Savoir"),
    "summary.abilities": ("Abilita' sbloccate", "Unlocked abilities", "Freigeschaltete Fähigkeiten",
                          "Habilidades desbloqueadas", "Capacités débloquées"),
    "summary.upgrades": ("Potenziamenti", "Upgrades", "Verbesserungen", "Mejoras", "Améliorations"),
    "summary.items": ("Oggetti in inventario", "Inventory items", "Inventargegenstände", "Objetos en inventario",
                      "Objets d'inventaire"),
    "summary.screenshots": ("Screenshot", "Screenshots", "Screenshots", "Capturas", "Captures"),
    "summary.yes": ("si", "yes", "ja", "sí", "oui"),
    "summary.no": ("no", "no", "nein", "no", "non"),
    "summary.hp_value": ("{hp} (base {base} + vita {bonus})", "{hp} (base {base} + life {bonus})",
                         "{hp} (Basis {base} + Leben {bonus})", "{hp} (base {base} + vida {bonus})",
                         "{hp} (base {base} + vie {bonus})"),
    "summary.stones_value": ("{n} sbloccate", "{n} unlocked", "{n} freigeschaltet", "{n} desbloqueadas",
                             "{n} débloquées"),
    "summary.upgrades_value": ("vita {h}, spada {s}, arco {b}, faretra {q}", "health {h}, sword {s}, bow {b}, quiver {q}",
                               "Leben {h}, Schwert {s}, Bogen {b}, Köcher {q}", "vida {h}, espada {s}, arco {b}, carcaj {q}",
                               "vie {h}, épée {s}, arc {b}, carquois {q}"),
    # -- sezioni e campi ---------------------------------------------------
    "section.progression": ("Progressione", "Progression", "Fortschritt", "Progreso", "Progression"),
    "section.character": ("Personaggio", "Character", "Charakter", "Personaje", "Personnage"),
    "section.upgrades": ("Potenziamenti", "Upgrades", "Verbesserungen", "Mejoras", "Améliorations"),
    "section.stones": ("Livello Pietre", "Stone levels", "Stein-Level", "Nivel de piedras", "Niveau des pierres"),
    "section.inventory": ("Inventario", "Inventory", "Inventar", "Inventario", "Inventaire"),
    "section.options": ("Opzioni di gioco", "Game options", "Spieloptionen", "Opciones de juego", "Options du jeu"),
    "field.playtime": ("Tempo di gioco", "Playtime", "Spielzeit", "Tiempo de juego", "Temps de jeu"),
    "field.playtime.help": (
        "Formato ore:minuti:secondi. Il gioco mostra questo valore nel menu.",
        "Hours:minutes:seconds. The game shows this value in the menu.",
        "Stunden:Minuten:Sekunden. Das Spiel zeigt diesen Wert im Menü.",
        "Horas:minutos:segundos. El juego muestra este valor en el menú.",
        "Heures:minutes:secondes. Le jeu affiche cette valeur dans le menu."),
    "field.completion": ("Completamento (%)", "Completion (%)", "Fortschritt (%)", "Progreso (%)", "Progression (%)"),
    "field.completion.help": (
        "Percentuale di completamento mostrata sul salvataggio.",
        "Completion percentage shown on the save.",
        "Im Spielstand angezeigter Fortschritt in Prozent.",
        "Porcentaje de progreso mostrado en la partida.",
        "Pourcentage de progression affiché dans la sauvegarde."),
    "field.game_completed": ("Gioco completato", "Game completed", "Spiel abgeschlossen", "Juego completado",
                             "Jeu terminé"),
    "field.quest": ("Avanzamento quest", "Quest progress", "Quest-Fortschritt", "Progreso de misión",
                    "Avancement des quêtes"),
    "field.hp": ("Punti vita attuali", "Current health", "Aktuelle Lebenspunkte", "Puntos de vida actuales",
                 "Points de vie actuels"),
    "field.hp.help": ("Valore mostrato nella barra della vita.", "Value shown in the health bar.",
                      "Wert in der Lebensleiste.", "Valor mostrado en la barra de vida.",
                      "Valeur affichée dans la barre de vie."),
    "field.hp_nobonus": ("Vita senza bonus LifeStone", "Health without LifeStone bonus",
                         "Leben ohne LifeStone-Bonus", "Vida sin bonus LifeStone", "Vie sans bonus LifeStone"),
    "field.hp_bonus": ("Bonus vita (LifeStone)", "Health bonus (LifeStone)", "Lebensbonus (LifeStone)",
                       "Bonus de vida (LifeStone)", "Bonus de vie (LifeStone)"),
    "field.focus1": ("Abilita' Focus 1", "Focus ability 1", "Fokus-Fähigkeit 1", "Habilidad de enfoque 1",
                     "Capacité Focus 1"),
    "field.focus2": ("Abilita' Focus 2", "Focus ability 2", "Fokus-Fähigkeit 2", "Habilidad de enfoque 2",
                     "Capacité Focus 2"),
    "field.abilities": ("Abilita' sbloccate", "Unlocked abilities", "Freigeschaltete Fähigkeiten",
                        "Habilidades desbloqueadas", "Capacités débloquées"),
    "field.abilities.help": (
        "Elenco separato da virgole, es. AirDash, BowAim, MiniMap.",
        "Comma-separated list, e.g. AirDash, BowAim, MiniMap.",
        "Kommagetrennte Liste, z. B. AirDash, BowAim, MiniMap.",
        "Lista separada por comas, p. ej. AirDash, BowAim, MiniMap.",
        "Liste séparée par des virgules, par ex. AirDash, BowAim, MiniMap."),
    "field.stones": ("Pietre sbloccate", "Unlocked stones", "Freigeschaltete Steine", "Piedras desbloqueadas",
                     "Pierres débloquées"),
    "field.stones_equipped": ("Pietre equipaggiate", "Equipped stones", "Ausgerüstete Steine", "Piedras equipadas",
                              "Pierres équipées"),
    "field.stone_slots": ("Slot Pietre", "Stone slots", "Steinplätze", "Ranuras de piedras", "Emplacements de pierres"),
    "field.crystals": ("Cristalli del tempo", "Time crystals", "Zeitkristalle", "Cristales del tiempo",
                       "Cristaux du temps"),
    "field.crystals.help": ("La moneta del gioco (Crystal).", "The game currency (Crystal).",
                            "Die Spielwährung (Crystal).", "La moneda del juego (Crystal).",
                            "La monnaie du jeu (Crystal)."),
    "field.health": ("Vita", "Health", "Leben", "Vida", "Vie"),
    "field.sword": ("Spada", "Sword", "Schwert", "Espada", "Épée"),
    "field.bow": ("Arco", "Bow", "Bogen", "Arco", "Arc"),
    "field.quiver": ("Faretra", "Quiver", "Köcher", "Carcaj", "Carquois"),
    "field.potions": ("Numero pozioni", "Potion count", "Anzahl Tränke", "Número de pociones", "Nombre de potions"),
    "field.potion_effect": ("Effetto pozioni", "Potion effect", "Trankwirkung", "Efecto de pociones",
                            "Effet des potions"),
    "field.health_dlc": ("Vita (DLC)", "Health (DLC)", "Leben (DLC)", "Vida (DLC)", "Vie (DLC)"),
    "field.upgrade.help": ("Livello del potenziamento (0 = base, 4 = massimo).",
                           "Upgrade level (0 = base, 4 = max).",
                           "Verbesserungsstufe (0 = Basis, 4 = Maximum).",
                           "Nivel de mejora (0 = base, 4 = máximo).",
                           "Niveau d'amélioration (0 = base, 4 = maximum)."),
    "field.stone": ("Pietra {n}", "Stone {n}", "Stein {n}", "Piedra {n}", "Pierre {n}"),
    "field.option": ("Opzione {n} ({kind})", "Option {n} ({kind})", "Option {n} ({kind})", "Opción {n} ({kind})",
                     "Option {n} ({kind})"),
    "field.integer": ("intero", "integer", "Ganzzahl", "entero", "entier"),
    "field.decimal": ("decimale", "decimal", "Dezimalzahl", "decimal", "décimal"),
    "options.note": (
        "Il gioco salva le opzioni come coppie id/valore senza nome. Modificale solo se sai cosa stai cambiando.",
        "The game stores options as unnamed id/value pairs. Change them only if you know what you are doing.",
        "Das Spiel speichert Optionen als namenlose ID/Wert-Paare. Ändere sie nur, wenn du weißt, was du tust.",
        "El juego guarda las opciones como pares id/valor sin nombre. Cámbialas solo si sabes lo que haces.",
        "Le jeu enregistre les options sous forme de paires id/valeur sans nom. Ne les modifie que si tu sais faire."),
    # -- tabelle -----------------------------------------------------------
    "world.travel": ("Viaggi rapidi (Wak-Wak)", "Fast travels (Wak-Wak)", "Schnellreisen (Wak-Wak)",
                     "Viajes rápidos (Wak-Wak)", "Voyages rapides (Wak-Wak)"),
    "world.travel.count": ("{done}/{total} sbloccati", "{done}/{total} unlocked", "{done}/{total} freigeschaltet",
                           "{done}/{total} desbloqueados", "{done}/{total} débloqués"),
    "world.header.point": ("Punto", "Point", "Punkt", "Punto", "Point"),
    "world.header.region": ("Regione", "Region", "Region", "Región", "Région"),
    "world.header.level": ("Livello", "Level", "Level", "Nivel", "Niveau"),
    "world.header.status": ("Stato", "Status", "Status", "Estado", "État"),
    "world.header.lesson": ("Lezione", "Lesson", "Lektion", "Lección", "Leçon"),
    "world.header.code": ("Codice", "Code", "Code", "Código", "Code"),
    "world.challenge": ("Sfide del tempio (lezioni di Artaban)", "Temple challenges (Artaban lessons)",
                        "Tempelprüfungen (Artaban-Lektionen)", "Desafíos del templo (lecciones de Artaban)",
                        "Défis du temple (leçons d'Artaban)"),
    "world.challenge.count": ("{done}/{total} completate", "{done}/{total} completed", "{done}/{total} abgeschlossen",
                              "{done}/{total} completadas", "{done}/{total} terminées"),
    "world.unlocked": ("sbloccato", "unlocked", "freigeschaltet", "desbloqueado", "débloqué"),
    "world.locked": ("bloccato", "locked", "gesperrt", "bloqueado", "verrouillé"),
    "world.completed": ("completata", "completed", "abgeschlossen", "completada", "terminée"),
    "world.challenge_locked": ("bloccata", "locked", "gesperrt", "bloqueada", "verrouillée"),
    "world.map": ("Mappa: {maps} aree, {layers} settori, {cells} celle (2 bit per cella).",
                  "Map: {maps} areas, {layers} sectors, {cells} cells (2 bits per cell).",
                  "Karte: {maps} Gebiete, {layers} Sektoren, {cells} Zellen (2 Bit pro Zelle).",
                  "Mapa: {maps} áreas, {layers} sectores, {cells} celdas (2 bits por celda).",
                  "Carte : {maps} zones, {layers} secteurs, {cells} cellules (2 bits par cellule)."),
    "table.item": ("Oggetto", "Item", "Gegenstand", "Objeto", "Objet"),
    "table.option": ("Opzione", "Option", "Option", "Opción", "Option"),
    "table.value": ("Valore", "Value", "Wert", "Valor", "Valeur"),
    "table.search": ("Cerca...", "Search...", "Suchen...", "Buscar...", "Rechercher..."),
    # -- screenshot, raw, backup ------------------------------------------
    "shots.none": ("Nessuno screenshot in questo salvataggio.", "No screenshots in this save.",
                   "Keine Screenshots in diesem Spielstand.", "No hay capturas en esta partida.",
                   "Aucune capture dans cette sauvegarde."),
    "raw.document": ("Documento", "Document", "Dokument", "Documento", "Document"),
    "raw.load": ("Carica", "Load", "Laden", "Cargar", "Charger"),
    "raw.apply": ("Applica JSON", "Apply JSON", "JSON anwenden", "Aplicar JSON", "Appliquer le JSON"),
    "raw.hint": (
        "Modifica diretta del JSON interno. Usa indentazione qualsiasi: viene ricompattato automaticamente. Se il JSON non e' valido il file non viene toccato.",
        "Direct edit of the inner JSON. Any indentation is fine: it is recompacted automatically. If the JSON is invalid the file is left untouched.",
        "Direkte Bearbeitung des inneren JSON. Beliebige Einrückung wird automatisch komprimiert. Bei ungültigem JSON bleibt die Datei unverändert.",
        "Edición directa del JSON interno. Cualquier sangría se compacta automáticamente. Si el JSON no es válido, el archivo no se toca.",
        "Modification directe du JSON interne. L'indentation est recompactée automatiquement. Si le JSON est invalide, le fichier n'est pas touché."),
    "raw.placeholder": ("Seleziona un documento e premi Carica", "Select a document and press Load",
                        "Dokument auswählen und Laden drücken", "Selecciona un documento y pulsa Cargar",
                        "Sélectionne un document et clique sur Charger"),
    "raw.confirm": ("Riscrivere il documento con questo JSON?", "Rewrite the document with this JSON?",
                    "Dokument mit diesem JSON überschreiben?", "¿Reescribir el documento con este JSON?",
                    "Réécrire le document avec ce JSON ?"),
    "toast.json_loaded": ("JSON caricato.", "JSON loaded.", "JSON geladen.", "JSON cargado.", "JSON chargé."),
    "toast.rewritten": ("Documento riscritto.", "Document rewritten.", "Dokument überschrieben.",
                        "Documento reescrito.", "Document réécrit."),
    "err.json_invalid": ("JSON non valido: {msg}", "Invalid JSON: {msg}", "Ungültiges JSON: {msg}",
                         "JSON no válido: {msg}", "JSON invalide : {msg}"),
    "backup.hint": (
        "I backup sono salvati fuori dalla cartella del gioco. Il ripristino crea a sua volta un backup dello stato attuale.",
        "Backups are stored outside the game folder. Restoring creates another backup of the current state first.",
        "Backups liegen außerhalb des Spielordners. Beim Wiederherstellen wird zuerst der aktuelle Zustand gesichert.",
        "Las copias se guardan fuera de la carpeta del juego. Al restaurar se crea antes otra copia del estado actual.",
        "Les sauvegardes sont stockées hors du dossier du jeu. La restauration crée d'abord une sauvegarde de l'état actuel."),
    "backup.none": ("Nessun backup per questo salvataggio.", "No backups for this save.",
                    "Keine Backups für diesen Spielstand.", "No hay copias para esta partida.",
                    "Aucune sauvegarde pour cette partie."),
    "backup.restore": ("Ripristina", "Restore", "Wiederherstellen", "Restaurar", "Restaurer"),
    "backup.confirm": (
        "Ripristinare {name}? Lo stato attuale verra' salvato in un nuovo backup.",
        "Restore {name}? The current state will be saved in a new backup.",
        "{name} wiederherstellen? Der aktuelle Zustand wird in einem neuen Backup gesichert.",
        "¿Restaurar {name}? El estado actual se guardará en una nueva copia.",
        "Restaurer {name} ? L'état actuel sera enregistré dans une nouvelle sauvegarde."),
    "toast.restored": ("Backup ripristinato.", "Backup restored.", "Backup wiederhergestellt.",
                       "Copia restaurada.", "Sauvegarde restaurée."),
    # -- barra applica -----------------------------------------------------
    "footer.nochanges": ("Nessuna modifica", "No changes", "Keine Änderungen", "Sin cambios", "Aucune modification"),
    "footer.changes_one": ("<strong>1</strong> modifica non applicata", "<strong>1</strong> pending change",
                           "<strong>1</strong> ausstehende Änderung", "<strong>1</strong> cambio pendiente",
                           "<strong>1</strong> modification en attente"),
    "footer.changes_many": ("<strong>{n}</strong> modifiche non applicate", "<strong>{n}</strong> pending changes",
                            "<strong>{n}</strong> ausstehende Änderungen", "<strong>{n}</strong> cambios pendientes",
                            "<strong>{n}</strong> modifications en attente"),
    "footer.reset": ("Annulla modifiche", "Discard changes", "Änderungen verwerfen", "Descartar cambios",
                     "Annuler les modifications"),
    "footer.apply": ("Applica", "Apply", "Anwenden", "Aplicar", "Appliquer"),
    "toast.saved": ("Salvate {n} modifiche. Backup: {backup}", "Saved {n} changes. Backup: {backup}",
                    "{n} Änderungen gespeichert. Backup: {backup}", "Guardados {n} cambios. Copia: {backup}",
                    "{n} modifications enregistrées. Sauvegarde : {backup}"),
    "err.generic": ("Errore: {msg}", "Error: {msg}", "Fehler: {msg}", "Error: {msg}", "Erreur : {msg}"),
    "err.http": ("Errore {code}", "Error {code}", "Fehler {code}", "Error {code}", "Erreur {code}"),
    "err.read": ("Impossibile leggere il salvataggio: {msg}", "Cannot read the save: {msg}",
                 "Spielstand kann nicht gelesen werden: {msg}", "No se puede leer la partida: {msg}",
                 "Impossible de lire la sauvegarde : {msg}"),
    # -- errori del server -------------------------------------------------
    "err.notfound": ("non trovato", "not found", "nicht gefunden", "no encontrado", "introuvable"),
    "err.backup": ("backup non trovato", "backup not found", "Backup nicht gefunden", "copia no encontrada",
                   "sauvegarde introuvable"),
    "err.doc": ("documento non disponibile", "document not available", "Dokument nicht verfügbar",
                "documento no disponible", "document indisponible"),
    "err.bad_request": ("richiesta non valida: {msg}", "invalid request: {msg}", "ungültige Anfrage: {msg}",
                        "solicitud no válida: {msg}", "requête invalide : {msg}"),
    "err.too_big": ("richiesta troppo grande", "request too large", "Anfrage zu groß", "solicitud demasiado grande",
                    "requête trop volumineuse"),
    "err.file": ("file mancante", "missing file", "fehlende Datei", "archivo faltante", "fichier manquant"),
    "err.screenshot": ("screenshot non trovato", "screenshot not found", "Screenshot nicht gefunden",
                       "captura no encontrada", "capture introuvable"),
    "err.folder_missing": ("cartella non trovata: {path}", "folder not found: {path}", "Ordner nicht gefunden: {path}",
                           "carpeta no encontrada: {path}", "dossier introuvable : {path}"),
    "err.no_save": ("in questa cartella non c'e' nessun salvataggio (PopSaveGame*.AlkSave)",
                    "no save found in this folder (PopSaveGame*.AlkSave)",
                    "in diesem Ordner wurde kein Spielstand gefunden (PopSaveGame*.AlkSave)",
                    "no hay ninguna partida en esta carpeta (PopSaveGame*.AlkSave)",
                    "aucune sauvegarde dans ce dossier (PopSaveGame*.AlkSave)"),
    "err.multi_save": ("trovati {n} salvataggi: scegli la cartella Save_ specifica",
                       "{n} saves found: pick the specific Save_ folder",
                       "{n} Spielstände gefunden: wähle den passenden Save_-Ordner",
                       "{n} partidas encontradas: elige la carpeta Save_ concreta",
                       "{n} sauvegardes trouvées : choisis le dossier Save_ précis"),
    "err.no_folder": ("nessuna cartella indicata", "no folder given", "kein Ordner angegeben",
                      "no se indicó ninguna carpeta", "aucun dossier indiqué"),
    "log.raw": ("{key}: JSON riscritto ({n} caratteri)", "{key}: JSON rewritten ({n} characters)",
                "{key}: JSON überschrieben ({n} Zeichen)", "{key}: JSON reescrito ({n} caracteres)",
                "{key} : JSON réécrit ({n} caractères)"),
    "picker.title": ("Seleziona la cartella del salvataggio (Save_..., SaveSlot1, ...)",
                     "Select the save folder (Save_..., SaveSlot1, ...)",
                     "Spielstand-Ordner wählen (Save_..., SaveSlot1, ...)",
                     "Selecciona la carpeta de guardado (Save_..., SaveSlot1, ...)",
                     "Choisis le dossier de sauvegarde (Save_..., SaveSlot1, ...)"),
}

LESSON_NAMES = {
    "Standard Attacks": ("Standardangriffe", "Ataques estándar", "Attaques standard"),
    "Launchers": ("Startangriffe", "Lanzamientos", "Lancements"),
    "Aerial Attacks": ("Luftangriffe", "Ataques aéreos", "Attaques aériennes"),
    "Charged Attacks": ("Aufgeladene Angriffe", "Ataques cargados", "Attaques chargées"),
    "Enemies Reactions": ("Gegnerreaktionen", "Reacciones enemigas", "Réactions ennemies"),
    "Defensive Options": ("Defensive Optionen", "Opciones defensivas", "Options défensives"),
    "Advanced Movements": ("Fortgeschrittene Bewegungen", "Movimientos avanzados", "Déplacements avancés"),
    "Parry": ("Parieren", "Parada", "Parade"),
    "Athra Surge": ("Athra-Welle", "Onda de Athra", "Onde d'Athra"),
    "Bow & Chakram": ("Bogen & Chakram", "Arco y chakram", "Arc et chakram"),
    "Shadow of the Simurgh": ("Schatten des Simurgh", "Sombra del Simurgh", "Ombre du Simurgh"),
    "Fabric of the World": ("Gewebe der Welt", "Trama del mundo", "Trame du monde"),
    "Rush of the Simurgh": ("Ansturm des Simurgh", "Embestida del Simurgh", "Ruée du Simurgh"),
}

_INDEX = {lang: i for i, lang in enumerate(_ORDER)}


def lesson_name(lang: str | None, name_it: str, name_en: str) -> str:
    """Nome della lezione di Artaban nella lingua scelta."""
    lang = normalize(lang)
    if lang == "it":
        return name_it
    if lang == "en":
        return name_en
    row = LESSON_NAMES.get(name_en)
    if not row:
        return name_en
    return row[{"de": 0, "es": 1, "fr": 2}[lang]]


def normalize(lang: str | None) -> str:
    lang = (lang or "").split("-")[0].split("_")[0].lower()
    return lang if lang in _INDEX else DEFAULT_LANG


def tr(lang: str | None, key: str, **fmt) -> str:
    lang = normalize(lang)
    row = S.get(key)
    if row is None:
        return key
    text = row[_INDEX[lang]] or row[_INDEX["en"]] or row[0]
    try:
        return text.format(**fmt)
    except (KeyError, IndexError):
        return text


SERVER_ONLY = ("summary.", "section.", "field.", "options.", "log.", "picker.")


def ui_strings(lang: str | None) -> dict:
    """Stringhe usate dal JavaScript (chiavi senza il prefisso ui.)."""
    lang = normalize(lang)
    out = {}
    for key, row in S.items():
        if key.startswith(SERVER_ONLY):
            continue
        out[key[3:] if key.startswith("ui.") else key] = row[_INDEX[lang]]
    return out


def lang_choices() -> list[dict]:
    return [{"code": code, "name": name} for code, name in LANGS]
