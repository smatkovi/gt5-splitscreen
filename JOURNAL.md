# GT5 3P/4P — Test-Journal

Chronologisch, neueste Einträge unten. Pro Eintrag: Datum, Patch-Stand, Ergebnis.

---

## 2026-09-05 — Übergabe an Claude Code, RPCS3-Aufbau

**Umgebung geprüft**
- `rpcs3-git 0.0.42.r19916` startet, Vulkan/RX 7900 XT, X11 (1280x1024), 61 GB RAM, 16 Threads.
- Referenz-EBOOT liegt als `eboot/EBOOT_orig.elf`, sha1 `306f86c6…0452` — stimmt.
  `~/gt5re/EBOOT.elf` ist jetzt ein Symlink darauf (HANDOFF nannte diesen Pfad).
- capstone/evdev fehlten im System-Python (externally managed) → venv `~/gt5re/.venv`.
- `CLAUDE.md` mit Sebastians Arbeitsregeln angelegt.

**Firmware**
- PS3UPDAT.PUP 4.93 per aria2c geholt (`~/gt5re/fw/`), in RPCS3 installiert
  (189 MB dev_flash, 1075 Dateien, `vsh/etc/version.txt` = 04.9300). Ergebnis: OK.
- Anmerkung: `rpcs3 --no-gui --installfw` funktioniert NICHT ("Cannot perform installation
  in no-gui mode"). Nur mit Oberfläche. Qt-Dialoge zeichnen unter Openbox teils nicht —
  deshalb Dialoge über `GuiConfigs/CurrentSettings.ini` abgeschaltet
  (`infoBoxEnabledWelcome=false` usw.) statt sie anzuklicken.

**Datenlage (Befund, wichtig)**
- Der Disc-Dump ist bereits lokal vorhanden: `~/gt5re/disc/game/` (21 GB) — ein erneuter
  Dump von der PS3 ist NICHT nötig. Die Disc liegt außerdem noch im Laufwerk (`/dev_bdvd`
  ist gemountet), Nachladen einzelner Dateien ist also möglich.
- **Der Mirror ist stellenweise korrupt.** Gemessen mit Byte-Range-Vergleich gegen die
  Konsole (`tools/verify_remote.py`):
  - `PS3_GAME/INSDIR/DATA000.PKG`: lokal 1038482640 statt 1196578448 Byte (abgeschnitten),
    `INSDIR/PARAM.SFO` fehlte ganz.
  - `PS3_GAME/USRDIR/GT.VOL`: Größe stimmt (12098856960), Inhalt ab ca. 0xb449d568 aber
    falsch — 5 von 7 Stichproben oberhalb 3 GB weichen ab.
- **Ursache**: webMAN liefert falsche Daten, wenn MEHRERE FTP-Verbindungen dieselbe Datei
  parallel lesen (lftp `pget`, `aria2c -x2`). Selbst reproduziert: `aria2c -x2` erzeugte
  eine Datei mit korrekter Größe und einem Null-Loch in der Mitte. Der ursprüngliche
  Disc-Mirror lief laut HANDOFF mit 2 Verbindungen — daher der Schaden.
  REST/Byte-Ranges an sich funktionieren korrekt, auch oberhalb von 2 GB.
- **Regel ab jetzt**: Downloads von der PS3 immer mit EINER Verbindung
  (`aria2c -x1 -s1 --continue=true`), danach mit `tools/verify_remote.py` stichprobenartig
  gegenprüfen.
- Folge: `disc_out/` und `GT_extracted/` wurden aus einem teilweise korrupten GT.VOL
  entpackt und sind mit Vorsicht zu genießen.

**RPCS3-Spielaufbau**
- Disc: `~/gt5re/disc/game/` (PS3_DISC.SFB + PS3_GAME) wird von RPCS3 als BDVD erkannt,
  Titel BCES00569, `CATEGORY DG`, APP_VER 01.00.
- Update 2.17 (`~/gt5re/update/`, `CATEGORY GD`, APP_VER 02.17) gehört nach
  `dev_hdd0/game/BCES00569/`.
- **Achtung**: erst als Hardlink-Farm (`cp -al`) angelegt — wieder entfernt, weil RPCS3
  (PKG-Installer) und GT5 selbst in dieses Verzeichnis schreiben und ein Schreibzugriff
  über einen Hardlink Sebastians Master unter `~/gt5re/update/` zerstören würde.
  Der Master ist unverändert.
- Erster Boot scheiterte an `INSDIR/DATA000.PKG` ("PKG file size mismatch") — daher die
  Nachladeaktion oben.

**Config-Änderungen in `~/.config/rpcs3/config.yml`**
- `Start games in fullscreen mode: false` (Fenster ist per xdotool/import bedienbar)
- `License Area: SCEE`, `Language: English (UK)` (PAL-Titel)

**RPCS3 läuft mit GT5 2.17 (00:36)**
- `dev_hdd0/game/BCES00569`: erst RPCS3 das Disc-PKG (`INSDIR/DATA000.PKG`, 1,2 GB) installieren
  lassen, dann `rsync -a update/ → hdd0` (ohne `PDIPFS_extracted`, `EBOOT.elf`). Alle PKG-Dateien
  sind eine Teilmenge des Update-Ordners; Ergebnis 4,3 GB, PARAM.SFO = 02.17.
  (Die „12,7 GB PDIPFS" aus dem HANDOFF enthielten `PDIPFS_extracted` (7,8 GB); die echte
  Update-Nutzlast ist 4,3 GB.)
- RPCS3 bootet beim Start der Disc automatisch `/dev_hdd0/game/BCES00569/USRDIR/EBOOT.BIN`
  (Update-Mechanismus funktioniert). hdd0-EBOOT.BIN ist byte-identisch mit `update/USRDIR/EBOOT.BIN`,
  dessen entschlüsselte Fassung sha1 `306f86c6…0452` hat → Adressen stimmen mit der Analyse überein.
- **PPU-Hash für das Patch-System: `PPU-223cc85fc80a6667fae775c7c02f7f65e6b2871f`**
  (`~/.config/rpcs3/patches/patch.yml` angelegt mit viewport=3, 0x37b250-Zwilling, cave4 —
  alle noch deaktiviert, bis 2P-Referenz steht).
- Rendering OK (Vulkan, 60 FPS im Menü), Tastatur-Pad-Handler für Spieler 1 geladen
  (`input_configs/global/Default.yml`, Spieler 1–4 als Keyboard mit getrennten Tasten;
  Spieler 2–4 noch nicht getestet).
- Erste In-Game-Abfrage „Data Installation Recommendation" (optionale 8-GB-Installation):
  mit **Nein** beantwortet — auf der Konsole ist sie ebenfalls nicht gemacht (PDIPFS 4,3 GB),
  und lokal wäre die Quelle der korrupte GT.VOL.
- Werkzeuge: `tools/shot.sh` (Screenshot des Spielfensters), `tools/pad.sh` (Tasten an RPCS3),
  `tools/verify_remote.py` (Byte-Vergleich gegen PS3), `tools/scan_disp.py` (D-Form-Zugriffe
  auf ein Displacement im EBOOT finden).

**Erster Lauf im Hauptmenü eingefroren (00:43), zweiter Lauf OK (01:00)**
- Lauf 1 (`--no-gui`, MEMLOCK-Hardlimit 8 MB → "Failed to lock sudo memory" ×viele): Hauptmenü
  erschien, danach Standbild (Uhr blieb auf 0:42, keine Reaktion). Host-gdb (`sudo gdb -p`):
  ALLE PPU-Threads in lv2-Wartezuständen (lwcond/event-queue/spu-group-join), SPUs in
  Channel-Reads — kein Thread lief. Nur `libpace-comm` pollte weiter `sys_net_bnet_poll`.
  Die PSN-Abfrage ("Sign in to PlayStation Network?") war noch nicht erschienen.
- Lauf 2 (GUI, MEMLOCK per `sudo prlimit --pid $$ --memlock=2G` VOR dem Start angehoben →
  keine Lock-Fehler; zusätzlich `Accurate RSX reservation access: true`,
  `Disable ZCull Occlusion Queries: true` laut RPCS3-Wiki): PSN-Dialog kam, mit Nein beantwortet,
  Menü bleibt lebendig. Ursache von Lauf 1 nicht sicher isoliert (MEMLOCK vs. Zufall) —
  MEMLOCK-Anhebung ab jetzt immer, `tools/rpcs3_run.sh` erledigt das.
- RPCS3-Wiki (via Wayback): keine GT5-spezifischen Freeze-Hinweise außer den beiden Settings;
  SPU-LLVM-Absturz beim Autokauf (irrelevant). Patch-Adressen dort sind virtuelle Adressen →
  unser Format stimmt.
- GT5 SCHREIBT ins Spielverzeichnis (`PDIPFS/9/K6/JA` via `.psctmp`, `PDIPFS_bdmark/…`) —
  Bestätigung, dass die Hardlink-Farm gefährlich gewesen wäre.
- Eingabe: `xdotool key --window` wird von RPCS3/Qt sporadisch verschluckt; XTest ohne
  `--window` (Fenster vorher aktivieren) ist zuverlässig. `tools/pad.sh` umgestellt.
- Erster Start legt Savedata `BCES00569-GAME` an; My-Home-Erstkonfiguration (Design-Dialog,
  Outfit-Items) einmalig weggeklickt. Menüpfad Hauptmenü: Icons = My Home, Arcade Mode,
  Course Maker, GT TV, ?, Optionen, Aufnahme, Beenden.

**Zweiter Menü-Freeze (01:07, Lauf 2, ~6 min nach Menü) — Gast-Backtraces**
- `tools`-Skripte `ppupc.py`/`ppubt.py` (gdb-Python, `sudo gdb -p`): Backchain-Walk aller PPU-Threads
  über `vm::g_base_addr`. Ergebnis (`scratchpad/ppubt1.txt`):
  - main_thread (0x1000000): lwcond-Wait in Schleife 0x511ad8–0x511b1c (3 Objekte bei
    [r28+0x1fc+i*4]; wenn obj+0xbc && obj+0xa8>0: signal(obj+0x70) → wait(r27)). Aufrufer
    0x068c05c → 0x0a3cb04 → 0x0a13dec → 0x09d8f20. Letzte Log-Aktivität 0:09:00 Emu-Zeit.
  - n3FKY (0x100002a): lwcond-Wait 0x0a6e034 ← 0x0a6dd78 ← 0x0a6fa84 … ← 0x005beb0.
  - ksF3-Worker (0x1000008–0x100000f): alle idle bei 0x0a71afc ← 0x0a716b4 (Job-Warteschleife).
  - Alle SPUs in Channel-Reads. Muster = verlorener Wakeup zwischen Job-Zähler (obj+0xa8) und Worker.
- Beide Freezes traten im Hauptmenü im Leerlauf auf (Hintergrundszene lädt PDIPFS-Dateien).
- Versuch 3: `SPU Decoder: Recompiler (ASMJIT)`, `Accurate SPU DMA: true`,
  `Accurate Cache Line Stores: true` (Wiki: SPU-LLVM bei GT5 problematisch).

**Dritter Freeze (01:19, Lauf 3 mit SPU-ASMJIT) — im GT-Logo-Ladebildschirm**
- Trat direkt nach dem On-Demand-Kopieren von Disc-Dateien nach PDIPFS auf (`9/U3/ZA` via
  `.psctmp`, `PDIPFS_bdmark/9/U3`). Freeze 1 ebenso nach `9/K6/JA`. → GT5 zieht bei Bedarf Dateien
  aus GT.VOL in den HDD-Cache; mit dem korrupten GT.VOL ist jeder Hänger verdächtig.
  **Emulator-Tests pausiert, bis GT.VOL.new fertig und verifiziert ist** (`tools/reset_hdd0.sh`
  danach ausführen, damit die aus dem kaputten GT.VOL kopierten Cache-Dateien verschwinden).
- Statisch: keine übersehenen Leser von WM+0x2c/+0x30 (Scan über Displacements 0x2c/0x30 im
  WM-Code und 0xabc/0xac0 scene-relativ; die Treffer 0x3845xx/0x384axx sind ein anderes Objekt
  mit {int,string}-Paaren, 0x46fxxx liegt im Fenster-Datenblock).
- Callers: getWindowMax ← 0x17277c (Adhoc-Thunk), 0x2284f8, 0x229310, 0x460600;
  setWindowMax ← 0x172750 (Thunk); setupWindows ← 0x16d0cc, 0x16d124, 0x1727ac, 0x481d94;
  WM-Ctor ← 0xc3adc0; setCameraTarget ← 0x1727e4.

**Mod-Stand / Toolchain**
- PS3 `PDIPFS` enthält byteidentisch `mod_mem-pdipfs` (K/4D, 9/PQ/O3, 9/DF/9T, 9/7T/X6 — md5 gleich).
  mod_mem = arcade v2 + race w5 (mit Speicherprofil-Logging); HANDOFF-Rezept (v2 + w4) ist
  funktional dasselbe ohne Logging.
- Toolchain-Pfade (Aliase nur in .bashrc): `~/.dotnet/dotnet --roll-forward Major
  ~/gt5re/GTToolsSharp/GTToolsSharp/bin/Release/net9.0/GTToolsSharp.dll` und
  `… GTAdhocToolchain/GTAdhocToolchain.CLI/bin/Release/net10.0/adhoc.dll`.
- `tools/deploy_mod_rpcs3.sh <mod>-pdipfs` legt den Pack-Overlay in die RPCS3-Kopie.
- `~/.config/rpcs3/patches/patch.yml`: Gruppen viewport3, twin, cave4, ctortest, win3c-core (52 W),
  win3b-loops (22 W) — alle aus, zum Einschalten `patch_config.yml`.
- `cave4b_words.txt`: cave4 verallgemeinert auf Slot-Index ≥ 2 (für 4P), capstone-geprüft,
  noch ungetestet.

**Mod-Build reproduziert (01:45)**
- `tools/build_mod.sh mod_x`: Clone von OpenAdhoc-HEAD (der Working-Tree des Referenz-Repos ist
  übrigens verändert — 6 Dateien M, `patch_arcade_phase1.py`/`WatcherUtil.ad` untracked; HEAD
  selbst ist sauber, `git clone` liefert die Referenz), patch_arcade_v3 + patch_race_log_w4
  (MOD_WINDOW_MAX=3) + `cp.checkValid()` in CarRoot/CarSplitRoot, adhoc build, GTToolsSharp pack.
  arcade.ad-Quelle identisch mit mod_mem (= PS3-Stand; das .adc weicht in wenigen Bytes ab, der Compiler ist nicht bit-deterministisch), race.adc byteidentisch mit mod_w4
  (mod_mem hat die w5-Logging-Variante). Overlay `mod_x-pdipfs` in die RPCS3-Kopie deployt.

## 2026-09-05 08:20 — 3P-Ladeabbruch im Emulator (Sebastian am Steuer, Script-Mod, keine RAM-Patches)

- GT.VOL.new (verifiziert, 25/25 Stichproben OK) eingetauscht (alter = `GT.VOL.corrupt-old`, 12 GB,
  kann weg), `reset_hdd0.sh`, `mod_x-pdipfs` deployt, Neustart. Sebastian navigierte selbst:
  Arcade → Split Battle → Spieler 3 = ja → Rennen starten → „hängt bei ~5 % Ladebalken".
- **Kein Hänger, sondern Absturz** (RPCS3-Log): `PPU[0x1000029] vyENO: Access violation writing
  0x83a8e50e` in `0x48deb4` (`stb r4,4(r3)`), Aufrufkette 0x170b98 → 0x26de54 → 0x48e1c0/0x48deb4.
  Emulation eingefroren („likely crashed").
- Mechanik: `0x170a38(MOrganizer, r4, index, r6, r7)` sucht in einer 0xd8-Liste den Eintrag zum
  Spieler-Index, alloziert ein 0x3270-Byte-Objekt (0xbc1974), Ctor `0x26eb54(obj,[MOrg+0xad8],index)`,
  dann `0x26de54(obj, [MOrg+0xa78], entry, index)` mit
  **`entry = MOrganizer + 0x2b8 + index·0x290`** (0x170b74/0x170b7c). `0x48e1c0(entry)` liest
  `[entry+0x284]` als Zeiger und setzt Byte +0x188+4. Für index 2 liegt der Eintrag bei +0x7d8 und
  `+0x284` = MOrg+0xa5c — kein Eintrag mehr, sondern ein anderes Feld → auf der PS3 ein gültiger
  Zeiger (stiller Speicherschaden, danach der 100-%-Hänger), im Emulator Müll → Absturz.
- MOrganizer (Laufzeit 0x422D8000) hält den Fenster-Manager bei +0xa90 (Thunks 0x172738/0x1727c8:
  `lwz r3,0(r3); addi r3,r3,0xa90`) und die Spieler-Eintragstabelle bei +0x2b8 (Stride 0x290,
  zwei Einträge: +0x2b8, +0x548; ein dritter würde +0x7d8..+0xa68 belegen — Layout dort unbekannt).
  Nutzer der Tabelle: 0x170b74 (Fabrik), Iteratoren `addi rX, rMOrg, 0x2b8` bei 0x175cec, 0x176164,
  0x1762dc, 0x1833e4; `mulli 0x290` bei 0xc3ad08 (MOrganizer-Ctor), 0x489eec–0x48a158, 0x25ec94/0x25ed44,
  0x2caca0, 0xcdbf5c–0xcdca30.

**Patch „MOrganizer entries ×4" (08:50, `morg_entries4_words.txt`, 35 Wörter, capstone via `tools/ppcasm.py`)**
- MOrganizer wird bei 0x177110 mit 0x35030 Byte alloziert (Ctor-Einstieg 0xc3ab7c, Aufrufer 0x177134).
- Cave 0x1580f00: `li r3,0xa40; bl alloc; lwz r5,0xc8(r1); stw r3,0x2b8(r5); addi r0,r3,0xa40;
  stw r0,0x2bc(r5); mr r5,r3; b 0xc3acd4` — Hook 0xc3acd0. Ctor-Schleife `cmpwi r28,-1 → -3`.
- 1:1-Umschreibungen `addi rX,rMOrg,0x2b8 → lwz rX,0x2b8(rMOrg)` bei 0x175cec, 0x176164, 0x1762dc,
  0x1833e4, 0xc40570, 0xc405ac, 0xc41d98, 0xc41dd4; Fabrik 0x170b78/7c → `lwz r10,0x2b8(r25); add r5,r9,r10`;
  Schleifengrenzen 0x175d00/0x176180/0x1833f8 `1 → 3`; Dtor-Endzeiger über Caves 0x1580f40–0x1580f5c
  (`lwz r31,0x2bc(r26)`), Sprünge 0xc40558/0xc40568/0xc41d80/0xc41d90 umgelenkt.
- Bewusst nicht geändert: 0xc3ad58 (`addi r5,r5,0x7d8` = Feld nach dem Array, kein Array-Ende);
  0x25ec50/0x2caca0/0xcdbf5c erhalten die Basis über Argumente/Handle → automatisch extern.
- Offen/Risiko: Direktzugriffe `lwz/stw rX, 0x2b8..0x7d7(rMOrg)` ohne addi lassen sich statisch nicht
  von anderen Objekten trennen; die tote Inline-Fläche 0x2c0..0x7d8 bleibt ungenutzt.
- `patch_config.yml`: viewport3 + twin + cave4 + entries×4 EIN. Test 3P im Emulator steht aus.

**3P-Test mit viewport3 + twin + cave4 + entries×4 (09:08)**
- Der Entry-Absturz ist weg. Mod-Log läuft durch bis `RR: startSessionForRace -> ok` (= PS3-Stand
  mit root1). Neuer Absturz: `main_thread: Access violation reading 0x7` (Log-PC 0x87f84 = Rücksprung
  nach `bctrl`, CIA veraltet). Kette: Adhoc `ORG.setCameraTarget(window_id=2, slot)` (RaceRoot.ad:47)
  → Thunk 0x1727c0 → 0x460780 liest `WM+0x10+2*8+0xc` = WM+0x2c = window_max (3) als Fensterzeiger →
  0x46565c liest [3+4] = 0x7. Damit ist Fenster[2] zwingend.
- Ladebildschirm zeigte bereits drei Einträge (Zonda/Zonda/GT-R, User[1]/[2]/[3]).
- Attract-Demo: startet nach ~1 min Inaktivität im Hauptmenü und lädt ein Rennen — Erklärung für die
  „Leerlauf-Hänger" (mit korruptem GT.VOL) und für unerwartete Bildschirmwechsel.
- Screenshots: Spielfenster vor der Aufnahme nach vorn holen (`shot.sh`), sonst zerrissen/verdeckt.

**Plan Fenster-Slots (Ansatz A, WM-Layout bleibt)**: externes Slot-Array (4×{ptr,node}) aus dem
WM-Ctor-Cave, Zeiger bei MOrg+0x2c0 (WM-relativ −0x7d0). Index-Zugriffe (`addi rX,rX,0x10` →
`lwz r11,-0x7d0(r3)`; `add r3,r3,rX` → `add r3,r11,rX`; `lwz r3,0xc(r3)` → `lwz r3,0(r3)`),
Byte-Offset-Schleifen (`add r9,r30,r31; clrldi; lwz r3,0x1c(r9)` → `lwz r9,-0x7d0(r30); add r9,r9,r31;
lwz r3,0(r9)`), `addi r31,r3,0x1c` → `lwz r31,-0x7d0(r3)`, Grenzen 8→0x18 bzw. 1→3, setWindowMax neu
(Schleife über 4), direkte Reads +0x1c/+0x24 bleiben (Dual-Write). window_max/clamp unverändert.

**Patch „window slots ×4" (09:20, `win4_words.txt`, 213 Wörter, Generator `tools/gen_win4.py`)**
- Externes 4-Slot-Array {ptr,node}, Zeiger bei WM−0x7d0 (= MOrg+0x2c0). Ctor-Cave 0x1581000 (Hook
  0x462124): Array allozieren, Slots 0/1 spiegeln, Fenster 2/3 mit 0x469320 bauen, Knoten 0x19472f0,
  Original-Tail replizieren, zurück nach 0x46215c.
- 22 Index-Zugriffe (`addi rX,rX,0x10 → lwz r11,-0x7d0(rBase)`, `add rD,rBase,rX → add rD,r11,rX`,
  `lwz rT,0xc(rD) → lwz rT,0(rD)`; Basis auch r4 bei 0x45fa9c/0x460544; 0x460cc0 mit zweitem Read
  0x460d74), 16 Byte-Offset-Schleifen (`add r9,rB,r31 → lwz r9,-0x7d0(rB)`; `clrldi → add r9,r9,r31`;
  `lwz 0x1c(r9) → 0(r9)`; `cmpwi r31,8 → 0x18`), 6 `addi r31,r3,0x1c → lwz`, 11 Zählgrenzen 1→3,
  setWindowMax (0x460814) als 14-Wort-Schleife über das externe Array. Direkte Reads +0x1c/+0x24
  unverändert (Spiegel). Destruktor-Schleifen unverändert (Fenster 2/3 leaken).
- RPCS3: 5 Gruppen aktiv (viewport3, twin, cave4, entries×4, slots×4), alle „Applied".
- Werkzeuge: `tools/classify.py` (Bildzustand per Referenz-Crops in `tools/nav_ref/`), `tools/nav.sh`
  (Automat: Startdialoge → PSN nein → Arcade → Split → Strecke → Autos P1/P2 → Optionen →
  Mod-Dialoge P3/P4 → Ladebildschirm; bricht bei Absturz ab).

- `tools/gen_deploy.py`: erzeugt aus Wortlisten ein PS3MAPI-Deploy-Skript (apply/off/verify; Caves vor
  Hooks setzen, Hooks zuerst entfernen). Entwurf `release/3p/deploy_3p.sh` (71 Cave- + 191 Code-Wörter)
  aus viewport3 + cave4 + entries×4 + slots×4 — noch ohne Hardware-Test.

## 2026-09-05 09:42 — **3-Spieler-Split-Battle läuft im Emulator**

Patch-Stand: viewport3 + twin + cave4 + entries×4 + slots×4 (RPCS3-Patchgruppen), Script-Mod `mod_x`
(arcade v3 + race w4, MOD_WINDOW_MAX=3). Weg: Arcade → 2P Split Screen → High Speed Ring → Zonda/Zonda →
Optionen → Mod-Dialog Spieler 3 = ja, Spieler 4 = nein.
- Ladebildschirm mit drei Einträgen, Mod-Log bis `load_sequence finished`, **kein Absturz**.
- Rennen gerendert mit **drei Ansichten** im Quadranten-Layout (oben links = Spieler 1, unten links = 2,
  unten rechts = 3), Quadrant oben rechts zeigt Gesamtzeit/Rangliste (User[1], User[3], User[2][2]).
  Position 1/3, 2 Runden, ~56 FPS.
- Eingabe: Gas für Spieler 1 (Pad 0, X) und Spieler 3 (Pad 2, F2) bewegt die jeweiligen Autos;
  Spieler 2 stand still, bis seine Taste (N) gedrückt wurde → alle drei Controller-Ports wirken.
- Schönheitsfehler: HUD (Tacho) sitzt unten mittig über beiden unteren Ansichten (2-Fenster-HUD-Layout);
  Quadrant oben rechts leer bis auf Rangliste.
- Beweisbilder: `doc/emu_3p_first_race_2026-09-05.png`, `doc/emu_3p_race_driving_2026-09-05.png`.
- Attract-Demo, Menüleisten-Toggle per Start und der P4-Dialog sind im Automaten (`nav.sh`) berücksichtigt.

**Test ohne cave4 (09:58)**: viewport3 + twin + entries×4 + slots×4, cave4 AUS → Rennen lädt und
startet ebenfalls (`load_sequence finished`, kein Absturz). Der Load-Fix cave4 ist also nicht mehr nötig —
der Slot-2-Reset war eine Folgeerscheinung des Speicherschadens durch den fehlenden dritten Spieler-Eintrag.
Release 3P deshalb ohne cave4 (adressabhängig); `cave4b_words.txt` bleibt als Reserve.
- `nav.sh`: Zustand `badshot` (Fenster verschoben/teilverdeckt) → Fenster nach 0,0 holen.

## 2026-09-05 10:05 — 4P-Zweig

- Commit `0a7259d` (3P-Stand, kein Tag bis Hardware-Test), `release/gt5-3p-release.tar.gz`.
- `mod_4p` = build_mod.sh mit MOD_WINDOW_MAX=4 (RaceRoot: window_max auf 4 geklemmt), Overlay deployt.
- Patchgruppe „GT5 4P: viewport count 4" (0x379c30/0x37b250 → +4); aktiv: entries×4, slots×4, viewport4.
- Test: nav.sh 4 (Spieler 3 = ja, Spieler 4 = ja).

**4P-Rennen läuft im Emulator (10:11)** — Patches entries×4 + slots×4 + viewport4, Mod MOD_WINDOW_MAX=4,
Dialoge Spieler 3 = ja, Spieler 4 = ja. Mod-Log: vier Einträge (Ports 0–3, eigene Fahrerobjekte),
`load_sequence finished`, kein Absturz. Vier Ansichten in Quadranten (1 oben links, 2 oben rechts,
3 unten links, 4 unten rechts), Position 1/4, ~47 FPS; Tasten aller vier Pads (X, N, F2, KP_Multiply)
bewegen die jeweilige Ansicht. Kosmetik wie bei 3P: HUD im 2-Fenster-Layout, Rangliste/Zeiten liegen
über Ansicht 2. Beleg `doc/emu_4p_race_2026-09-05.png`.

**Mod w6 (10:15)**: `patch_race_log_w6.py` — `ORG.window_max = min(RaceOperator.window_max, MOD_WINDOW_MAX)`
in LoadingUtil statt fest 3/4; `mod_w6` (MOD_WINDOW_MAX=4) dient beiden Releases. Release-Ordner 3p/4p
auf `mod/openadhoc-split.diff` + `mod/pdipfs` aus mod_w6 umgestellt; `release/4p/{README.md,
rpcs3-patch.yml, deploy_4p.sh, words.txt}` angelegt. Gegentest 3P mit w6 läuft.

**Gegentest w6 mit 3 Spielern (10:19)**: `window_max vorher ORG=3 RaceOperator=3` → Klemme wirkt,
drei Einträge, `load_sequence finished`, Rennen läuft (58 FPS), kein Absturz. Ein Mod-Build für beide
Releases bestätigt. Commit mit release/4p + Tarballs `release/gt5-3p-release.tar.gz`,
`release/gt5-4p-release.tar.gz`. Tags erst nach Hardware-Test.

## 2026-09-05 10:30 — Hardware-Test 3P (Sebastian an der Konsole)

- `verify` vor dem Apply: 250/250 Originalwörter stimmen mit der Konsole überein.
- Mein `apply` wurde vom Auto-Mode-Klassifikator blockiert (Schreiben auf die PS3) → Sebastian führt
  `deploy_3p.sh apply` selbst aus. Ergebnis: 249 gesetzt, 1 original (0xc40570, Dtor-Anfang) — ein Poke
  ging unter Last verloren (webMAN antwortet leer/503). Nachpoken per einzelnem setmem angefordert.
- `gen_deploy.py`: rd() mit 5 Wiederholungen, poke() liest zurück und wiederholt 3×; Skripte regeneriert.

**Hardware-Befund (10:45–11:00)**: nach `apply` (warm, im Hauptmenü) startete die Attract-Demo; ihr Rennen lud
vollständig (`load_sequence finished`, window_max=2) und hing dann im Rennen. Ursache: der MOrganizer entsteht
beim Spielstart (`bootstrap_phase2.ad: main::ORG = gtengine::MOrganizer()`), die Ctor-Caves laufen bei Warm-Pokes
nie → externe Arrays uninitialisiert → umgeschriebene Zugriffe lesen Müll. **RAM-Pokes können diesen Patch
prinzipiell nicht tragen; er muss ins EBOOT.**

**Gepatchtes EBOOT (13:30)**: scetool (Sebastians Build) mit `data/keys` aus RPCS3s key_vault (NPDRM-Satz
Revision 0x19, NP_tid/NP_ci/NP_klic_*), Template = Original-EBOOT, `-5 NPDRM -c UEXEC -b FREE -2 19`, ohne
`priv` (unsigniert → CFW-„fake sign"; leeres `priv=` ließ scetool mit NULL-Kurven abstürzen). Rückweg
(`scetool -d`) ist bytegleich mit dem gepatchten ELF. Header wie Original (0x19 / App-Type 0x21 / Lizenz 3).
`tools/build_eboot.sh` reproduziert das. RPCS3 lädt das SELF (PPU-Hash ef2fe6c2…), Wörter im Speicher aktiv.
Release-Ordner enthalten jetzt `EBOOT.BIN`, `EBOOT_patched.elf`, `SHA1SUMS`; READMEs erklären den Weg.

**Emulator mit gepatchtem EBOOT.BIN (13:30, keine Patchgruppen)**: 3P-Rennen lädt (`load_sequence
finished`, 3 Einträge), läuft mit 58 FPS, kein Absturz → das re-verschlüsselte SELF trägt den Patch vollständig.
Konsolen-EBOOT vorab gesichert (`eboot/EBOOT_console_backup.BIN` == Original 2.17). Warte auf Sebastians
Freigabe für den FTP-Upload.

**4P-EBOOT im Emulator (13:45)**: `EBOOT_split4.BIN` allein → 4 Einträge, `load_sequence finished`, vier
Quadranten, kein Absturz (32 FPS).
**PS3-Upload (13:50, Freigabe von Sebastian)**: GT5 nicht aktiv; `USRDIR/EBOOT.BIN.orig` = Original hochgeladen,
`USRDIR/EBOOT.BIN` = `release/3p/EBOOT.BIN` (9477072 B). Rück-Download bytegleich. Nächster Schritt: GT5 vom
XMB starten → entweder Fehlercode (SELF abgelehnt) oder Menü → Split Battle mit Spieler 3.
