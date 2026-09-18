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

**PS3 lehnt das erste SELF ab (14:00)** → Original zurückgespielt (bytegleich verifiziert). Ursache gefunden:
im NPDRM-Kontrollblock waren beide OMAC-Hashes falsch, weil `NP_tid`/`NP_ci` in meiner Schlüsseldatei vertauscht
waren — der CID_FN-Hash des Originals (`6f6c156c…`) reproduziert exakt mit NP_tid = RPCS3 `NP_OMAC_KEY_3`
über ContentID(0x30)+"EBOOT.BIN". Zweiter Unterschied: scetool ließ die FW-Version im Digest auf 0 (Original
41000 = 4.10) → `tools/npdrm_fixup.py` setzt sie und verifiziert beide Hashes (das Original besteht die Prüfung
unverändert). Weitere, vermutlich unkritische Abweichungen: kein SCE-Version-Block/Typ-3-Section (ELF-Section
0x1D, 0x5352 B), leere LOAD-Segmente 3/4 nicht als Sections gelistet (`--skip-sections`). Erster
`--skip-sections FALSE`-Bau hatte fälschlich TLS/Param-Segmente verschlüsselt.
Neue EBOOTs (split3/split4) + Kontroll-SELF `EBOOT_plain_rebuild.BIN` (Original-ELF neu verschlüsselt) gebaut.

## 2026-09-05 15:30–19:00 — PS3: SELF akzeptiert, 3 Ansichten auf Hardware, Controller 3 steuert nicht

- Korrigiertes EBOOT (NP_tid/NP_ci getauscht, FW 4.10) auf die PS3 geladen → GT5 startet von der Disc
  ohne Fehler, `verify` = 250/250 gepatchte Wörter aktiv. **Split Battle mit Spieler 3: drei Ansichten,
  drei Autos auf echter Hardware** (Sebastian). Aber: Controller 3 (LED 3, Port 2) bewegt Auto 3 nicht,
  auch nicht wenn alle drei Pads vor dem Start verbunden sind. Mod-Log: entry 2 port=2 ctrlport=2.
- webMAN-Virtualpad (`/pad.ps3`) registriert sich als Port 1, wird von GT5 in-game aber ignoriert (nur
  XMB/Dialoge?). `/xmb.ps3$screenshot` funktioniert nur im XMB (hier: nicht verfügbar). `/play.ps3`
  startete zweimal den „Simple File Manager" statt der Disc — Fernstart von GT5 offen.
- Heap-Adressen sind auf PS3 und RPCS3 identisch (Entries 0x4FF13550, Slots 0x4FFC8300, Entry-Liste
  0x4FF3DBE0). Die 0xd8-Liste in der Spieler-Fabrik ist die **Teilnehmerliste** („PDI Entry0N",
  player_no bei +0x20), nicht die Pad-Liste.
- Pad-Pfad (RPCS3 cellPad-Trace): GT5 pollt jeden Frame `cellPadGetData` für Ports 0–3 (Schleife bis 7),
  `SetPortSetting(port,6)` für alle; Pad-Manager = globales Objekt **0x18ef8f8**: +0x00 max=7, +0x04
  now_connect, +0x0c connected[7], +0x28 setting[7], +0x44 capability[7], +0x7c alter Status, Daten je
  Port ab +0xa0 (Stride 0x84: len, button[0..]). Nach GetData prüft GT5 `button[1]`: High-Nibble muss 7
  sein, Low-Nibble (Wortzahl) 0xA/0xC-Verzweigung (RPCS3: 0x7C bei len 24). Trampolines 0xfa1070
  (GetData) ← 0xab37f4, 0xfa1118 (GetInfo2) ← 0xab364c, 0xfa0fc8 (SetPortSetting) ← 0xab37d0.
- `tools/ps3_padprobe.sh`: liest den Pad-Manager der Konsole (nur lesen) — im nächsten Test mit
  gedrückten Tasten an Pad 3 laufen lassen, um zu sehen, ob dessen Daten bei GT5 ankommen.

**Stand 19:10 / nächste Schritte (Sebastian abwesend, Hardware unangetastet, PS3 im XMB)**
- Pad-Modul (0xab2xxx–0xab3xxx) wird über Deskriptoren/vtables aufgerufen (keine `bl`-Aufrufer);
  Init 0xab3230 legt 7 Pad-Slots (+0x468, Stride 0xe0) an. Emulator zeigt für Port 2 keine Sperre —
  der Unterschied muss aus den Live-Daten der Konsole kommen (Gerätekennung/Status von Pad 3, Spielstand-
  Optionen).
- Nächster Hardware-Test (Sebastian anwesend, 3 Pads LED 1–3, ins 3P-Rennen):
  1. `PS3=192.168.1.11 ~/gt5re/tools/ps3_padprobe.sh 8` laufen lassen, dabei an Pad 3 Gas/Tasten halten
     → zeigt connected/setting/capability je Port und len/button[1]/digital je Port. Erwartung für ein
     echtes DS3 mit Setting 6: len=24, button[1]=7C. Abweichung bei Port 2 = Ursache gefunden.
  2. Wenn Pad 3 korrekt ankommt: Pad-Zuordnung pro Fahrer im Spieler-Objekt (0x3270-Objekt aus 0x170a38)
     untersuchen — dort den Port-Index lesen (Emulator: Objekt finden, Offset des `ctrlport` bestimmen,
     dann auf der PS3 vergleichen).
  3. Frage an Sebastian: ist Controller 3 ein originaler DualShock 3 (nicht Sixaxis/Nachbau)? Testweise
     die Pads tauschen (das als LED 3 verwenden, das vorher LED 1 war).
- Fernstart der Disc: `/play.ps3` startet auf dieser Konsole den „Simple File Manager"; für GT5 vom XMB
  aus muss vorerst jemand vor Ort ✕ drücken (oder webMAN-Konfiguration prüfen: „disc icon" Zuordnung).

**Spieler-Objekte im Emulator (19:00)**: drei 0x3270-Objekte an festen Adressen 0x4FA78000 / 0x4FA6C000 /
0x4FA48000 (Spieler 0/1/2; vtable 0x16d4ee8; +0x34 = Index, +0x2c → Unterobjekt 0x4FE5D690+i·0x98,
+0x3198/+0x31a4 = Index, +0x31a8 = Renneintrag). Eingabezustand liegt nicht im Kopf (+0x00..0x40 statisch);
+0xa4 kippte bei gehaltenem Kreuz auf Pad 2 in Objekt 2 UND 0 (bei Pad 0 gar nicht) → nur Hinweis.
`tools/ps3_padprobe.sh` liest Pad-Manager (primär) + diese Objekte.

### 2026-09-06 00:15–00:50 — Controller 3 steuert nicht: Ursache gefunden (Key-Config nur für Port 0/1)

Hardware-Sonde (Sebastian im 3P-Rennen, ✕ auf Controller 3 gehalten): Pad-Manager 0x18EF8F8 zeigt
Port 2 `digital2=0040` (✕ kommt an), Ports 0–2 connected, setting 6, capability 0x1F — identisch zu RPCS3.
Die Spieler-Objekte (0x3270 B, vtable 0x16d4ee8) liegen auf der PS3 **nicht** an den RPCS3-Adressen:
PS3 idx0 0x4FA76000, idx1 0x4FA48000, idx2 0x4FA28000 (RPCS3: 0x4FA78000/0x4FA6C000/0x4FA48000);
Sub-Objekte 0x4FE5D690/728/7C0, MOrg-Entries 0x4FF13550.., Fenster-Slots 0x4FFC8300 und Fensterobjekte
sind auf beiden Systemen gleich. `ps3_padprobe.sh` las daher falsche Objekte (Fixadressen entfernt → Scan).

Pad-Pfad im EBOOT (statisch, gleich auf PS3/RPCS3):
- 7 Geräteobjekte "PS3SIXAXIS port1..7" an 0x18EFD60 + port·0xE0 (vtable 0x171B108): +0x40 Port, +0x4c Status
  (2 = aktiv), +0x50 Capability, +0x54 Kopie der CellPadData. Update-Funktion 0xAB280C, Decoder 0xAB2E6C.
- 4 Handles "SuperPort SIXAXIS Fixed1..4" an 0x18F3F0C + i·0xC (vtable 0x171B230) → Gerät i.
  Lookup `getSuperPort(i)` 0xAB63C4 erlaubt i ≤ 3. MOrg-Entry i → +0x2c → Wrapper 0x18F3CE8 + i·0xC.
  ⇒ Die Engine-Seite kann 4 Pads; hier liegt der Fehler nicht.
- Nachtest im Emulator: F2 (Pad 3 ✕) erreicht Pad-Manager Port 2 und Gerät 2 (data 0x40), aber das
  Spieler-Objekt idx2 ändert sich nicht (Wortdiff 84 vs. 85 Kontrolle); n (Pad 2) → idx1 138, x (Pad 1) → idx0 140.
  **Der Fehler tritt also auch in RPCS3 auf** — die frühere Aussage „alle Pads lenken" war falsch.
- Ursache: `scripts/gt5/global_status/GameOption.ad`, `DeclareControllers()`: `declare_play_normal(controller,
  "SIXAXIS", 2, …)` deklariert die Tastenkanäle nur für `port < 2`; `bootstrap_phase3.ad` behandelt ebenfalls
  nur `controller_port < 2`. `gtengine::MController` (Natives 0x9AEB0 declare / 0x9AD98 getConfig / 0x9A38C
  setConfig, Singleton via 0x98D7C) hat für Port 2/3 keine Belegung → Eingaben werden nicht auf Gas/Lenkung
  abgebildet.
- Fix (Adhoc, `patch_arcade_v3.py` → createSplitBattle): für Ports ≥ 2 alle SIXAXIS-Kanäle deklarieren und
  `key_config.setConfig(key_config.getConfig(0), port)`. Build `mod_kc` (MOD_WINDOW_MAX=4), Test im Emulator läuft.

**Test mod_kc im Emulator (00:48)**: Absturz beim Rennstart, `Access violation reading 0x4` in 0x9B114
(native `MController::declare`). Der Wrapper holt über 0x98D7C → 0x48B15C den Controller-Kontext (statisches
Aggregat 0x17FDF60, Registry „GT-ALL") und ruft dessen vtable-Slot 0x10 = **0x48A8F4 `getHandle(port)`**:
`cmplwi r4,1; bgt → 0` sonst `0x17FDF70 + port*8`. Die C++-Seite hat also nur **zwei statische Port-Handles**
{vtable 0x16EB0B0, &Konfig-Vektor}; die Konfig-Vektoren (0x10 B, je 3 InputModes à 0x14 B mit Geräte-Listen)
liegen im Kontextobjekt (+0x24/+0x34), gebaut vom statischen Ctor 0x48A9D4 (Vektor-Ctor 0x48BD30 mit vtable
0x16B6720, Handle-Init 0x48AF24). Einzige Zugriffe auf die Slots: der Getter (+ Ctor/Dtor).
→ Der Adhoc-Fix allein reicht nicht; `declare(…, port=2, …)` crasht, und die Fahrer-Eingabe für Port 2/3 findet
ebenfalls keine Konfiguration. **EBOOT-Patch `keycfg4`** (`tools/gen_keycfg4.py` → `keycfg4_words.txt`, 38 W):
zwei weitere Handles + Vektoren im ungenutzten Rest des RW-Datensegments (memsz endet 0x19485B0, Seite bis
0x1950000 gemappt; NEW = 0x1948600), Ctor-Cave 0x1581140 (Hook 0x48ABA8) baut sie mit 0x48BD30/0x48AF24,
Getter komplett in Cave 0x1581100 (Hook 0x48A8F4 → `b`), erlaubt Port ≤ 3, Port 2/3 → NEW. Test-EBOOT
`eboot/out/EBOOT_test_keycfg4.BIN` (viewport + entries4 + win4 + keycfg4) im Emulator, Mod mod_kc aktiv.

**Emulator-Test keycfg4 + mod_kc (01:02) — Controller 3 steuert.** Statische Ctor-Cave hat die neuen Handles
gebaut (0x1948600: {016EB0B0, 01948610}, {016EB0B0, 01948620}, Vektoren mit je 3 InputModes wie Port 0/1).
Mod-Log: „keyconfig: SIXAXIS declared and port 0 config copied to port 2", kein Absturz, `load_sequence
finished`. Spieler-Objekte diesmal an 0x4FA74000/0x4FA68000/0x4FA32000 (Heap-Layout variiert je Lauf → Scan
nach vtable 0x16D4EE8 statt Fixadressen). Wortdiff je Objekt (idx0, idx1, idx2), Kontrolle [84, 47, 88]:
F2 (Pad 3 ✕) → [84, 52, **173**], F7 (Pad 3 Stick rechts) → [87, 83, **247**], n (Pad 2) → [84, **132**, 62],
x (Pad 1) → [**165**, 161, 63]. Bildvergleich bei 6 s F2: Fenster 3 (unten rechts) 59 % Pixel geändert,
Fenster 1 0,5 % → Pad 3 fährt das Auto in Fenster 3. Belege `doc/emu_3p_pad3_*.png`.

**4P-Gegentest keycfg4 + mod_kc (01:12)**: `ports: 4`, Key-Config für Port 2 und 3 gesetzt, `load_sequence finished`,
kein Absturz. Spieler-Objekte 0x4FA82000/0x4FA6A000/0x4FA46000/0x4FA3A000 (idx0..3). Wortdiff (idx0..3),
Kontrolle [50, 9, 50, 24]: KP_Multiply (Pad 4 ✕) → [56, 97, 61, **109**], F2 (Pad 3 ✕) → [91, 94, **145**, 69],
KP_Divide (Pad 4) → [55, 78, 65, **156**]. Die Nebenänderungen (idx1 bei Pad 4, idx0 bei Pad 3) passen zur
Startaufstellung: Auto 4 steht hinter Auto 2, Auto 3 hinter Auto 1 → Auffahrkollision beim Gasgeben.
Bildvergleich Pad 4: Fenster 4 (unten rechts) 59 %, Fenster 2 71 % (gerammt), Fenster 1/3 ≈ 20 %.
Beleg `doc/emu_4p_pad4_accel_2026-09-06.png`. Release-Ordner 3p/4p aktualisiert, Commit 178ac64.
Nächster Schritt: PS3 — `release/3p/EBOOT.BIN` + `release/3p/mod/pdipfs/*` hochladen
(`tools/deploy_ps3_release.sh`, erst nach Sebastians Freigabe), Hardware-Test, dann Tag 3p-v1.

## 2026-09-06 01:20 — Hardware-Test 3P bestanden

Sebastian: GT5 beendet, `tools/deploy_ps3_release.sh release/3p` (EBOOT.BIN 9477184 B + 5 Overlay-Dateien,
alle Größen ok), GT5 gestartet, 3P-Rennen: **„ja p3 kann steuern und fahren"** — drei Ansichten, drei Autos,
Controller 3 fährt Auto 3. Fern-`verify` (288 Wörter über webMAN getmem) lief während des Rennens in den 10-min-Timeout — nicht wiederholt,
Sebastians Fahrtest ist der Beleg.
Damit ist Auftrag 3 (3-Spieler-Splitscreen auf der PS3) erfüllt → Tag `3p-v1`.
Offen: 4P-Hardware-Test mit `release/4p` (gleiches Upload-Skript, vier Controller nötig), dann Tag `4p-v1`.

## 2026-09-06 (früh) — Hardware-Test 4P bestanden

Erster Upload-Versuch scheiterte, weil die PS3 aus/nicht erreichbar war (Skript meldete fälschlich „kein
Backup" → Skript korrigiert, 1be9b09). Zweiter Versuch: `deploy_ps3_release.sh release/4p`, alle 6 Dateien ok.
Sebastian: **„p3 und p4 können steuern"** → vier Ansichten, vier Autos, Controller 3 und 4 fahren → Tag `4p-v1`.

Neue Wünsche von Sebastian: (1) Autoauswahl auch für Spieler 3 und 4, (2) Streckenkarte in allen vier
Ansichten, (3) Tachometer ausblenden.

## 2026-09-06 05:40–06:15 — HUD in Quadranten, Autoauswahl für Spieler 3/4

- `patch_hud_quad.py` (OnboardMeterRoot.ad): neuer Zweig `sWinN >= 3` — Fenster 0 behält die ROOT-Widgets,
  Fenster 1..3 bekommen Kopien in `DivWork` + weiteren Containern (`sQuadDivs`, einmal erzeugt, wiederverwendet)
  an ihrer Quadranten-Position (4 Fenster TL,TR,BL,BR; 3 Fenster TL,BL,BR). Jedes Fenster ruft
  `CourseMapFace.begin(…, k)` und `RaceDisplayFace.begin(…, k)`; Tacho/Drehzahl/Gang aus (`Parette` unsichtbar,
  `carmeter_disp = false`). Emulator 4P (mod_hud): Karte + Position/Runde/Zeiten in allen vier Fenstern, kein Tacho,
  kein Absturz (`doc/…` folgt). Kosmetik: Rundenzeit (Info::Current) überlappte „Total Time" → nach (250,100)
  verschoben; ein Vorschaustreifen (Widget noch nicht identifiziert) sitzt mittig oben in jedem Fenster.
- Autoauswahl: `CarSplitBaseRoot.check_page_status` fragt nach Runde 1 („Spieler 3/4 fährt mit?"), merkt sich
  Spieler 1/2 (`rememberSplitPlayers`), schließt die Seiten und startet die Split-Autowahl als Runde 2 für
  Spieler 3/4; danach `restoreSplitPlayers` (Slots 0/1 zurück auf Spieler 1/2). `createSplitBattle` nimmt die
  gemerkten Autos/Fahrer (`mod_cars/mod_drivers`), Ersatzauto nur noch als Fallback.
- Versuch, die Panes in Runde 2 per `event_mask = 4/8` an Pad 3/4 zu binden: beide Panes taub für alle Pads
  (Maskenbits ≠ Pad-Ports) → zurück auf 5/10: Controller 1 wählt für Spieler 3, Controller 2 für Spieler 4.
  Sub-Kontexte: `Context1P/2P = ContextMain.getSubContext(0/1)`; native `getSubContext` 0x57C668 → 0x5653A0.

**Emulator-Test mod_sel (06:16)**: Runde 1 (Pads 1/2) → Dialoge P3 ja / P4 ja → Hinweis-Dialog (OK; braucht einen
längeren Tastendruck, Navigator-Zustand `okdialog` ergänzt) → Runde 2 → Optionen → Rennen: 4 Einträge, alle mit den
in Runde 2 gewählten Autos (code 1536 statt Ersatzwagen 1388), `load_sequence finished`, kein Absturz — vier gleiche
Autos laden also problemlos (die frühere „eigenes Modell nötig"-Annahme stammte aus der Zeit der kaputten Entries).
Pads im Rennen: KP_Multiply → idx3 100 (Kontrolle 6), F2 → idx2 100; Kollisions-Nebenwirkungen wie zuvor.
HUD-Korrektur (Rundenzeit nach (250,100)) im selben Build. Release-Ordner 3p/4p aktualisiert (mod aus mod_sel),
Belege `doc/emu_4p_quad_hud_2026-09-06.png`.

**Optionsdialoge für Spieler 3/4 (06:20–06:30)**: In Runde 2 bekam die linke Seite (player_no 0) den
Spieler-1-Dialog mit Rennoptionen (Runden, Low-mu, Schaden) und hätte über den `player_num == 0`-Zweig in
`CarSplitRoot.cb_selected_car` die Renneinstellungen von Spieler 1 überschrieben. Fix in `setup_driving_option`
(`player_no == 0 && mod_round == 1`) und in CarSplitRoot (gleiche Bedingung). Emulator: beide Runde-2-Dialoge
zeigen nur Spieler-Einstellungen (Screenshots r2_2/r2_4). Der Dialogtitel sagt weiter „player 1/2" (aus
`window_id`, das auch die Pane-Position bestimmt; Setting-Projekt, nicht Teil der Mod) — kosmetisch.

## 2026-09-06 06:35–07:30 — Innenansichten (Cockpit/Windschutzscheibe) im Split-Modus: Analyse

- SELECT wechselt im Split-Rennen für jeden Spieler das eigene Fenster (Bildvergleich: Pad 2 → TR, Pad 3 → BL,
  Pad 4 → BR), aber nur zwischen zwei Sichten. Kamera-Kontext pro Fenster: `*(window+4)` (0x422BE000,
  0x4230E000, 0x4231E000, 0x4232E000; Fensterliste via MOrg+0x2c0). Sichtindex/Mount im Kontext bei
  +0x174/+0x17c (Kopien +0xDB84/+0xDB8C, +0xE1E4/+0xE1EC): Split: Index 3↔0 (Mount 2↔0, Typ 1↔0);
  1P-Rennen: Index 0,1,2,3 (Mount 0,1,3,2; Typ 0,26,6,1) → im Split fehlen genau Index 1/2 = Mount 1/3 =
  INCAR (Windschutzscheibe) und DRIVER (Cockpit).
- Engine-Pfad: SELECT → Pad-Modul (Key-Config-Button 0x20) → Kamera-Kontext+0xE3C0 Flags (0x48A05C) →
  Sichtwechsel 0x467A14: Zähler `table->vt[+0x1c]`, Sicht per Index `0x46432C`, Zulässigkeit `0x464460`
  (Bitmaske aus vier virtuellen Methoden des Sichtobjekts), Anwenden `0x467488`. Wo die Liste im Split
  gekürzt wird (Liste bauen / Zulässigkeit), ist noch nicht gefunden; Kandidaten-Scans (li r4 0/1/3/2,
  Bit-4-Tests, WM window_max-Leser) ohne Treffer. Klassen: ChaseViewCamera(2), PSPBonnetViewCamera,
  InCarCamera, DriverCamera, BackViewCamera (vtables 0x16EAC18..0x16EAD08), CameraOnboard 0x16EADD0.
- Skript-Umweg getestet (`MOD_VIEW_EXPERIMENT=1` in patch_race_log_w6.py): `ORG.changeSpectatorCamera(ONBOARD,
  DRIVER, 0)` am Ende des Ladevorgangs wird ausgeführt (Log), ändert die Sicht aber nicht; Tastenereignisse
  (TRIANGLE/SELECT) erreichen `RaceRoot.onKeyPress` während der Fahrt nicht (kein „key event"-Log);
  der Poll-Thread loggt in diesem Build nicht (Ursache unklar). → Ein reiner Skript-Weg fällt aus, es braucht
  einen EBOOT-Patch an der (noch zu findenden) Listen-/Zulässigkeitslogik. Aufwand offen, dazu Renderlast
  von 3–4 Cockpits auf der PS3 unklar.
- Nebenprodukte: `tools/nav.sh` kennt `MODE=single` (1P-Rennen) und den Zustand `okdialog`.

## 2026-09-06 09:20 - PS3 freeze when mounting a game (read-only diagnosis, console 192.168.1.11)

Sebastian: every game freezes when mounted via webMAN MOD 1.47.48 (CFW 4.92 Cobra 8.5); last case
LittleBigPlanet Karting; console ran all night. Nothing on the console was changed.

Findings (PS3 clock is wrong: it shows 2025-06-08 while the real date is 2026-09-06; times below are
console time, offset about +6h16m to real time):
- `wmtmp/last_game.txt` 02:48:12 = LBP Karting mount; `/dev_hdd0/tmp/turnoff` (created by VSH at boot)
  02:49:03 = next boot. So the console was restarted 51 s after the mount. `crash_report/vsh` dir
  mtime 02:49 (empty) = a VSH crash report was written and consumed -> VSH crash, not a kernel hang.
- A physical disc (NFS Carbon BLES00020) is in the drive. `/dev_bdvd` lists the real disc;
  `/dev_hdd0/tmp/game/ICON0.PNG` (XMB disc icon cache, 02:49:05) is byte-identical to the NFS Carbon
  ICON0. webMAN's cpursx line "/dev_bdvd -> <iso>" only echoes last_game.txt (cpursx.h:699), it does
  not prove a mount. Cobra source (storage_ext.c mount_ps3_discfile): with a real disc inserted
  `total_emulation = 0` and the real PS3 disc keeps `effective_disctype` -> ISO mount + real PS3 disc
  is an unsupported mixed state. Prime suspect.
- Thermal: CPU 76 C / RSX 73 C at 24 % fan before the reboot (fan control "Auto at 80 C", min 25 %);
  69-70 C at 27 % right after boot. Secondary suspect, needs fixing anyway.
- `/dev_hdd0/PS3ISO` holds 4367 `.dkey` files (full redump key set) next to 23 ISOs; 13 ISOs are
  encrypted redump images with matching keys (LBP Karting: EBOOT.BIN sector 0x65c19d is in the
  encrypted region, dkey present). Slows every scan, not a freeze cause by itself.
- VSH plugins: webftp_server.sprx (1.47.48 full) + psnpatch.sprx. No game process running.
  Startup counters: 2,767 ON / 2,704 OFF (63 improper shutdowns). 10.1 GB free.
- Sebastian confirmed: all games freeze, LBP Karting last; console ran all night.

Proposed (needs his OK, changes the console): eject the disc, then mount LBP Karting via the web UI
while pinging; lower fan target to 65-70 C / min 40-45 %; move the unused .dkey files out of PS3ISO;
fix the clock.

### 2026-09-06 09:45 - follow-up: disc theory dropped, dkey files moved

- Sebastian: the freeze also happens without a disc in the drive (tested earlier by him).
- With his OK: moved 4572 unused `.dkey` files from `/dev_hdd0/PS3ISO` to `/dev_hdd0/dkeys/`
  (FTP RNFR/RNTO, 157 s, 0 failures). 15 dkeys whose ISO exists stayed in PS3ISO. Full listing
  showed 4620 entries (the earlier curl LIST was truncated at 4397): 28 ISOs, 3 CUE, 2 PNG.
  `LittleBigPlanet2.iso` is a 134 MB fragment (2026-05-24), `BCES00850 - Little Big Planet 2.iso`
  (20.6 GB) is the complete one.
- webMAN GitHub issues checked: #1279 (freeze 4.92.2 + 1.47.48 with encrypted ISO + key, Cobra
  side), #1386 (freeze while loading ISO, overheating message), #1303 - aldostools' standard advice:
  test with fan control in SYSCON/manual mode (dynamic fan control can freeze), remove other
  plugins (here psnpatch.sprx), clean reinstall.
- Temperatures 24 min after boot: CPU 69 C / RSX 67 C at 27 % fan.
- Prepared `tools/ps3_mount_probe.sh` (mount via /mount.ps3 while logging ping/HTTP/temps/bdvd);
  not run yet - needs Sebastian's OK because it mounts a game.

### 2026-09-06 09:40 - freeze tests 1+2 by Sebastian, psnpatch disabled

- Test 1 (Sebastian, XMB mount, dynamic fan): freeze again -> hard reset.
- Test 2 (Sebastian set fan to manual 40 %, then mounted again): freeze again -> hard reset.
  My remote mount probe (tools/ps3_mount_probe.sh) was not run - he mounted himself both times.
- Console change with his OK: `/dev_hdd0/boot_plugins.txt` now has `#/dev_hdd0/plugins/psnpatch.sprx`
  (Cobra load_boot_plugins passes every non-blank line to prx_load_vsh_plugin, so the '#' line simply
  fails to load). Original saved as `/dev_hdd0/boot_plugins.txt.orig` and locally in the job tmp dir.
  Restarted via /restart.ps3 at 09:39; back after ~30 s; PS3MAPI plugin list: slot 1 webftp_server
  only, slot 2 NULL. Fan still manual 40 %.
- Next: Sebastian mounts again (test 3, without psnpatch). If it still freezes: clean reinstall of
  webMAN MOD (uninstall pkg, reboot, install 1.47.48 again) or test with the plugin unloaded
  (`/unloadprx.ps3`? no: use `L3+R2+R3` UNLOAD WM combo) and mount via multiMAN.

### 2026-09-06 09:50 - webMAN clean reinstall (remote) - plugin was NOT corrupt

Sebastian: test 3 (psnpatch disabled, manual fan 40 %) also froze on mount. Asked me to do the
uninstall + reinstall. A true uninstall would sever remote access (no FTP/HTTP without webMAN), so
did a clean reinstall over the top instead:
- Downloaded official webMAN_MOD_1.47.48_Installer.pkg (15187040 B, aria2c) from aldostools' GitHub
  release. content id EP0001-UPDWEBMOD_00-..., 4626 items.
- Backed up running /dev_hdd0/plugins/webftp_server.sprx locally (sha1 f88f9f31...) and as
  webftp_server.sprx.bak on the console.
- Uploaded pkg to /dev_hdd0/packages/, installed via `http://PS3/install_ps3/<pkg>` -> extracted fresh
  to /dev_hdd0/game/UPDWEBMOD (all mtimes -> 03:34).
- KEY FINDING: fresh USRDIR/webftp_server_full.sprx is byte-identical to the running plugin
  (both sha1 f88f9f31c1110147d4afa25e699a57a284903da6, 352353 B). The active webMAN was already the
  pristine official file -> webMAN was not corrupt, a reinstall cannot change the mount freeze.
- Rebooted via /restart.ps3; back in ~35 s. Slots: only webftp_server (psnpatch stays off). Fan 40 %.

Conclusion: freeze reproduced with dynamic fan, manual fan, psnpatch off, and now on a verified-
pristine webMAN. webMAN only calls Cobra's mount syscall; the hang is at Cobra/CFW or hardware level.
Real next steps (all need Sebastian, none remote-safe): reflash/repair the CFW (4.92 Evilnat Cobra
8.5) PUP; full cold shutdown + dust/thermal-paste (149 d uptime, ~70 C); test booting the physical
NFS Carbon disc directly vs a mounted ISO to split drive vs Cobra emulation.

### 2026-09-06 10:15 - CFW 4.93 Evilnat Cobra 8.5 [CEX] prepared for reflash

Sebastian chose to reflash the CFW (webMAN ruled out) and to go to 4.93 instead of 4.92.2.
- Source: Evilnat's official MEGA folder (linked by brewology post p=4840 by aldostools and by
  consolecrunch): "CFW Evilnat 4.93/CEX/CFW 4.93 Evilnat Cobra 8.5 [CEX].rar", 215766279 B, folder
  marker "Updated 31-03-2026". Downloaded with a small Python MEGA public-folder client
  (job tmp/mega_public.py, pycryptodome added to ~/gt5re/.venv). rar test OK.
- PS3UPDAT.PUP 215764316 B, md5 d3af31ce6bdbc6790a5504cf8b3da1b2 = bundled md5.txt; sha1
  5075240b714dbb789005a1ed0918e76df9fcc5d2; header SCEUF, version.txt "4.93 Evilnat [CEX]", 9 entries.
  (archive.org third-party copy Evilnat_4.93_CEX.PUP md5 a69ec3b1... is an older build.)
- Extracted to ~/Downloads/CFW-4.93-Evilnat-CEX/ (README.txt, md5.txt, PS3/UPDATE/PS3UPDAT.PUP).
- Note: GitHub account "EviInat" (capital I) mimics Evilnat; brewology's github.com/Evilnat link is
  dead; Evilnat's real GitHub is xXEvilnatXx (Cobra-PS3, xai_plugin, flash-writer). Not used.
- USB sticks: first Intenso Micro Line (USB 2.0) was NTFS with 5.6 GB of his data -> not touched.
  Second Intenso Micro Line (serial ...0558, bcdUSB 2.00, 480 Mbit/s, MBR, FAT32, 22 MB used) ->
  PS3/UPDATE/PS3UPDAT.PUP copied, md5 verified on the stick, unmounted.
- Console prep before flashing: eject NFS disc, nothing mounted, fan manual 40 %, psnpatch off.

### 2026-09-06 12:45 - PS3 now on 4.93 Evilnat Cobra 8.5 (Sebastian flashed it), webMAN 1.47.48 alive

cpursx.ps3 (read-only): "Firmware: 4.93 CEX Cobra 8.5", webMAN 1.47.48s MOD, uptime 40 min, CPU 69 C / RSX 67 C.
Next: Sebastian mounts a game to see whether the freeze is gone.

### 2026-09-06 11:30 - freeze persists on 4.93; webMAN downgrade test to 1.47.47 (Sebastian's OK)

- Sebastian: mounting still freezes on 4.93 Evilnat. He tried to install the old webMAN himself and failed.
- Found: installing the webMAN installer PKG through webMAN (/install_ps3) also auto-copies a plugin into
  /dev_hdd0/plugins: my 09:50 reinstall of 1.47.48 had silently switched the active plugin from the "full"
  variant (352353 B, f88f9f31) to "rebug_cobra_ps3mapi" (329109 B, 1664b7a7) - cpursx header showed
  "[Rebug-PS3MAPI]" afterwards. So the freeze was reproduced with two 1.47.48 variants (full this morning,
  rebug on 4.93). Overclocking (new in 1.47.48) excluded: wm_config.bin bytes 628/629/888/889 are 0 -> no
  LV1 writes (feat/clock.h overclock() requires 300..1200 MHz).
- Installer 1.47.48 also added /dev_hdd0/game/{LOADWMMOD,RELOADXMB,PKGLAUNCH,PS2CONFIG}, wm_res/ps3mon.sprx,
  wm_lang, wm_icons, mygames.xml at 08:35-08:45 and reset settings (re-saved 09:02 by Sebastian).
- Downgrade: installed /dev_hdd0/packages/webMAN_MOD_1.47.47_Installer.pkg.841.v1.47.47g_brewology_com.pkg
  via /install_ps3 -> USRDIR 05:19 (PS3 clock), active plugin now 1.47.47 rebug_cobra_ps3mapi (320811 B,
  sha1 346fdb5f554210f0336ed576dc6bb36c9b753e00); wm_config.bin kept. Restarted for the mount test.

### 2026-09-06 11:48 - freeze also with 1.47.47 and with a folder game (GT5); test T1 = XMB pushlist aside

- Sebastian: LBP Karting froze again with webMAN 1.47.47; GT5 (folder, worked at 07:00) freezes too; the
  console is completely dead during the freeze (no ping). Every freeze touches crash_report/vsh (report is
  consumed at the next boot). Cobra config /dev_hdd0/vm/cobra_cfg.bin is 24 B, plain values. Pending
  XMB download tasks d0/d1.pdb look generic.
- Suspect that survives CFW reflash + webMAN version + config: files the installer touched at 08:33-08:45,
  esp. /dev_hdd0/vsh/pushlist/patch.dat + game.dat (modified 08:39 during the installer run, new
  UPDWEBMOD/LOADWMMOD entries; UPDWEBMOD entry has an odd 0x80 flag). The XMB consults the pushlist on
  disc insert (update badges) -> possible crash on a malformed entry.
- T1 (with backups in job tmp/vshbak): renamed both to *.bak (11:45), restarted via webMAN, XMB up 11:46
  with only the .bak files present. Sebastian mounts GT5 next.
- Fallback T2: rename the new app folders /dev_hdd0/game/{LOADWMMOD,RELOADXMB,PKGLAUNCH,PS2CONFIG};
  T3: reset wm_config.bin.

### 2026-09-06 12:00 - STRONG lead: internal HDD failing (sustained-read test)

- Discriminator from Sebastian: real Blu-ray discs boot fine; every HDD mount (ISO + folder GT5) freezes
  the whole console (no network). Survives: webMAN 1.47.47 + two 1.47.48 variants, psnpatch off, dynamic +
  manual fan, CFW 4.92->4.93 reflash (fresh Cobra), disc in/out, overclock (config zeros), pushlist removed,
  wm_config intact. mygames.xml "XML errors" are a FALSE alarm (webMAN's format is intentionally non-strict).
- Sustained sequential read of GT.VOL (12.1 GB, the file GT5 streams at load) over FTP:
  chunk0 50MB @ 0.6 MB/s (85 s), chunk1 short read 42MB @ 0.9 MB/s, chunk2 EOFError (webMAN FTP died).
  A healthy HDD here does several MB/s; earlier today small reads and the 21 GB NFS mirror read fast.
  0.6 MB/s + short reads + connection death = classic failing-sector retry pattern on the internal 2.5" HDD.
- MK64 homebrew (reads ROM/data from HDD) also froze -> anything that streams from the internal HDD hangs;
  optical-disc boot bypasses the HDD and works. Conclusion: the internal HDD is very likely dying.
- I never mount games; all my probes are read-only FTP. Stopped heavy reads to avoid stressing the drive.
- Recommend: back up savedata now (still partly readable), then replace the 2.5" SATA HDD; run a full CFW
  reinstall onto the new drive. Left the console as found (pushlist restored, 1.47.47, psnpatch off, fan 25%).

### 2026-09-06 12:45 - PS3 freeze: narrowed to webMAN's XMB mount path; Sebastian considers it solved (mmCM works)

- HDD excluded (21 GB copied from Blu-ray in 40 min this morning; my FTP read speeds were WLAN-limited ~0.4-1 MB/s,
  on-console copy is a hard link so not a throughput test; /md5.ps3 not compiled in). External Cobra stage2: none
  (/dev_flash/sys/stage2.bin from the PUP). boot_history.dat: no mounted game ever reached launch -> crash at the
  mount action. mmCM (BLES80608, 04.91) mounts and starts LBP Karting fine now; his earlier mmCM attempt froze
  (before the dkey move / downgrade / reflash). webMAN column entries use module_name idle_plugin +
  module_action /mount_ps3/... = webMAN's path-mapped wm_proxy.sprx loaded INTO the XMB. Remaining split:
  XMB-side proxy load vs webMAN's mount_game() -> decisive test = mount from the PC browser (web UI). Not done.
- Console left: webMAN 1.47.47 rebug variant, psnpatch off, pushlist restored, fan 25 %, temp copies deleted.

### 2026-09-18 - Start countdown per window and a car meter per window (3P/4P)

Sebastian: the start countdown is gone in 3P/4P and every player wants a speed readout.
All work done in RPCS3 with the 4P patch set (`patch_config.yml`: viewport count 4, MOrganizer
player entries x4, window slots x4, MController key config - the 3P-only patches stay off).

**Countdown.** `RaceRoot.onCountDown` does fire in a 4P race (log: count 6..1, `winmax=4`), so
nothing suppresses the callback. GT5 has exactly one `Info::CountDown` (256x256, centred on the
1920x1080 screen) plus two dead position templates in `RaceRoot::hidden` (`1P_CountDown` y=96,
`2P_CountDown` y=636 - referenced by neither the scripts nor the EBOOT). With four viewports that
single widget sits exactly on the crossing of the window borders, which is what "no countdown"
looks like from the couch.
`patch_countdown_split.py` gives every window its own: at the first countdown tick
`modSplitCountDownSetup` appends copies of `Info::CountDown` and `Info::Go` to ROOT and centres them
in their quadrant (4 windows TL/TR/BL/BR, 3 windows TL/BL/BR - the HUD order);
`onCountDownDefault` shows them, `Go_Message` drives the GO/START copies, and the stock widget is
hidden while the copies are up. `onStartVehicle`, `onOvertakeRestart` and `resetDisplay` clear them.
Two windows or fewer take the stock path untouched.
Evidence `doc/emu_4p_countdown_2026-09-18.png` (3-2-1 in all four windows, START likewise).

**Car meter.** The native `MRaceDisplayFace` fills the meter widgets it finds *by name* inside the
container passed to `begin()`; `Speedmeter`, `Tachometer`, `DigitalSpeed` and `Indicator` are all
children of `Panel` (760x212). `Panel` was not in the quadrant patch's copy list, so switching
`carmeter_disp` back on only gave window 0 a meter - one 1P panel across the middle of the screen
(`doc/emu_4p_meter_center_2026-09-18.png`). Fix in `patch_hud_quad.py`: `Panel` joins the widget
list copied into every window container, is scaled to 0.6 (456x127) and placed at (100, 358) inside
the quadrant. The scale is applied around the widget centre, so those coordinates put the panel
centred and flush above the lower quadrant edge. `appearPanel`/`disappearPanel` now also reach the
extra containers (`sQuadDivs`), otherwise the panels of windows 3 and 4 never fade in.
`MOD_HUD_SPEED=0` builds the earlier meterless HUD.
Evidence `doc/emu_4p_meter_2026-09-18.png`.

**Tooling.** `tools/shot.sh` now runs `import` under `timeout 10`: `import` grabs the X server while
it captures, and when RPCS3 died mid-capture the grab froze Sebastian's whole desktop until the
stuck process was killed by hand. `tools/build_mod.sh` runs `patch_countdown_split.py` as well.
`race.mproject` unpacked to text with `adhoc mproject-to-text` (`mproj_txt/race.txt`) - that is how
the widget geometries above were read; note the CLI wants a FILE for -i/-o, not a folder.

Open: nothing tested on the console yet - `release/3p` and `release/4p` carry the new overlay,
the hardware test (upload + 4 pads) is still pending.

### 2026-09-18 (later) - All cars and all courses in the arcade lists

Sebastian wanted Ferrari/BMW/VW and the Nordschleife in split screen. Everything is on the disc;
three gates keep it out of the arcade lists, all three are lifted in `patch_arcade_unlock.py`
(`MOD_ARCADE_UNLOCK=0` builds the stock behaviour):

1. **Cars.** The "Arcade Only" tab calls `CarData::ArcadeModeGT5::getCarList()`, which appends
   `arcade = 1` to the spec DB query - a few hundred of the ~970 cars. `CarRoot.ad` and
   `CarSplitRoot.ad` now call `CarData::getCPPListImpl(nil, nil, nil, nil, "pp", "ASC", nil, true)`
   instead, i.e. the same query without that condition. Note the condition list must be `nil`, not
   `[]`: `createWhere` does `conditions.push(additional_conditions.join(" AND "))` and an empty
   array would produce a bare `WHERE`.
   Verified in the emulator: the split car select now offers e.g. Golf VI R '10 and
   Corvette Z06 (C6) RM '06, neither of which was in the arcade list before.
2. **Courses.** `CourseRoot.getCourseCandidates` drops every course whose `COURSE_AVAILABLE` save
   flag is unset. That bitfield (`GameFlags.ad`) covers exactly topgear, nurburgring,
   nurburgring_24h, nurburgring_vln, nurburgring_daynight, nurburgring_24h_daynight, spa, spa_wet,
   newindoorkart(+short, +reverse), routex, routex_oval and the motegi layouts - the Nordschleife
   among them, while `nurburgring_GP`/`nurburgring_dtm` have no flag and are always listed. That is
   exactly the "two GP layouts but no Nordschleife" that Sebastian saw. The check is removed; all of
   those courses ship in the volume (checked against `entries_mod.txt`).
   Verified: Kart Space and Spa-Francorchamps are in the list now.
3. **Weather courses in a split battle.** The stock code greys out every course whose weather can
   change - the Nordschleife is one. Instead of disabling them, the course parameter is pinned to
   sunny (`rain_/snow_situation_ = false`, `weather_changeable_ = false`,
   `decisive_weather_ = SUNNY`); `createSplitBattle` then takes `decisive_weather_` into the race
   parameter, so the race runs with fixed weather and no dynamic weather system in split screen.

Still untested: a 4P race on the Nordschleife (memory/performance with four viewports on a 20 km
track) and a Standard car in a 4P race. A 2P race with the unlocked lists started normally.
