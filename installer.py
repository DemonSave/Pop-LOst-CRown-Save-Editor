#!/usr/bin/env python3
"""Installer per PoPSaveEditor (Windows, per-utente, senza privilegi admin).

Modalita':
    PoPSaveEditor-Setup.exe                 installazione guidata (GUI)
    PoPSaveEditor-Setup.exe /S              installazione silenziosa
    PoPSaveEditor-Setup.exe --uninstall     disinstallazione guidata
    PoPSaveEditor-Setup.exe --uninstall /S  disinstallazione silenziosa

Installa in %LOCALAPPDATA%\\Programs\\PoPSaveEditor, crea la scorciatoia nel
menu Start (opzionale sul desktop) e registra la voce in "App e funzionalita'"
sotto HKCU. I backup dei salvataggi (%LOCALAPPDATA%\\PoPSaveTool) non vengono
mai toccati, ne' dall'installazione ne' dalla disinstallazione.
"""

from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

APP_NAME = "PoP Save Editor"
APP_ID = "PoPSaveEditor"
VERSION = "1.0.0"
PUBLISHER = "PoPSaveEditor"
APP_EXE = "PoPSaveEditor.exe"
UNINST_EXE = "uninstall.exe"
DOC_FILES = ("LEGGIMI.txt", "LEGGIMI.en.txt", "README.md", "README.en.md")
SHORTCUT_NAME = "PoP Save Editor.lnk"

LOCALAPPDATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
PROGRAMS = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming")) / \
    "Microsoft" / "Windows" / "Start Menu" / "Programs"
DESKTOP = Path(os.environ.get("USERPROFILE", Path.home())) / "Desktop"
DEFAULT_DIR = LOCALAPPDATA / "Programs" / APP_ID
UNINST_KEY = rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_ID}"

BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
PAYLOAD = BUNDLE_DIR / "payload"

CREATE_NO_WINDOW = 0x08000000
DETACHED = 0x00000008


# --------------------------------------------------------------------------
# utilita' Windows
# --------------------------------------------------------------------------
def message(text: str, title: str = APP_NAME, error: bool = False) -> None:
    flags = 0x10 if error else 0x40  # MB_ICONERROR / MB_ICONINFORMATION
    ctypes.windll.user32.MessageBoxW(None, text, title, flags)


def powershell(script: str) -> tuple[bool, str]:
    """Esegue uno script PowerShell senza finestra e restituisce (ok, output)."""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-Command", script],
            capture_output=True, text=True, creationflags=CREATE_NO_WINDOW,
        )
        return proc.returncode == 0, (proc.stdout + proc.stderr).strip()
    except OSError as exc:
        return False, str(exc)


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def make_shortcut(lnk: Path, target: Path, workdir: Path, icon: Path | None = None) -> None:
    lnk.parent.mkdir(parents=True, exist_ok=True)
    script = (
        f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut({ps_quote(str(lnk))});"
        f"$s.TargetPath={ps_quote(str(target))};"
        f"$s.WorkingDirectory={ps_quote(str(workdir))};"
        f"$s.IconLocation={ps_quote(str(icon or target) + ',0')};"
        f"$s.Description={ps_quote(APP_NAME)};"
        "$s.Save()"
    )
    ok, out = powershell(script)
    if not ok:
        raise OSError(f"Impossibile creare la scorciatoia {lnk.name}: {out}")


def uninstall_entry(install_dir: Path, size_kb: int) -> str:
    uninst = install_dir / UNINST_EXE
    return (
        f"$path = 'HKCU:\\{UNINST_KEY}';"
        "New-Item -Path $path -Force | Out-Null;"
        f"Set-ItemProperty -Path $path -Name DisplayName -Value {ps_quote(APP_NAME)};"
        f"Set-ItemProperty -Path $path -Name DisplayVersion -Value {ps_quote(VERSION)};"
        f"Set-ItemProperty -Path $path -Name Publisher -Value {ps_quote(PUBLISHER)};"
        f"Set-ItemProperty -Path $path -Name InstallLocation -Value {ps_quote(str(install_dir))};"
        f"Set-ItemProperty -Path $path -Name DisplayIcon -Value {ps_quote(str(install_dir / APP_EXE) + ',0')};"
        f"Set-ItemProperty -Path $path -Name UninstallString -Value {ps_quote(f'\"{uninst}\" --uninstall')};"
        f"Set-ItemProperty -Path $path -Name QuietUninstallString -Value {ps_quote(f'\"{uninst}\" --uninstall /S')};"
        f"Set-ItemProperty -Path $path -Name InstallDate -Value {ps_quote(time.strftime('%Y%m%d'))};"
        f"Set-ItemProperty -Path $path -Name EstimatedSize -Value {size_kb} -Type DWord;"
        "Set-ItemProperty -Path $path -Name NoModify -Value 1 -Type DWord;"
        "Set-ItemProperty -Path $path -Name NoRepair -Value 1 -Type DWord"
    )


def remove_registry() -> None:
    powershell(
        rf"Remove-Item -Path 'HKCU:\{UNINST_KEY}' -Recurse -Force "
        "-ErrorAction SilentlyContinue"
    )


# --------------------------------------------------------------------------
# installazione / disinstallazione
# --------------------------------------------------------------------------
def check_payload() -> Path:
    exe = PAYLOAD / APP_EXE
    if not exe.is_file():
        raise FileNotFoundError(f"Payload mancante: {exe}")
    return exe


def install(install_dir: Path, start_menu: bool, desktop: bool, log=print) -> None:
    payload = check_payload()
    install_dir = install_dir.resolve()
    log(f"Cartella di installazione: {install_dir}")
    install_dir.mkdir(parents=True, exist_ok=True)

    target = install_dir / APP_EXE
    tmp = target.with_suffix(".exe.new")
    shutil.copyfile(payload, tmp)
    try:
        tmp.replace(target)
    except OSError:
        tmp.unlink(missing_ok=True)
        raise OSError("PoPSaveEditor.exe e' in esecuzione: chiudilo e riprova.")
    log("Copiato PoPSaveEditor.exe")

    for doc in DOC_FILES:
        if (PAYLOAD / doc).is_file():
            shutil.copyfile(PAYLOAD / doc, install_dir / doc)
            log(f"Copiato {doc}")

    # l'uninstaller e' una copia di questo stesso setup
    uninst = install_dir / UNINST_EXE
    if Path(sys.executable).resolve() != uninst.resolve():
        tmp = uninst.with_suffix(".exe.new")
        shutil.copyfile(sys.executable, tmp)
        tmp.replace(uninst)
    log("Creato uninstall.exe")

    if start_menu:
        make_shortcut(PROGRAMS / SHORTCUT_NAME, target, install_dir)
        log("Scorciatoia nel menu Start creata")
    if desktop:
        make_shortcut(DESKTOP / SHORTCUT_NAME, target, install_dir)
        log("Scorciatoia sul desktop creata")

    size_kb = sum(f.stat().st_size for f in install_dir.iterdir() if f.is_file()) // 1024
    ok, out = powershell(uninstall_entry(install_dir, size_kb))
    if not ok:
        raise OSError(f"Registrazione in App e funzionalita' fallita: {out}")
    log("Voce aggiunta in App e funzionalita'")
    log("Installazione completata.")


def uninstall(log=print) -> None:
    # La cartella e' quella dell'uninstaller stesso, non un percorso arbitrario.
    install_dir = Path(sys.executable).resolve().parent
    log(f"Rimozione da: {install_dir}")

    for lnk in (PROGRAMS / SHORTCUT_NAME, DESKTOP / SHORTCUT_NAME):
        try:
            if lnk.is_file():
                lnk.unlink()
                log(f"Rimossa scorciatoia {lnk}")
        except OSError as exc:
            log(f"Avviso: scorciatoia non rimossa ({exc})")

    remove_registry()
    log("Voce rimossa da App e funzionalita'")

    # Rimuove solo i file installati; la cartella resta se contiene altro.
    for name in (APP_EXE, UNINST_EXE, *DOC_FILES):
        f = install_dir / name
        try:
            if f.is_file():
                f.unlink()
        except OSError as exc:
            log(f"Avviso: {name} non rimosso ({exc})")

    log("I tuoi backup dei salvataggi in %LOCALAPPDATA%\\PoPSaveTool non sono stati toccati.")
    # L'uninstaller non puo' cancellarsi da solo: uno script in %TEMP% attende
    # che il processo esca, ritenta la cancellazione e rimuove la cartella se vuota.
    temp = Path(tempfile.gettempdir())
    bat = temp / f"popsave_cleanup_{os.getpid()}.bat"
    uninst = install_dir / UNINST_EXE
    try:
        bat.write_text(
            "@echo off\r\n"
            "for /l %%i in (1,1,30) do (\r\n"
            f"  del /f /q \"{uninst}\" >nul 2>&1\r\n"
            f"  if not exist \"{uninst}\" goto folder\r\n"
            "  ping -n 2 127.0.0.1 >nul\r\n"
            ")\r\n"
            ":folder\r\n"
            f"rmdir \"{install_dir}\" >nul 2>&1\r\n"
            "(goto) 2>nul & del /f /q \"%~f0\" >nul 2>&1\r\n",
            encoding="ascii", errors="replace",
        )
        subprocess.Popen(["cmd", "/c", str(bat)], creationflags=CREATE_NO_WINDOW | DETACHED,
                         close_fds=True, cwd=str(temp))
    except OSError as exc:
        log(f"Avviso: pulizia automatica non avviata ({exc})")
    log("Disinstallazione completata.")


# --------------------------------------------------------------------------
# interfaccia grafica
# --------------------------------------------------------------------------
def gui_install() -> None:
    import tkinter as tk
    from tkinter import filedialog, ttk

    root = tk.Tk()
    root.title(f"{APP_NAME} {VERSION} - Installazione")
    root.resizable(False, False)
    try:
        root.iconbitmap(default=str(PAYLOAD / APP_EXE))
    except tk.TclError:
        pass

    pad = {"padx": 18, "pady": (0, 10)}
    tk.Label(root, text=APP_NAME, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(16, 0))
    tk.Label(root, text=f"Versione {VERSION} - installer per-utente, senza privilegi di amministratore.",
             fg="#444").pack(anchor="w", padx=18, pady=(2, 12))

    box = tk.Frame(root)
    box.pack(fill="x", **pad)
    tk.Label(box, text="Cartella di installazione:").pack(anchor="w")
    row = tk.Frame(box)
    row.pack(fill="x", pady=(4, 0))
    dest = tk.StringVar(value=str(DEFAULT_DIR))
    entry = tk.Entry(row, textvariable=dest, width=64)
    entry.pack(side="left", fill="x", expand=True)

    def browse() -> None:
        chosen = filedialog.askdirectory(initialdir=str(DEFAULT_DIR), title="Scegli la cartella")
        if chosen:
            dest.set(chosen)

    tk.Button(row, text="Sfoglia...", command=browse).pack(side="left", padx=(6, 0))

    start_var = tk.BooleanVar(value=True)
    desk_var = tk.BooleanVar(value=False)
    tk.Checkbutton(box, text="Crea la scorciatoia nel menu Start", variable=start_var)\
        .pack(anchor="w", pady=(10, 0))
    tk.Checkbutton(box, text="Crea anche un collegamento sul desktop", variable=desk_var)\
        .pack(anchor="w", pady=(2, 0))
    tk.Label(box, text="I backup dei salvataggi in %LOCALAPPDATA%\\PoPSaveTool non vengono toccati.",
             fg="#666").pack(anchor="w", pady=(10, 0))

    logbox = tk.Text(root, height=9, width=86, state="disabled", bg="#111", fg="#ddd",
                     font=("Consolas", 9), relief="flat")
    logbox.pack(fill="both", padx=18, pady=(4, 12))

    def log(msg: str) -> None:
        logbox.configure(state="normal")
        logbox.insert("end", msg + "\n")
        logbox.see("end")
        logbox.configure(state="disabled")

    buttons = tk.Frame(root)
    buttons.pack(fill="x", padx=18, pady=(0, 16))
    install_btn = tk.Button(buttons, text="Installa", width=14)
    install_btn.pack(side="right")
    tk.Button(buttons, text="Annulla", width=10, command=root.destroy).pack(side="right", padx=(0, 8))
    launch_btn = tk.Button(buttons, text="Avvia PoPSaveEditor", width=18, state="disabled")

    def do_install() -> None:
        target = Path(dest.get().strip())
        if not target.is_absolute():
            message("Indica un percorso assoluto per la cartella di installazione.", error=True)
            return
        install_btn.configure(state="disabled")
        for child in buttons.winfo_children():
            if isinstance(child, tk.Button) and child.cget("text") == "Annulla":
                child.configure(state="disabled")

        def worker() -> None:
            try:
                install(target, start_var.get(), desk_var.get(), log)
            except Exception as exc:  # mostra l'errore all'utente
                root.after(0, lambda: (message(f"Installazione non riuscita:\n\n{exc}", error=True),
                                       install_btn.configure(state="normal")))
                return

            def done() -> None:
                install_btn.pack_forget()
                launch_btn.pack(side="right")
                launch_btn.configure(state="normal",
                                     command=lambda: launch(target / APP_EXE))
                log("Premi 'Avvia PoPSaveEditor' o 'Chiudi'.")

            root.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    install_btn.configure(command=do_install)
    root.mainloop()


def launch(exe: Path) -> None:
    if exe.is_file():
        subprocess.Popen([str(exe)], cwd=str(exe.parent), close_fds=True)


def gui_uninstall() -> None:
    import tkinter as tk

    root = tk.Tk()
    root.title(f"{APP_NAME} - Disinstallazione")
    root.resizable(False, False)
    tk.Label(root, text=f"Rimuovere {APP_NAME}?", font=("Segoe UI", 14, "bold"))\
        .pack(anchor="w", padx=18, pady=(16, 6))
    tk.Label(root, justify="left", text=(
        "Verranno rimossi il programma, la scorciatoia del menu Start e la voce\n"
        "in 'App e funzionalita'.\n\n"
        "I salvataggi del gioco e i backup in %LOCALAPPDATA%\\PoPSaveTool\n"
        "resteranno intatti."
    )).pack(anchor="w", padx=18, pady=(0, 12))

    logbox = tk.Text(root, height=6, width=72, state="disabled", bg="#111", fg="#ddd",
                     font=("Consolas", 9), relief="flat")
    logbox.pack(fill="both", padx=18, pady=(0, 12))

    def log(msg: str) -> None:
        logbox.configure(state="normal")
        logbox.insert("end", msg + "\n")
        logbox.see("end")
        logbox.configure(state="disabled")

    buttons = tk.Frame(root)
    buttons.pack(fill="x", padx=18, pady=(0, 16))
    rm_btn = tk.Button(buttons, text="Rimuovi", width=14)

    def do_remove() -> None:
        rm_btn.configure(state="disabled")
        def worker() -> None:
            try:
                uninstall(log)
            except Exception as exc:
                root.after(0, lambda: (message(f"Disinstallazione non riuscita:\n\n{exc}", error=True),
                                       rm_btn.configure(state="normal")))
                return
            root.after(0, lambda: (message(f"{APP_NAME} e' stato rimosso."), root.destroy()))
        threading.Thread(target=worker, daemon=True).start()

    rm_btn.configure(command=do_remove)
    rm_btn.pack(side="right")
    tk.Button(buttons, text="Annulla", width=10, command=root.destroy).pack(side="right", padx=(0, 8))
    root.mainloop()


# --------------------------------------------------------------------------
def main() -> int:
    argv = [a.lower() for a in sys.argv[1:]]
    silent = "/s" in argv or "--silent" in argv
    uninstall_mode = "--uninstall" in argv

    try:
        if uninstall_mode:
            if silent:
                uninstall(lambda msg: None)
            else:
                gui_uninstall()
        else:
            if silent:
                install(DEFAULT_DIR, start_menu=True, desktop=False, log=lambda msg: None)
                print(f"{APP_NAME} {VERSION} installato in: {DEFAULT_DIR}")
            else:
                gui_install()
    except Exception as exc:
        if silent:
            print(f"Errore: {exc}", file=sys.stderr)
        else:
            message(str(exc), APP_NAME, error=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
