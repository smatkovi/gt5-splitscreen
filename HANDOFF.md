# GT5 3P/4P-Splitscreen — Übergabe an Claude Code (ArchBang, ~/gt5re)

Du übernimmst ein laufendes Reverse-Engineering-Projekt von Sebastian. Alles Wissen steht hier
und im Dossier `~/gt5re/doc/gt5-3p-dossier.html` (Text mit `python3 -c` aus dem HTML ziehen oder
im Browser lesen). Lies beides vollständig, bevor du anfängst. Antworte Sebastian auf Deutsch.

## Auftrag (in dieser Reihenfolge)

1. **RPCS3 auf diesem Rechner mit GT5 lauffähig machen** — BCES00569 (EU) mit Update 2.17,
   unserem Adhoc-Script-Mod (PDIPFS) und den RAM-Patches (als RPCS3-Patch, nicht per Hand).
2. **Selbständig bis ins laufende 3-Spieler-Split-Battle-Rennen kommen** — drei Ansichten werden
   gerendert, drei Autos stehen/fahren auf der Strecke. Dazu die Freeze-Ursache des 3-Fenster-
   Patches (win3b/win3c, s. u.) mit dem Emulator-Debugger finden und beheben.
3. **Ergebnis sichern und übergeben**: `~/gt5re/release/3p/` mit
   - `rpcs3-patch.yml` (fertiger Patch-Block für RPCS3),
   - `deploy_3p.sh` (PS3-Hardware-Skript, ps3mapi-Pokes, Muster wie `win3b_deploy.sh`, mit `apply|off|verify`),
   - Mod-Quellen: Diff gegen OpenAdhoc + das gepackte PDIPFS-Verzeichnis (Muster `deploy_mod.sh`),
   - `words.txt`: jede Patch-Adresse mit Original- und Neuwort, capstone-verifiziert,
   - `README.md` (Englisch): was der Patch tut, wie er getestet wurde, Testablauf auf der PS3.
   Dann `git` in `~/gt5re` (initialisieren, falls nicht vorhanden; `.gitignore` für EBOOT/ISOs/
   Dumps), Commit + Tag `3p-v1`, zusätzlich `~/gt5re/release/gt5-3p-release.tar.gz`.
   Sebastian den Pfad nennen und ihm den Hardware-Test auf der PS3 Schritt für Schritt vorgeben
   (Konsole kalt im Hauptmenü, dann Split-Battle mit Spieler 3).
4. **Dasselbe für 4 Spieler** → `~/gt5re/release/4p/`, Tag `4p-v1`. Vier Ansichten (Quadranten),
   vier Autos, vier Controller-Ports (0–3).

## Autonomie-Regeln

- Arbeite selbständig und durchgehend. Unterbrich nur, wenn du physisch etwas von Sebastian
  brauchst: Disc in die PS3 legen, Controller anstecken, Knöpfe auf der Konsole drücken, BIOS.
- Programme installieren darfst du (pacman/yay). Für `sudo` fehlt dir das Passwort: bereite den
  Befehl vollständig vor und bitte Sebastian, ihn in seinem Terminal auszuführen — jeder
  sudo-Befehl in einem eigenen Block, danach neuer Block (sonst verschluckt sein Terminal die
  Folgebefehle). Prüfe vorher mit `sudo -n true`, ob sudo gerade ohne Passwort geht.
- Auf der PS3 (webMAN-FTP/HTTP unter 192.168.1.11) nichts verändern, ohne es vorher zu sagen.
  Die Konsole ist der Referenzstand. Lesen (getmem, FTP-Download) ist jederzeit erlaubt.
- Halte in `~/gt5re/JOURNAL.md` fest, was du getestet hast und was dabei herauskam (Datum,
  Patch-Stand, Ergebnis) — damit nichts doppelt gemessen wird.
- Melde Sebastian Zwischenstände knapp; keine Zusammenfassungen dessen, was er selbst sieht.

## Arbeitskonventionen (von Sebastian)

- Dateien immer mit Python bearbeiten (kein sed/perl-Regex-Substitute).
- Alles, was in Git und in den Quellcode geht (Commit-Messages, Code-Kommentare, READMEs), auf Englisch.
- Wenn du ihm Lesebefehle gibst: alle in einem einzigen Block gebündelt und durch `more` geleitet;
  Aktionsbefehle getrennt davon. Bei Deploy-/Messrunden alle Befehle vollständig und in Reihenfolge.
- Große Downloads (Firmware-PUP, AppImages, ISOs) mit `aria2c`, nicht curl/wget.
- Lege diese Regeln zusätzlich als `~/gt5re/CLAUDE.md` ab, falls noch nicht vorhanden.

## Umgebung (bekannt)

- ArchBang (Arch Linux), Ryzen 7800X3D, AMD-V aktiv, X11-Desktop (Openbox). System ist nicht
  per `-Syu` aktuell (altes glibc — .NET deshalb als Microsoft-Tarball unter `~/.dotnet`).
- `rpcs3-git` aus dem AUR ist installiert (wurde für die EBOOT-Entschlüsselung genutzt) — prüfen,
  ob es noch startet; sonst AppImage von rpcs3.net per aria2c oder Flatpak.
- Toolchain in `~/gt5re`: GTToolsSharp (Alias `gttools`, `dotnet ~/GTToolsSharp/GTToolsSharp.dll`),
  GTAdhocToolchain (Alias `adhoc`, `adhoc build` im Projektordner, `adhoc <datei.adc>` disassembliert),
  OpenAdhoc-Repo (Referenz, NIE direkt patchen: pro Testlauf `git clone OpenAdhoc mod_x`, dann
  alle `*.Ad` nach `*.ad` umbenennen). Ghidra-Projekt: `gt5_ghidra_proj.7z.001` (PS3-Loader).
- Daten: `~/gt5re/update/` = kompletter 2.17-Update-Ordner BCES00569 (USRDIR/PDIPFS, 12,7 GB,
  Key GT5_EU, TOC unter PDIPFS/9/TA/ND), `~/gt5re/pdipfs_out/` entpackt, `~/gt5re/disc_out/`
  = entpacktes GT.VOL der Disc. `~/gt5re/EBOOT.elf` = entschlüsseltes EBOOT 2.17, Ladeadresse
  0x10000, sha1 beginnt mit 306f86c6 und endet auf 0452 — jede RPCS3-Kopie dagegen prüfen,
  sonst stimmen die Adressen nicht.
- PS3: CFW, webMAN MOD 1.47.48 (Full, PS3MAPI), FTP + HTTP auf 192.168.1.11. GT5 liegt dort nur
  als Update-Ordner `/dev_hdd0/game/BCES00569/` (kein ISO); die Disc ist vorhanden (Blu-ray).
  Der USB-BD-Brenner (Pioneer BDR-UD03) liest PS3-Discs nicht — Disc-Dump also über die PS3:
  Disc einlegen, dann `/dev_bdvd/` per FTP spiegeln (lftp mirror, 2 Verbindungen) oder webMAN
  ein ISO erzeugen lassen. Sebastian vorher bitten, die Disc einzulegen.
- RPCS3 braucht außerdem die offizielle Sony-Firmware (PS3UPDAT.PUP) — per aria2c holen und
  in RPCS3 installieren.

## Ermittlungsstand (Kurzfassung — Details im Dossier)

### Was funktioniert (auf echter Hardware gemessen)

- Adhoc-Script-Mod (arcade.adc, race.adc aus OpenAdhoc, gepatcht mit `patch_arcade_v2/v3.py`,
  `patch_race_log_w4.py`): Split-Battle bietet Spieler 3 an, drei Einträge mit eigenem
  MCarDriverParameter (ctrlport 0/1/2), `MOD_WINDOW_MAX=3`. Gepackt/hochgeladen mit `deploy_mod.sh`
  nach `/dev_hdd0/game/BCES00569/USRDIR/PDIPFS/`. Log des Mods: `USRDIR/4pmod_race.log`.
- **Load-Fix (cave4)**: Funktion 0x381e54 setzte Slot 2 nach dem Laden (Zustand 11) über den
  `[slot+0x28]!=0`-Zweig bei 0x381fbc auf Zustand 22 zurück. Cave bei 0x1580d80, Hook 0x381fb0
  (Original `38800016` = `li r4,0x16` → `491FEDD0`): wenn Slot(r26)==0x42402c90 und
  [slot+0x4f4]==0x0b, springe nach 0x382084 (Reset übersprungen), sonst `li r4,0x16; b 0x381fb4`.
  Wörter in `cave4_words.txt`. Für 4P muss die Bedingung auf Slot-Index ≥ 2 verallgemeinert
  werden (`[slot+0x4f8]` ist der Index) statt Zeigervergleich.
- **viewport_count=3**: 0x379c30 `39290002`→`39290003` (`addi r9,r9,3` in 0x379bf0). Zwilling
  0x37b250 `3bff0002` (Slot-Zahl in 0x37b208; das Array hat ohnehin 3 Slots, dieser Poke war
  wirkungslos, aber für 4P relevant, weil die Slot-Zahl an `Organizer+0x984` geschrieben wird).
- Mit cave4 + viewport=3 (`root1_deploy.sh`) laden alle drei Autos (alle Slots Zustand 11), und
  die Sequenz läuft: carload passed → canEnterCourse → enterCourse → inCourse → RR.onInitialize →
  startSessionForRace → ok. Danach hängt es in der Session-/Render-Init, weil nur zwei Fenster
  existieren.

### Die offene Wand: Fenster[2]

- Fenster-Manager = Inline-Objekt in RaceScene+0xa90, Zeiger in `Organizer+0x9c4` (Laufzeit
  0x422D8A90). Layout: +0x1c Fenster[0], +0x24 Fenster[1] (8-Byte-Slots, das zweite Wort +0x20/
  +0x28 hält den Registrierungsknoten 0x19472f0), +0x2c window_max, +0x30 clamp, +0x34..0x3a
  View-Flags, +0x37 und +0x3b sind die einzigen freien Bytes, +0x44 nächstes lebendes Scene-Feld.
- WM-Konstruktor 0x461fa4 (Frame 0xb0, `this` in r29/r25), Schleife über 2 Fenster mit Grenze
  0x462118 (`cmpwi r27,1`); Alloc 0xbc1974 (Größe in r3, 0x740 je Fenster); Fenster-Konstruktor
  0x469320 (r3=win, r4=index; Index bei win+0; 58-KB-Viewport-Datenblock 0xe580 bei win+4).
  Ctor-Nachlauf 0x462124–0x462158 schreibt window_max=1 (+0x2c), clamp=1 (+0x30), Flags,
  Global 0x17fd0b4=0, +0x18=0.
- setWindowMax 0x460814, getWindowMax 0x45f274 (liest +0x2c), setupWindows 0x46058c
  (Schleifengrenze 0x460648; Kameratabellen 0x1784614 voll / 0x178463c 2-Split, 8-Byte-Einträge
  {flag, view-id}, 0xffffffff-terminiert), setCameraTarget 0x460780 (keine Bereichsprüfung).
  Externe getWindowMax-Iteratoren 0x2284f8, 0x229310. RaceDisp_reset 0x238394 läuft schon 4-fach.
- **Bewiesen (ctortest.sh, 2P-Lauf startet normal)**: ein drittes Fensterobjekt per Cave nach der
  Ctor-Schleife (Hook 0x462124) mit 0x469320(index=2) anlegen ist absturzfrei, solange der Zeiger
  weggeworfen wird.
- **Friert ein (Endlos-Hang, PS-Knopf lebt)**: `win3b_deploy.sh` (75 Wörter: cave4 + viewport=3 +
  Fenster[2]-Konstruktion mit Ablage bei +0x2c + Knoten bei +0x30 + window_max/clamp verlagert auf
  Bytes +0x37/+0x3b + setWindowMax neu gefasst (0x460814–0x460864, Fenster 0–2) + 22 Schleifen-
  grenzen) und ebenso `win3c_deploy.sh` (dasselbe ohne die 22 Schleifen). Der Hang entsteht also
  beim lebendigen Verdrahten von Fenster[2], nicht bei der Konstruktion und nicht bei den Schleifen.
- Hypothesen, im Emulator zuerst prüfen: (a) ein Leser von +0x2c/+0x30 wurde nicht verlagert —
  alle Zugriffe auf WM+0x2c/+0x30 und auf RaceScene+0xabc/+0xac0 (0xa90+0x2c/+0x30) suchen, auch
  über kopierte Zeiger; (b) getWindowMax=3 treibt 0x2284f8/0x229310 über Fenster[2], bevor dessen
  Viewport-Block/Registrierung fertig ist; (c) setupWindows hat keinen >2-Zweig, die 2-Split-
  Kameratabelle hat 4 Einträge — für drei Ansichten braucht es eine eigene Tabelle und ein
  drittes Viewport-Rechteck; (d) der Registrierungsknoten 0x19472f0 ist ein Listenkopf: ein
  drittes Fenster muss dort korrekt eingehängt werden, sonst wartet ein Render-Thread ewig auf
  ein Fenster, das nie „fertig" meldet — ein Hang statt Absturz spricht für genau so eine Warteschleife.
- Alle Patch-Wortlisten liegen als `<name>_final.txt` / `<name>_words.txt` vor (Adresse, Original,
  Neu) und sind capstone-verifiziert. Neue Wörter immer mit capstone (`ppcdis.py`) gegenprüfen —
  zweimal ist `stb r8` statt `stb r0` (0x991D0018 vs. 0x981D0018) durchgerutscht.

### Speicher-Fakten

- Organizer 0x4FEB9000, Slot-Array 0x42402010 (Stride 0x640, Slot 2 = 0x42402c90), Slot-Zahl
  Organizer+0x984, Slot-Zustand +0x4f4 (11 geladen, 22 wartend), Index +0x4f8, Bereit +0x510 (3).
  Adressen waren über alle Läufe deterministisch — im Emulator neu verifizieren.
- Zustandsprimitive 0x3b87a8(slot, state) unter Sperre +0x4ec; setReady 0x3b61e8.
  Auftrags-Array Organizer+0xbd8 (0x34 je Eintrag, +0x28 Slot-Index, +0x2c Callback-Tabelle
  0x01727E28); pro-Slot-Ladeschritt 0x16fc48 → 0x381e54.
- Code-Caves: freie Null-Läufe im schreibgeschützten R-E-Bereich ab 0x1580ca0 (0x1580d80 = cave4,
  0x1580dc0 = win3b-Ctor-Cave, 0x1580e40 = ctortest); Code-Segment R-X bis ~0x169e6e8.
- Auf der PS3 wirken Code-Pokes nur, wenn sie KALT im Hauptmenü gesetzt werden (I-Cache). Im
  Emulator gilt das genauso, wenn man zur Laufzeit pokt — deshalb dort Patches über das
  Patch-System vor dem Start anwenden.

## Emulator-Hinweise

- RPCS3-Patchsystem: `~/.config/rpcs3/patches/patch.yml` (Version 1.2, Schlüssel `PPU-<sha256 des
  entschlüsselten EBOOT>`, Einträge `[ be32, <adresse>, <wort> ]`). Das genaue Adressformat
  (virtuelle Adresse vs. Dateioffset) vor dem ersten Einsatz in der RPCS3-Wiki nachlesen und mit
  einem harmlosen Wort (z. B. 0x379c30) verifizieren. Der Hash steht im RPCS3-Log beim Laden.
- Für Breakpoints/Einzelschritt PPU-Decoder auf Interpreter stellen (LLVM hat keine Breakpoints);
  für flüssige Läufe wieder LLVM. SPU: Empfehlung der Kompatibilitätsseite für BCES00569 übernehmen.
- Start ohne Oberfläche: `rpcs3 --no-gui <pfad>/PS3_GAME/USRDIR/EBOOT.BIN`; Log `RPCS3.log`
  im Config-/Cache-Verzeichnis. Abstürze stehen mit PPU-PC im Log; bei Hängern RPCS3 pausieren
  und im Debugger-Fenster die PCs aller PPU-Threads ablesen (das ist genau das, was auf der PS3
  nicht ging). Alternativ Host-gdb an den rpcs3-Prozess: Gastspeicher liegt linear ab
  `vm::g_base_addr`, damit lassen sich Organizer/Slots/WM direkt lesen.
- Bildschirm lesen: `import -window root shot.png` (ImageMagick) oder `scrot`, dann die PNG mit
  deinem Read-Werkzeug ansehen. So erkennst du selbst, wo im Menü du bist.
- Eingabe ohne Hände: Spieler 1 über den RPCS3-Tastatur-Handler und `xdotool key --window`
  (Mapping in `~/.config/rpcs3/input_configs/global/Default.yml` prüfen/setzen). Spieler 2–4
  als virtuelle Gamepads über `/dev/uinput` (python-evdev `UInput` mit Gamepad-Eventcodes) im
  RPCS3-evdev-Handler — damit kannst du „Spieler 3 drückt X" selbst auslösen und die ganze
  Menüführung bis ins Rennen skripten. `/dev/uinput` braucht Rechte (udev-Regel oder Gruppe
  `input`) — sudo-Block für Sebastian vorbereiten. Echte DualShock-3-Controller hat er, falls du
  sie brauchst.
- Menüpfad auf der PS3 war: Arcade → Split-Battle (2 Spieler) → mit Mod: Spieler 3 = ja → Auto-
  wahl → Strecke → Ladebalken → Rennen. Erst 2P im Emulator ohne Patches bestätigen (Referenz),
  dann 3P mit cave4+viewport (muss im Ladebalken alle drei Autos laden), dann Fenster-Patch.

## Dateien in ~/gt5re (Übersicht)

- Deploy/Poke-Skripte (alle brauchen `PS3=192.168.1.11`, lesen die PID aus `home.ps3mapi`):
  `cave4_deploy.sh` (nur Load-Fix), `root1_deploy.sh` (cave4 + viewport=3, bestätigt),
  `win3b_deploy.sh` (Vollpatch, friert), `win3c_deploy.sh` (ohne Schleifen, friert),
  `ctortest.sh` (Ctor-Isolation, sicher), `patch_windows3.sh`/`win3_deploy.sh` (ältere Fassung),
  `poke_cold.sh`, `fix3rd.sh`, `test_reset.sh`, `test_spin1.sh`, `cave_deploy.sh`/`cave3_deploy.sh`
  (+ `_read.sh`: Instrumentierungs-Caves und Auslesen).
- Mess-/Dump-Werkzeuge: `gt5mem.py` (Organizer + Slots dumpen/diffen), `watch3.py` (Slot-Zustände
  live), `dump_org.sh`, `dump_jobs.sh`, `slots.sh`, `leak_a.sh`/`leak_b.sh`/`leak_org.sh`, `probe_mem.sh`.
- Script-Mod: `patch_arcade_v2.py`, `patch_arcade_v3.py`, `patch_race_log_w4.py` (+ ältere),
  `deploy_mod.sh` (packen + FTP-Upload). Bau siehe Dossier „Bauen und ausrollen".
- Statische Analyse: `EBOOT.elf`, `ppcdis.py` (capstone), `findrefs.py`, `callers.py`, `rtti.py`,
  `race.diss`, `race_split.diss`, `arcade.diss`, `pml.diss`, `gpu.diss`, `wm.txt`,
  `gt5_decomp_windowmgr.c`, `out1-4.c` (Ghidra-Decompilate), `strings.txt`, `full.txt`
  (Gesamt-Disassembly, ggf. neu erzeugen), `scripts/DumpFuncs.java` (Ghidra-Skript).
- Wortlisten: `cave4_words.txt`, `ctortest_words.txt`, `win3b_cave.txt`, `win3_final.txt`,
  `win3b_final.txt`, `win3c_final.txt`, `win3_patches.txt`, `cave_words.txt`, `cave3_words.txt`.
- `doc/gt5-3p-dossier.html` — das vollständige Dossier.

## Hardware-Test auf der PS3 (für die Übergabe an Sebastian)

Wenn der Emulator durch ist: `deploy_3p.sh` erzeugen, Sebastian den Ablauf geben — GT5 frisch
starten, im Hauptmenü stehen bleiben, `PS3=192.168.1.11 ~/gt5re/release/3p/deploy_3p.sh apply`
(darf auch du ausführen, aber ansagen), dann Arcade → Split-Battle → Spieler 3 → Rennen. Rückbau
immer mit `... off` bzw. Neustart des Spiels. Erst nach bestandenem Hardware-Test taggen.
