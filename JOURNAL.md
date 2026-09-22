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

### 2026-09-19 - GT6 cars in GT5? Car list diff and MDL3 format survey (no game change yet)

Sebastian downloaded GT6 (BCES01893, disc 1.00, `GT.VOL` 15.4 GB) to the external btrfs partition and
asked which GT6 cars GT5 lacks and whether they can be converted - the Tesla Model S first.
`/` has only ~600 MB free, so all GT6 work lives in
`/run/media/sebastian/2e638a7f-26db-4e89-9446-81d688464798/gt6work/` (never unpack the volume fully;
`GTToolsSharp unpack --indices <FileIndex...>` extracts single entries, `listfiles` gives the indices).

**Car list.** GT6 spec DB = `specdb/GT6/DB0106.dat`, SQLite, Salsa20 (`cryptsalsa -k` with
`KeysetStore.SPECDB_KEY`). GT5 labels read from `GENERIC_CAR.idi` (`gt6work/idi.py`).
GT6 1.00 has 1227 cars, GT5 2.17 has 1149; 1069 share label *and* ID. **158 GT6 cars are not in GT5**
(155 premium) -> `gt6work/gt6_cars_not_in_gt5.tsv` (id, label, model code, name). None of them reuses a
model file GT5 already ships (checked `car/race/<ModelCode>` against `volume_entries.txt`), so there
are no "spec DB only" ports. Tesla Model S Signature Performance '12 = ID 1896, model 02360002.

**File layout.** GT5: `car/{hq,race,interior,info,meter}/<model8>` + `wheel/{hq,race}/<model8>[.NN]`.
GT6: `car/<maker4>/<car4>/{hq,race}/{body,body_s,wheel}`, `interior`, `info`, `meter`.
The Tesla Roadster (02360001) exists in both games - the Rosetta pair for any converter work.

**Format.** Header layout (0xE4) is identical, but:
- GT5 files are MDL3 **v8** (disc) / **v9** (2.x DLC cars); GT6 files are **v14**.
- GT6 moves vertex/index data out of the model into `body_s`: raw-deflate chunks, referenced by a
  table at header+0xDC (6 named entries for the Roadster) that PDTools does not parse and GT5 files
  leave 0. `shapeStreamMap` (header+0xAC) is 0 in both games' car files.
- GT6 uses packed meshes (PMSH keys: 0x69 in the Roadster race body, none in GT5 v8; the v9 DLC files
  have a PMSH header but no keys) and only 9 FVF definitions where the GT5 Roadster has 0x59.
- Shaders/materials are compiled per game and bundled in the model.
- `info` is `CAR5` in GT6; `meter` of the Roadster is byte-size identical in both games.
- GT5's MDL3 fixup routine (around 0x8ca800..0x8cd000) only branches on version <= 1/2/3/5/6/7; there is
  no upper version gate, i.e. a v14 file would be walked with the v8/v9 layout and never get its
  `body_s` data.
Community state (GTPlanet thread 425706, Nenkai's modding hub): nobody has ported GT6 cars to GT5;
model creation is "not possible at the moment".

**Conclusion.** No drop-in. Needs a v14 -> v9 downgrade converter (inline `body_s`, PMSH -> plain
FVF shapes, material/shader remap) plus new spec DB rows (~20 Huffman `.dbt` tables), names, sound,
thumbnails. Waiting for Sebastian's go before starting that.

### 2026-09-19 (morning) - GT6 -> GT5 car port: test path in RPCS3, version-gate probe

Sebastian gave the go for the converter, Roadster first. Tooling (all on the external disk,
`gt6work/`): `build_cartest.sh <name> [volpath=file ...]` builds the usual 4P Adhoc mod plus
arbitrary replacement files, with the arcade car list reduced to one spec DB label (script-side
filter via `MSpecDB::getCarLabel`, default `tesla_roadster_08`); `run_cartest.sh <name>` deploys it,
boots GT5 (`--no-gui`), walks to a 1P arcade race with `nav_single.sh`/`nav_to_car.sh`
(copy of `tools/nav.sh`: three courses to the right = High Speed Ring, because the unlock patch puts
Kart Space first and a kart-only course leaves the car list empty - that, not the SQL filter, was
the "There are no cars to select" I first ran into), and stores menu/cockpit/roof/chase shots in
`gt6work/shots/<name>/`. Select (`space`) cycles bumper -> cockpit -> roof -> chase.

| test | car/race/02360001 | result |
|---|---|---|
| `t_base` | stock | Roadster in menu, cockpit and chase view - reference shots `shots/t_base4/` |
| `t_ver14` | stock v8 file, version field (0xC) patched 8 -> 14 | loads and renders exactly like stock |

So GT5 2.17 has no upper MDL3 version gate (matches the disassembly: the fixup routine only
compares the version against 1..7). What keeps a GT6 file from loading is structure, not the number.
Note: `car/race/<id>` is what the race uses; the menu shows `car/hq/<id>` (not replaced yet).
Reference material fetched to `gt6work/ref/`: Nenkai's 010 templates (incl.
`MDL3SeparateCarData.bt` = the `body_s` table) and current PDTools. `gt6work/sepdata.py` parses the
table (stream struct stride is 0x18, not what the template says) and inflates `body_s`:
entry "/" = base car (26 mesh chunks + 2 texture chunks), `custom_*` = GT6 custom parts.
Nine parallel analysis notes (header/commands, VM, shapes/FVF, PMSH, body_s, TXS3, materials,
shaders, GT5 loader RE) are in `gt6work/notes/*.md`, each with an adversarial verification section.

**Swap test (same morning).** `t_swap`: `car/race/02360001` := GT5 `00010002` (yellow Mazda) -> the race
shows the Mazda under the "Tesla Roadster" entry while the menu still shows the Roadster (menu =
`car/hq`). That proves the PDIPFS replacement of `car/race/<id>` really reaches the renderer, so the
`t_ver14` result counts: no upper version gate. `GTToolsSharp pack` also accepts a path that is not in
the TOC yet (`Adding new file to TOC: car/race/02360002`) - not tried in game so far.

**Analysis verdicts** (`gt6work/notes/understand_result.json`): all core findings confirmed by the
adversarial pass; refuted sub-claims are corrected in each note's "Verification" section. Key facts:
GT5 has no PMSH code at all (own, older chunked format via shape ref+0x30 and header+0x94); all strides
(header, model, shape, FVF, material set, SHDS, TXS3, VM) are identical in v8/v9/v14; render command
op 8 is encoded differently in GT6 (flag 0x92 carries an extra byte) and must be re-assembled; GT6
shader programs use semantic ids 0xAB/0xAC (GT5 table ends at 0xA8, no bounds check) and a different
shadow/light model -> GT5 donor shaders must be transplanted; GT6 texture pixels live in `body_s`.

**Converter architecture** (`gt6work/conv/`): "append and repoint" - `core.Mdl` keeps the source main
region as a mutable prefix, new structures are appended (offsets final at once), the VRAM region
(pixels, then FP microcode) is rebuilt and pointer fix-ups resolved in `finalize()`; untouched
structures stay byte-identical. Identity round trip of the GT5 Roadster verified. Modules (written in
parallel, each with a GT5-container self-test so failures are attributable): `geometry.py`
(PMSH/chunk decode -> plain shapes), `shaders.py` (GT5 donor transplant engine), `matmap.py`
(GT6 material -> donor mapping), `textures.py`, `models.py` (commands/header/VM plumbing),
`validate.py` (offline GT5-loader oracle).

### 2026-09-19 afternoon - GT6 port: main-region size budget (RPCS3, slot car/race/02360001)

Root `/` had run full (0 bytes): GT5's PDIPFS patch dir inside the RPCS3 install grows while playing. Moved the
regenerable `~/gt5re/pdipfs_out` (7.8 GB, checksummed) to `gt5re_offload/pdipfs_out` on the external btrfs
partition and left a symlink -> 7.6 GB free. The machine hard-rebooted at 13:49 (most likely an amdgpu gfx ring
hang, same as the logged VK_ERROR_DEVICE_LOST at 14:28); after a reboot the external partition must be mounted
again (`udisksctl mount -b /dev/nvme0n1p7`) or the symlink and gt6work are gone.

Padding series (zeros appended to the main region, VRAM pointers shifted):
Roadster +64k/256k/512k/768k (main up to 0x2e8980) race OK and car renders; Roadster partial marker (main 0x31fe00,
real data) and +1M (0x328980) crash in ksF3 at 0x8fe848; +2M: model never loaded (NULL at 0x2baf94).
Same +1M padding in VRAM instead: OK. Stock 00020024: unchanged OK, +1M zeros and +1M random both crash identically
(-> not compression). Stock 02290001 (main 0x357280, the largest) runs unchanged, so it is not a fixed P limit:
most likely a shared memory budget for main region + runtime allocations. Details: gt6work/notes/gt5_loader.md
("Main-region size budget"). Rule for the converter: keep the main region lean, no dead weight; <= 0x2e8980 is
proven for the Roadster slot.

### 2026-09-19 15:13 - first ADDITIONAL car registered: Tesla Roadster AWD '08 (RPCS3)

Overlay `gt6work/build/reg/roadster_awd_full-pdipfs` (built by `gt6work/specdb/build_reg.sh roadster_awd
cars/tesla_roadster_awd_08.json`: uncompressed spec DB tables + regenerated .idi/.sdb, PartsInfo entry, thumbnail,
arcade.adc with reg_patch_arcade_addcars.py; review_reader: 0 problems). Test `run_cartest.sh reg_awd`
(shots in `gt6work/shots/reg_awd/`): boots, the Arcade car list shows "TESLA ROADSTER AWD '08" as its own entry
(thumbnail, Tesla logo, spec panel Drivetrain 4WD), starting grid lists "User - Tesla Roadster AWD '08" next to
AI "Tesla Roadster '08", race loads, cockpit and chase views correct, no ·F errors.
=> the game accepts uncompressed .dbt tables (open question 1 of reg_registration_chain.md answered: yes).
Not yet checked: that the drive physics are really AWD (only the spec panel was seen), split screen, PS3 hardware.
Sebastian drove the AWD clone in RPCS3 (18:xx): "der tesla scheint 4wd zu sein, ich hab mehr kontrolle beim rutschen"
-> AWD physics confirmed by hand. Yellow colour (index 8) also verified by test awd_yellow. A hang when starting a second
race in a 3-hour-old leftover test instance (run_cartest.sh leaves rpcs3 running) did not reproduce on a fresh boot.

## 2026-09-19 19:30-20:30 - Split screen: cockpit/windscreen views, experiment

Sebastian asked for all camera views in split screen. Findings:
- RPCS3 runs the pre-patched EBOOT in dev_hdd0 (PPU hash `PPU-e7b9d5803786c4224421fb0b72a2460bd1fb9c7c`, 4P words baked in);
  the groups under `PPU-223cc85f...` in `~/.config/rpcs3/patches/patch.yml` do NOT apply to it. New experiment groups must
  go under the e7b9 hash. Verified by reading memory through RPCS3's GDB stub (127.0.0.1:2345, `m<addr>,4`);
  closing the socket kills the GDB thread with a fatal error and freezes the emulation -> read only at the end of a run.
- SELECT path: 0x467a14 walks the view list of the global view table (`*0x17fd3f8`); 0x46432c maps a view number to a
  list index (skips views with vt+0x70 true / vt+0x10 false); 0x464460 returns a skip mask (0x10 bad index, 0x20 no
  view, 1/2/4/8 from vt+0x14/+0x10/+0x18/+0x70).  Experiment group "GT5 split: allow all camera views (experiment)"
  (nops 0x4644e8/0x46450c/0x464538/0x464560 and 0x4643b0/0x4643d8, confirmed in memory): 2P split on High Speed Ring
  still cycles only bumper <-> chase. => INCAR/DRIVER are not filtered but NOT REGISTERED in split mode; the place where
  the table is filled per window is still unknown.  Group left in patch.yml, disabled.
- The interior model (`car/interior/02360001`, PDIPFS 9/61/MX) is loaded in every 1P race and never in split races:
  a cockpit view would also need the interior loading enabled (memory per player on the PS3, see the car main-region
  budget finding of the same day).
- Tooling: `nav.sh` misreads the split "Driving Options" dialog as `car` and waits; confirm with X + n by hand.

### 2026-09-20 - second AWD clone: Volkswagen 1200 AWD '66, and camera-view experiments

**Beetle AWD (Sebastian's request "4x4 vw käfer")**: `gt6work/specdb/cars/volkswagen_1200_awd_66.json`
(clone of `volkswagen_1200_66`, car id 1585, same model code; stock car is RR drivetype 4 -> drivetype 2 / type4WD 2,
fixed 30:70 front:rear because of the rear engine, open driven front diff, wheel inertias unchanged).
Combined overlay with the Roadster AWD: `specdb/build_reg.sh awd_cars cars/tesla_roadster_awd_08.json
cars/volkswagen_1200_awd_66.json` -> `build/reg/awd_cars_full-pdipfs` (review: 0 problems). RPCS3 test `awd_cars`:
car select shows "1200 AWD '66" (VW logo, Drivetrain 4WD), race on High Speed Ring runs, no ·F errors.
One overlay = one TOC, so both cars must be packed together (as done here).

**Split-screen camera views - three experiments, all negative** (patch group under the e7b9 hash, verified in memory):
1. skip-mask/lookup filters nopped (0x4644e8/0x46450c/0x464538/0x464560 + 0x4643b0/0x4643d8): still bumper <-> chase only.
2. sentinel 0x467a14 = `li r3,0; blr`: SELECT does nothing -> 0x467a14 IS the split SELECT path.
3. view count forced to 16 (0x3694f4 / 0x369534 = `li r3,0x10; blr`), alone and together with (1): still 2 views.
Runtime facts (RPCS3 GDB stub): the view table (global 0x17fd3f8) has its counters at (table+4)+0x20..0x23 =
`10101010` in 1P and `02020202` in split; the 16 view slots at camctx+0xd970 are filled unconditionally.
The counters are only ever *copied* from a source struct (0x4901ec, 0x4913e4), so the 2 comes from a per-mode
parameter block that is not located yet. Next lead: dump the 16 slot objects (vtable + the number returned by
vt+0x20) in 1P and in split and compare - if split slots carry other view numbers, the numbers (not the count)
are the gate. Script: `scratchpad/gdbslots.py`.
GDB stub notes: it PAUSES emulation while connected ('c' did not resume it), and closing the socket kills the GDB
thread and freezes the game -> use it only as the last action of a run.

### 2026-09-20 - split-screen TUNING prototype (works, not yet operable)

`gt6work/specdb/patch_arcade_split_tuning.py` (wired into build_reg.sh behind `MOD_SPLIT_TUNING=1`) opens
`SettingProject::SettingPopup.open(context, cp, nil, nil)` right after each split-battle player's Driving Options
dialog in arcade.ad (anchor: `result = SettingProject::DrivingOptionRoot.OpenDialog(context, data);`), after
`cp.ownArcadePartsAll()` for rental cars. The setting project is already loaded in arcade, so no project load is needed.
RPCS3 test `split_tuning` (overlay build/reg/awd_tuning_full-pdipfs): the FULL settings UI appears in the split flow
(Body/Chassis, Engine, Intake, Exhaust, Turbo, Transmission, Drivetrain, Suspension, Brakes, Tyres; 278 BHP, 1238 kg,
PP 464, "Player: 2") -> tuning in split screen is possible at script level.
Open problem: the popup takes no pad input (X/Circle/Start/Triangle on pads 1 and 2 all ignored), so the flow is stuck
and the race never starts. Most likely it is opened without a pad/window routing that the split flow needs
(DrivingOptionRoot gets `data.split_battle` + `data.window_id`; SettingPopup has no such parameter).
Next: hook it into CarSplitRoot (the per-player car select page, which already has pad routing per player) instead of
the arcade.ad options branch, or find the port/window binding SettingPopup needs.

### 2026-09-20 - survey: can all 158 GT6-only cars be converted? (no game change)

Extracted race/body + race/body_s of all 158 cars from GT.VOL (`GTToolsSharp unpack --indices`, 316 files, 405 MB,
`gt6work/gt6_survey/`) and ran `conv/geometry.decode_gt6` over them (`gt6work/scratch/survey_decode.py`,
results `gt6work/gt6_decode_survey.json`, write-up `gt6work/notes/gt6_convert_survey.md`).
* Data: every one of the 158 cars has race+hq body/body_s/wheel, interior and info; only the optional meter is
  missing for 35.
* Decode today: **59 of 158** (16 of them with tessellated shapes). Of the 99 failures, **80 fail only because the
  base render-command path allows opcodes {0,1,2,5,6,9,10,14} (conv/geometry.py:758) while those cars also use 8,
  11 and 12**; the other 19 are packed map2/tangent layout variants and one inconsistent separate-data header.
* Still unproven end to end: no GT6 car runs in GT5 yet (shader/material self-tests crash), and a new model code
  needs checklist B of the registration notes.

### 2026-09-20 - split tuning, second attempt (still no pad input)

`patch_arcade_split_tuning.py` now patches `CarSplitRoot::CarFinder.cb_selected_car` (right after the colour
selector, before setup_driving_option) instead of arcade.ad, and calls `ArcadeProject::ignorePadEvent(false)` before
`SettingProject::SettingPopup.open(context, cp, nil, nil)`. Test split_tuning2/3: the popup appears for the
selecting player at the right moment (car select -> colour -> tuning), but still takes no pad input (Down/X/Circle
on pads 1 and 2 do nothing, no focus highlight), so the flow stays stuck there. ModalPage.open() does block
(pushPage + enterEventLoop, scripts/gt5/SequenceUtil.ad:336), and SettingPopup.onInitialize does set a focus
(ROOT.setFocus(...Close)) and hides the other pages - neither is visible in game, so the page is probably never
initialised in this context.
Ideas for the next attempt: check whether the split contexts need the page pushed through the player's own
root_window (CarSplitRoot has per-window roots) instead of the SettingProject ROOT singleton; or extend
`SettingProject::DrivingOptionRoot` (which already works per player with split_battle/window_id) with tuning items
instead of reusing SettingPopup.
Deployed overlay left as `awd_cars` (both AWD cars, no tuning patch) so the game stays playable.

### 2026-09-20 - first END-TO-END conversion attempt of a GT6 car (Tesla Model S) - hangs at race load

`gt6to5.py gt6_survey/car/0236/0002/race/body build/models_race.mdl --lut synth` produces a complete GT5 v8 file
(3.9 MB, main region 0x301800) and `conv/validate.py` reports **PASS, 0 errors** (warnings: hdr+0x94 = 0,
op5 selectors 113/114/124 unknown to the GT5 host, 16 x op54, 2 x op61). `--lut gt5_roadster` is refused for this
car (9 GT6 colour slots vs 12 Roadster LUTs) -> `--lut synth` is the right policy for non-Roadster cars.
Test t_models / t_models2 (file put into car/race/02360001): menu and car select fine, the pre-race grid appears,
but pressing start never loads the race - file reads stop completely, no ·F, no SPU/RSX error, the game just hangs
(screenshots shots/t_models2/late*.png).
Second attempt with `--custom static0` (notes/header_model_cmds.md option A: replace op44+op54 custom-part pairs by
Jump -> branch 0): op5 selectors and op54 are gone (warnings down to 3), file 0x3d4800 / main 0x301580 -
**same hang** (shots/t_models_s0).
So the remaining suspects are not the custom-part VM path: op61 (2x), the missing packed-shape context (hdr+0x94 = 0),
the shader/material transplant, or the geometry itself. Next: bisect by converting with parts of the pipeline
disabled (geometry only on a donor container vs. textures only vs. shaders only).
Split tuning, third attempt: `SettingPopup.openPage(...)` instead of `.open(...)` - worse, the page transition
drops out of the arcade sequence back to the mode screen (shots/split_tuning4, split_tuning5). Patch reverted to
the ModalPage `open()` variant (renders correctly, no pad input). Deployed overlay is `awd_cars` again.

### 2026-09-20 - split tuning, attempts 4 and 5

4. Copy the SettingPopup page per player (`doCopy()` + `context_number`, the trick DrivingOptionRoot.OpenDialog
   uses): **black screen**. The copy's postInitialize hides every other page while the copy itself draws nothing -
   all of SettingPopup's internals reference the `ROOT` singleton, not `self`, so per-player copies cannot work
   without rewriting SettingPopup.ad.
5. New approach `specdb/patch_split_tuning_rows.py`: add three tuning sliders (cp.ballastWeight 0..200,
   cp.ballastPosition -50..50, cp.restrictorPermill 500..1000) to `SettingProject::DrivingOptionRoot`, which IS
   opened per player in split battles. Rows are built by copying the existing `Laps` slider row
   (`Pane_S.Laps.doCopy()` + `Pane_S.appendChild`), values written back in `apply()`. build_reg.sh now also
   compiles and packs `projects/gt5/setting/setting.adc` when MOD_SPLIT_TUNING=1 (the build works).
   In game: the split flow reaches the car select, then the screen goes **black** right after the car is confirmed
   -> the row copy or the appendChild call fails (no script error is visible; TTY.log stays empty).
   Next: verify the row/widget names of the Laps row (label child, slider child) against the layout, try
   `Pane_S.appendChild(row)` without context, or copy a simpler row; a widget-name dump from the running game
   would settle it.
Deployed overlay is `awd_cars` again (both AWD cars, no tuning), so the game stays playable.

### 2026-09-20 - converter: packed-shape context ruled out as the cause of the Model S hang

Test t_nopackctx: the STOCK Roadster with `conv.geometry.zero_gt5_packed_context` applied (hdr+0x94 = 0 and the four
u16 at B0+0x28 = 0) **crashes** at race load (·F ksF3 0x00b99284, read of 0x20). That is not a contradiction of
notes/vm.md - that file still contains chunked shapes, and a chunked shape with a NULL context takes the packed path
and dereferences it. It does confirm the precondition the note states: zeroing is only allowed when EVERY shape is
plain, which is exactly the case in converted GT6 files (PMSH is decoded to plain shapes).
=> hdr+0x94 = 0 is not the reason the converted Model S hangs; the remaining suspects are the shader transplant
(the t_selftr / t_matmap self-tests fail with SPU compile errors), the material mapping and the geometry itself.

### 2026-09-20 - split-screen tuning WORKS (preset picker in the arcade project)

Decisive negative first: shipping a **recompiled** `projects/gt5/setting/setting.adc` breaks the Driving Options
dialog (black screen) even when the source is completely unchanged - control build with MOD_TUNE_LEVEL=0
(shots/tune_l0), same with one copied row (tune_l1). The compile itself looks fine (350553 B vs stock 350434 B),
but only `arcade.adc` / `race.adc` are known to rebuild faithfully. => no modifications inside the setting project.

Working solution: `specdb/patch_arcade_split_tuning.py` (rewritten) patches **arcade/CarSplitRoot.ad** only. It adds
`openTuning` / `makeInitialDataForTuning` / `cb_init_tune` / `cb_focused_tune` / `applyTuning` to the module
`CarColorSelector` - i.e. it reuses the colour selector's finder, the one dialog that provably takes the pad of a
single split-screen player - and calls it in `cb_selected_car` right after the colour selector:
8 presets (Standard, Ballast 50/100/200 kg, Power 90/80/70, Ballast 100 + Power 80) writing `cp.ballastWeight`,
`cp.ballastPosition`, `cp.restrictorPermill` between `cp.beginSetting()` / `cp.endSetting()`, after
`cp.ownArcadePartsAll()` for rental cars and before `setArcadeCar(cp, player_num)`.
In game (shots/tune_step, tune_race): after the colour chips the player gets a second row of 8 chips (the presets,
balloon tip = preset name), X confirms, the flow continues into the Driving Options and the 2P race runs normally.
`scratchpad/split2_hsr.sh` updated for the extra step.
Open: the preset name in the balloon tip and the actual effect are not verified yet (the split default car is a
kart, whose spec panel shows "---"); redo with a Tesla/Beetle. Next UX step would be own chip colours/labels and
more values (gears, LSD, brake balance) - all the same pattern.

### 2026-09-20 - converter: the blocker is the shader transplant (SPU side)

Re-ran both self-tests on the STOCK Roadster container (so geometry/textures are known good):
* `t_selftr2` (build/g5r_selftransplant.mdl, material set pointing at a transplanted copy of all shader programs):
  **crash** - `·F SPU[0x3000100] PDICellSpursKernel3 [0x07654] SPU: Compilation failed.`
* `t_matmap4` (build/g5r_matmap_selftest.mdl): **crash** - `·A SPU[0x0000100] PDICellSpursKernel0 [0x08eb8]
  VM: Access violation reading location 0x0`.
Both die inside the SPURS kernels, i.e. the game hands the SPU a structure our transplant leaves NULL or mis-relocated;
the PPU-side structure rules that conv/validate.py checks are all satisfied (SHDS FP table: 109 entries, every ucode
offset inside the VRAM region and 128-byte aligned, txs/shds P fields correct - verified against the stock file).
=> the GT6 Model S hang at race load has the same root cause; geometry and textures are not the blocker.
Next: find what the SPU reads per material/shader (SPURS job data) and which pointer of the transplanted material set
is still stale - compare stock vs transplanted material-set records field by field, not just the SHDS table.

### 2026-09-20 - split tuning verified in game (Tesla Roadster AWD, High Speed Ring)

shots/tune_proof: after the colour chips player 1 gets the second row of 8 chips, the balloon tip reads the preset
name (screenshot shows **"Power 70"** on chip 7) -> the picker is operated by that player's pad and is labelled.
Side effect of `cp.ownArcadePartsAll()`: the following Driving Options dialog now also offers **Front/Rear Tyres**
(the arcade parts are owned), i.e. tyre choice per player in split screen comes for free.
The Specifications panel keeps showing the spec-DB power (248BHP) - it does not reflect cp settings, so it cannot
serve as proof of the restrictor; a top-speed comparison in-race was attempted but the unattended cars hit the
barriers, so the measured numbers (91 vs 88 mph) are not conclusive. The values themselves are written with the
game's own API (`beginSetting` / `ballastWeight` / `ballastPosition` / `restrictorPermill` / `endSetting`) before
`setArcadeCar`, exactly as TuningPopup does it.
Deployed overlay: `awd_tuning` (both AWD cars + the picker) - the 1P flow is untouched, only CarSplitRoot is patched.
Converter, static comparison of the self-transplant against the stock file (no new lead): the material-map records,
the table at hdr+0xf0 and the B0 per-model records are all relocated correctly in the transplanted file; the 126
words that still point into the old material-map range sit inside the DEAD copy of the hdr+0xf0 table that
append-and-repoint leaves behind, not in any live structure. The stale-pointer hypothesis is therefore refuted;
the SPU crash must come from data the SPURS jobs read (shader program / command-list structures), which the PPU-side
comparison cannot see. Next: find the SPU job descriptor for material/shader work and dump it in the emulator.

### 2026-09-20 23:06 - installed on the PS3 (console 192.168.1.6, announced and requested by Sebastian)

Console found at **192.168.1.6** (the journal's 192.168.0.2 / .1.11 are stale; MAC 00:1f:a7:.. = Sony),
webMAN 1.47.47g MOD, firmware 4.93 CEX Cobra 8.5, no game running, `EBOOT.BIN` = the patched 4P one (9477184 B)
with `EBOOT.BIN.orig` (9505120 B) still next to it -> the EBOOT was NOT touched by this upload.
Uploaded `gt6work/mods/awd_tuning-pdipfs` (57 files) to `/dev_hdd0/game/BCES00569/USRDIR/PDIPFS/`, every file
size-verified after upload (57 ok, 0 mismatch). Contents: arcade.adc (all cars/tracks unlocked + the two AWD cars
+ the split-screen tuning preset picker), race.adc (3P/4P windows, quadrant HUD/meter, split countdown),
spec DB + PartsInfo + carlist + thumbnails for Tesla Roadster AWD '08 and Volkswagen 1200 AWD '66.
Backup + rollback: `gt6work/build/ps3_backup_0920_2306/` holds the 5 files the console had before (K/4D = TOC,
9/DF/9T arcade.adc, 9/S3/3J race.adc, 9/PQ/O3, 9/7T/X6) and `rollback.sh` (`PS3=192.168.1.6 ./rollback.sh`)
which restores them and deletes the 52 added files.
NOT included (does not work): all camera views in split screen.

### 2026-09-20 - split-screen camera views: attempts 6-8 (still only bumper <-> chase)

All three ran on the e7b9 hash group, this time with the patched words **verified in the running game** through the
GDB stub (3694f4 = li r3,0x10, 369534 = li r3,0x10, 4644e8 = li r30,0, 4643b0 = nop):
6. count/bound forced to 16 + all skip-mask filters nopped: unchanged, 2 views.
7. same, verified in memory: unchanged -> the count and the permission mask are NOT the gate.
8. number->index lookup 0x46432c replaced by an identity mapping (`mr r3,r5; extsw r3,r3; blr`), so a candidate
   number is used directly as a slot index: unchanged, 2 views.
So the switch never even reaches the other slots: the candidate number in 0x467a14 only ever takes two values
(r23 = the current view's own number via view->vt[0x20], r31 = r23 +/- step). The next thing to look at is where
that step/current number comes from (0x46473c and the ctx fields at +0x174/+0x17c the 09-06 journal found), not the
list mechanics.
Independently: the interior model (car/interior/<code>) is never loaded in a split race (PDIPFS 9/61/MX opened in
every 1P race, never in split), so even a selectable cockpit view would have nothing to draw. Both halves have to
be solved for the feature.
Patch group left in patch.yml, disabled.

### 2026-09-21 - MILESTONE: GT6 geometry renders in GT5 (shader transplant bypassed)

`gt6work/scratch/geom_only_port.py`: put GT6 meshes into the UNCHANGED GT5 donor container - donor material set,
SHDS and TXS3 stay byte-identical, only shapes are replaced, each keeping the donor shape's material index.
* Variant A (keep the donor shape's FVF definition, 40 shapes, main 0x2aec80): **race runs, the GT6 body is
  visible** in cockpit and chase view (shots/t_geom40, doc screenshot: a metallic, scrambled car-shaped mass).
  Scrambled because GT6 attributes are written into the donor layout without conversion - but it draws.
* Variant B (`OWN_FVF=1`: a layout built from the mesh + emit_fvf, main 0x2c0900): **all race views black**
  (shots/t_geom40b) - a new FVF the donor's vertex program does not understand kills the frame.
=> The geometry pipeline (PMSH decode -> plain GT5 shapes) is sound; the blocker really is the material/shader side.
Direction for the converter: convert GT6 mesh attributes INTO the donor's existing layout (reorder/retype per
element) instead of synthesizing a new FVF, and keep donor materials until the transplant is fixed.
Note: replacing all 217 shapes gives main 0x464c00 (4.6 MB) - far over the memory budget; the old geometry stays in
the file as dead weight (append-and-repoint), so a real port must drop the donor geometry it replaces.

### 2026-09-21 - bonnet/interior view: attempt 9 (forcing the applied view index) - still two views

New group "GT5 split: force view index 1 on SELECT": `0x467c94` (`extsw r4,r3`, the index 0x46432c resolved) ->
`li r4,1`, verified in memory (38800001). Every SELECT should now apply slot 1 and the view should become constant.
In game (shots/cam_force1) SELECT still toggles bumper <-> chase.
Together with attempt 2 (sentinel: patching 0x467a14 to return immediately DOES kill SELECT) this means the split
toggle runs through 0x467a14 but not through its 0x467c90/0x467c94 apply tail - i.e. the two reachable views are
switched by an earlier branch inside 0x467a14 (the 0x4677e4 / 0x467488 path at 0x4674xx, or the pad module's own
camera toggle at 0x48A05C from the 09-06 journal). That is where the next attempt has to look; the list mechanics
(count, permission mask, number->index lookup) are now all ruled out by measurement.

### 2026-09-21 - bonnet/interior view: attempts 10 and 11 - the split toggle does not use 0x467488 at all

10. `0x467c94 -> li r4,2` (force the applied index at the walk's apply tail): unchanged, bumper <-> chase.
11. additionally `0x4677e0 -> li r4,1` (the OTHER caller of 0x467488, in the message dispatcher; both verified in
    memory): unchanged.
So neither call site of the view-apply function drives the split-screen toggle, although patching 0x467a14 to
return immediately DOES disable SELECT (attempt 2). Conclusion: 0x467a14 consumes the SELECT event and switches the
camera through a path that bypasses 0x467488 - most likely writing the camera context's view index/mount fields
directly (09-06 journal: ctx+0x174/+0x17c with copies at +0xDB84/+0xDB8C, +0xE1E4/+0xE1EC). The bulk writes at
0x493c58/0x499270 are struct copies, not the toggle, and 0x48a05c is the per-player input state builder (0x290
stride), not the camera switch. Next attempt should trace inside 0x467a14 between 0x467a58 (0x46473c) and the apply
tail, or set a data watch on the context fields.

### 2026-09-21 - bonnet view: important CORRECTION - 0x467a14 is dead code

A full-segment branch scan (whole first PT_LOAD, not just .text up to 0xf9e6e0) finds **no caller at all** for
0x467a14, and its address appears nowhere as data (no OPD/vtable entry). The same scan confirms 0x467488 has
exactly the two callers 0x4677e4 / 0x467c9c - both of which were patched to force a constant view without any
effect. So:
* the "sentinel" result of attempt 2 (patching 0x467a14 kills SELECT) was a **misreading** - that run simply never
  showed a chase frame. Every conclusion built on "0x467a14 is the split SELECT path" is void.
* the visible split toggle does not go through 0x467488 either (no other caller exists, forcing it changes nothing),
  and it does not write the current-view field (only writers: 0x465bfc reset, 0x4674d8 inside apply, 0x468890 init).
New, better lead: the per-frame camera update around **0x475b30** (reads the global view table at 0x17fd3f8, calls
the permission check 0x464460 at 0x475cbc, stores 0/1/2 into ctx+0xd38 and sets the camera through 0x464db0 /
0x466cdc). Inside apply, 0x4675a0 picks between two camera configs of the SAME view object (r27+0x10 vs r27+0x20) -
so the two reachable "views" in split may well be two configs of one view, not two different views.
Next attempt should trace 0x475b30: what feeds the view index r22 it asks 0x464460 about, and where the split flow
limits it.

### 2026-09-21 - bonnet view, attempt 12 (live view query) - still two views; stopping this approach

Traced from the permission check 0x464460 to its callers: 0x467bf4 and 0x475cbc sit in **dead** functions
(0x467a14 / 0x475b44 - neither is branched to anywhere in the whole segment nor referenced as data; the search
method was validated against a known vtable function), 0x481d48 is dead as well. The only LIVE caller is
**0x478310**, a virtual method in vtable 0x16ea680 at +0x68 ("is this view selectable?", stores the answer as a
byte at this+0x1c). Patch "view query always allows" (0x4783a4 `bne` -> nop, verified in memory): the split race
still only alternates bumper <-> chase.
Status: twelve measured attempts. Ruled out by experiment: list length/bound, permission mask, number->index
lookup, both apply call sites, the live view query. The camera change in split therefore happens in code that does
not consult any of these - it cannot be found by static reading alone any more.
What it would take next: instruction-level tracing (RPCS3's GUI debugger with a breakpoint on the camera context
write, or a logging patch into a code cave that records the requested view numbers into a scratch area which the
GDB stub reads at the end of a run). That is a different working mode than the black-box patch/run loop used so far.
All camera patch groups are in patch.yml and disabled.

### 2026-09-21 - clean body port works: conv/port_body.py

`gt6work/conv/port_body.py <gt6 body> <out.mdl> [--budget]`: keeps the donor's material set, SHDS and TXS3
byte-identical and only swaps geometry. Donor GTBE_BODY shapes and GT6 GTBE_BODY shapes are paired by vertex count
(the names of two different cars never match - only 2 of 217/225 names are identical), the biggest GT6 body shapes
replace the biggest donor ones until the main-region budget is reached, and **every donor body shape that is not
replaced is emitted as a degenerate shape** - without that the donor's own body is drawn through the new one, which
is exactly the "both Teslas rendered into each other" Sebastian saw.
Model S -> Roadster container: 13 of 124 GT6 body shapes replaced, 164 donor shapes hidden, main 0x2eb200,
file 3.5 MB. In game (t_clean2): the race runs and the car is a coherent, clearly different body (sedan rear
instead of the roadster's), rendered in the donor's dark material. Side-by-side with the stock car:
shots/t_clean2/race_chase.png vs shots/t_pad512k/race_chase.png.
Open for a full port: paint/materials (the shader transplant still crashes in the SPU), only 13 of 124 body shapes
fit because append-and-repoint keeps the replaced donor geometry as dead weight - a real port has to compact the
main region.
Pitfall for future tests: `run_cartest.sh <name>` only deploys `mods/<name>-pdipfs`; the file has to be built with
`build_cartest.sh` / `batch_cartest.sh` first, otherwise the previous overlay is tested (cost one run today).

### 2026-09-21 - bonnet view: the live camera code is finally located (attempts 13-15)

Black-box bisect of the 8 call sites of the camera-set helper 0x464db0 (nop the bl, then run a 2P race):
* group A (0x466d84 + 0x466f94 + 0x4671b8) off: the race still toggles between two views, but one of them is
  **visibly broken** - the camera sits under the car looking at the underbody (shots/cam_groupA). So these calls
  are the ones that actually position the split-screen cameras; the live camera code is
  **0x466d08, 0x466df0 and 0x467008** (the three functions containing those sites).
* only 0x466d84 off: everything normal again (shots/cam_site1) -> the effect comes from 0x466f94 or 0x4671b8.
Inside 0x466df0 the current view's type is queried (`0x4645ac` = currentView->vt[8](), the view object comes from
sub+0xD9B0 via 0x46459c) and compared against 9; not the gate we are after, but the type value is now readable.
This is the first live code that provably drives the split cameras - every earlier lead (0x467a14, 0x475b44,
0x481d48) was dead code. Next: continue the bisect (0x466f94 vs 0x4671b8), then read the switch inside 0x467008 /
0x466df0 that picks the camera config, and find what restricts it to two.
All experiment groups are in patch.yml and disabled.

### 2026-09-21 - new cars instead of replacing the donor + AWD family + bonnet view attempts 16/17

**Ported cars are their own cars now.** `specdb/build_reg.sh` learned `MOD_EXTRA_DIR=<dir>`: every file below that
directory is copied into the pack tree, so converted models can ship under a NEW model code.
`build/extra_02360002/` holds car/race/02360002 (the port_body output), car/hq, car/interior, car/info,
wheel/race, wheel/hq (interior/info/wheels copied from the Roadster, hq = the ported race model for now - the real
hq model could not be extracted: `GTToolsSharp unpack --indices` extracts 0 files from the installed PDIPFS).
Overlay `full` = 9 cars: Tesla Roadster AWD, VW 1200 AWD, 6 Golf AWD variants and **Tesla Model S Signature
Performance '12 as its own car (id 1896, model code 02360002)** - the Roadster is no longer replaced.
Build: spec DB checks 0 problems, 88 files, 11 MB; the game boots, the car list shows the new cars and a race runs.
Still to verify: selecting the Model S itself in game.

**AWD family**: `specdb/gen_awd.py <label>...` generates an AWD clone description for any car (skips cars that are
already 4WD), with free ids taken from the stock tables and the other descriptions. Generated: 6 Golf variants
(golf_gti_05, _std, golf_gti_5dr_01, _rm, _std, golf_gti_76); golf_r32_3d_03, golf_r_10 and hpa_golf_r32_04 are
factory 4WD and were skipped. Only one Tesla exists in GT5 (the Roadster, already done). Naming bug fixed: using
both the long and the short name as replacement pairs produced "Golf V GTI '05 AWD AWD"; one pair is enough and
"AWD" now goes in front of the year ("Golf V GTI AWD '05"). The Beetle's ids were moved (3520/3521, 8920/8921,
11903) because the Model S description already used 3503/8903/11902.

**Bonnet view attempts 16/17**: the camera-set bisect narrowed to **0x466f94** (nop it -> one of the two split
views looks at the underbody, shots/cam_site2). The function 0x467008 contains a 4-way switch on
`r11 = *(r30+0x34)` (cases 0..3 = four camera kinds, which matches the journal's "split only has index 3 and 0");
forcing r11 = 1 (0x467088 `lwz` -> `li r11,1`, group in patch.yml) changes nothing visible, so that switch is not
the selector either. Seventeen measured attempts; all experiment groups are disabled.

### 2026-09-21 - bonnet view attempt 18 + shader transplant integrity checks

**Bonnet view, attempt 18**: dumped the camera context in 1P and in split through the GDB stub
(scratchpad/gdbcam.py, cam_1p.txt / cam_split.txt). The five counters at (table+4)+0x20..0x24 are `10 10 10 10 10`
in 1P and `02 02 02 02 02` in split. Patched the VALUE at its source (the two struct copies 0x4901ec / 0x4913e4,
`lbz src+0x27..0x2b` -> `li r0,16`, group in patch.yml): the split race still only alternates bumper <-> chase.
So even with all five counters at 16 the two extra views do not appear - the counters are not the gate either.
18 measured attempts; nothing further without SPU/PPU instruction tracing.

**Shader transplant**: three targeted integrity checks of build/g5r_selftransplant.mdl against the stock file, all
**pass**:
* all 109 FP microcode blocks are byte-identical after the move,
* every MaterialData colour-key pointer points into the NEW key pool (the pool move is complete, not only the
  Material.keys pointers the code comments mention),
* no pointer of Material (0x34), MaterialData (0x28) or the s14 array became NULL.
So the PPU-side structures are consistent; the crash (`SPU: Compilation failed` / SPU read of 0x0 in the SPURS
kernels) comes from data the SPU itself consumes. Finding it needs SPU-side debugging (RPCS3's SPU debugger or a
logging patch), not more static comparison.
Practical consequence: the usable path to GT6 cars today is conv/port_body.py (donor materials, correct geometry),
not the transplant.

### 2026-09-21 - bonnet view: the logging patch WORKS and finally produces data

Built `gt6work/notes/scripts/make_camlog_patch.py` (trampolines in the RX cave at 0x1581200+, log buffer at
0x1949000 in the mapped page behind the RW segment - the area the 4P mod already uses). Lessons:
* a store with RA=0 is an ABSOLUTE address on PPC, so the buffer pointer must live in r11 and the counter must be
  incremented in r12, never in r0 (two generator bugs, both found by disassembling the generated words);
* the buffer address is writable (GDB canary 0xdeadbeef), the cave is executable (minimal canary stored 0x1234
  from the per-frame model-draw call) - so caves added by RPCS3 patches do run;
* simple 5-word "marker" trampolines (one store + tail branch) are the robust pattern.

**Marker run (1P vs split, identical results)**: camera-set sites 0x466d84 and 0x466f94 fire, 0x4671b8 never fires,
the apply calls inside 0x467488 never fire, but **the dispatcher call 0x4677e4 -> 0x467488 fires in both modes**;
the model-draw canary confirms the patch was active.
**Value ring on 0x4677e4** (16-entry ring at 0x1949100): in a split race with four SELECT presses the view numbers
passed to 0x467488 are **0, 0, 0, 1, 1** - i.e. split really only ever asks for view 0 and view 1 (the old journal's
"index 3 and 0" was wrong). That also explains attempt 11: forcing r4 = 1 there forced one of the two values that
are used anyway, which is why nothing changed.
**Forcing r4 = 2 and r4 = 3**: the camera jumps somewhere completely different (sky/mirror-ground, the car is not
in frame) - so the view number does control the camera, but views 2/3 are never POSITIONED in split: the per-frame
camera-set code only runs for the two active views.
Next: log inside 0x466df0's guard chain (0x466eb4 / 0x466ec0 view type == 9 / 0x466ed8 / 0x466ee4 / 0x466ef8) to see
which guard skips views 2/3 in split, then lift that guard.
Ring in a 1P race for comparison: only **two** calls, both with view number **7** - so the numbers are ids in a
larger space (not 0..3), and in 1P most SELECT presses do not go through the dispatcher path at all, while in split
every press does (5 calls with 0/1). The split limitation therefore sits in whoever builds that request (the event
object whose +0x20 holds the number, read at 0x4677d8), not in the apply function.
Next concrete step: log the CALLER of the dispatcher (LR at 0x4677e4 is inside the dispatcher, so hook one level up)
or log the event object's fields, to find who computes 0/1 in split and 7 in 1P.

### 2026-09-22 - decoder: three opcodes added (59 -> 121 of 158), bonnet view attempts 19/20

**Decoder**: `conv/geometry.py:758` now allows the render opcodes **8, 11 and 12** in the base path
(backup geometry.py.bak-opcodes). They carry no geometry - the bit parser already consumes them exactly (op8 has no
payload, op11 22 bits, op12 29 bits) and the triangle loop only reacts to 1/2/5/14, exactly as for the
long-allowed 6/9/10; the `loaded == n_raw` assertion stays as the guard. Result of the survey rerun:
**121 of 158 cars decode** (was 59), 14.9 M triangles in total; the remaining 37 fail on packed map2/tangent layout
variants. Regression check: the Model S decodes to exactly the same 225 shapes / 122314 triangles as before.
In game: `monster_sx4_pikespeak_11` (02470001, could NOT be decoded before) ported with conv/port_body.py onto the
small donor 00570018 (main 0x172b80) renders correctly in a race (shots/t_sx4).

**Bonnet view**: attempt 19 = ask for view 2 AND nop all five positioning guards of 0x466df0 (0x466eb4, 0x466ec4,
0x466ed8, 0x466ee4, 0x466ef8) - unchanged broken camera. Attempt 20 = ask for view **7**, the number a 1P race
requests from the same dispatcher - same broken camera. So views 2/3/7 all behave alike in split: the number is not
backed by a view object there, and the code falls back to an uninitialised camera. The view NUMBER is a property of
the view objects (vt+0x20); in split the objects carry 0/1, in 1P 7. Next: find where those numbers are assigned,
i.e. where the camera set is configured per race mode.
Note: scratchpad scripts are lost on reboot - split2_hsr.sh now lives in gt6work/.

### 2026-09-22 - bonnet view: camera slots understood, but forcing them breaks the game -> stopping the feature

Runtime dump of the split-screen camera context (logged with a cave trampoline at the call of 0x4664fc, the
function that picks the CURRENT view out of the 16-slot array; context = 0x4232e000, slots at ctx+0xd970, current
view at ctx+0xd9b0): all 16 slots hold DIFFERENT camera classes, e.g. slot 0 = CameraOnboard (vtable 0x16eadd0),
slot 1 = a trackside camera, slot 11 = the one split actually uses. 0x4664fc chooses between the hard-wired
indices 3 and 13 (0x466580 `li r4,3`, 0x466590 `li r4,0xd`).
Forcing that index does change the camera in split - slot 0 gives a low forward onboard view, slot 1 a trackside
view, slot 5 a wider one - **but the result is not usable**: Sebastian reports "das schaut nicht gut aus und fahren
ist dann auch nimmer möglich"; forcing the index replaces the camera for every view of that player and the car can
no longer be driven properly. The bonnet/cockpit images are SUB-views (mounts) of the onboard camera, not slots, so
this lever is the wrong one anyway.
=> ~24 measured attempts. Stopping the bonnet-view work here: every further probe changes global camera state and
costs the user a broken game session. If it is ever picked up again, the entry point is the onboard camera's mount
selection (ctx+0x174/+0x17c per the 09-06 journal, written by the parameter-block copies at 0x493c58/0x499270),
and the tooling for it (cave trampolines + GDB dumps, gt6work/notes/scripts/make_camlog_patch.py) now works.
All experiment groups in patch.yml are disabled; the deployed overlay is `awd_tuning` again.

### 2026-09-22 - SPLIT-SCREEN VIEW SWITCH SOLVED (roof/over-the-bonnet camera works)

Found by runtime diffing (cave logger + GDB dumps), not by reading:
* The active window's camera context is the **CameraOnboard object itself** (window 0 = 0x422BE000, vtable
  0x16eadd0); the four window contexts are 0x422BE000/0x4230E000/0x4231E000/0x4232E000 and only the active one
  has `current-view == itself` (idx 0).
* Its **sub-view index lives at ctx+0x3a20**. Measured in 1P: 0 = bumper, **1 = cockpit** (full interior with wheel
  and dashboard), **3 = roof/over-the-bonnet**, 2 = chase. In split only 0 and 2 occur.
* The index is computed at 0x4890f8 by the lookup 0x4814d0 from the **requested view id at ctx+0x36c** against the
  16-entry table at 0x13BA3FC: id 0 -> idx 0, id 0x1a -> idx 1, id 6 -> idx 3, id 1 -> idx 2.
* Forcing the INDEX alone does nothing visually; forcing the **ID** works. The id is written by the onboard
  camera's setter 0x4852c8 (`stw r30, 0x36c(r31)` at 0x485340).

**Working patch** (group "GT5: split onboard view 0 -> 6 (roof/over-the-bonnet)"): the store at 0x485340 is
redirected to a cave at 0x1581900 that turns id 0 into id 6:
`cmpwi cr7,r30,0 / bne skip / li r30,6 / skip: stw r30,0x36c(r31) / b 0x485344`.
In game (shots/cam_swap): player 1 in a 2P split race now toggles between the **roof/over-the-bonnet camera** and
chase instead of bumper and chase; the car drives normally.
Limitation: the true cockpit view (id 0x1a) shows the underbody in split (shots/cam_swap1a) because `car/interior`
is never loaded in a split race - that is the remaining piece for a real interior view. In the half-height split
viewport the bonnet itself is below the visible area, so the roof camera reads as a high forward view.

### 2026-09-22 - packaging question: can split-screen mod and cars coexist on the PS3?

Verified with GTToolsSharp (build/chain_test): packing a second overlay with `-i <already modified PDIPFS>`
produces a TOC that lists **both** sets - `car/race/02360002` and `specdb/.../GENERIC_CAR.dbt` from the first pack
and `car/thumbnail_M/chaintest_00` from the second, 48385 entries in the listing. The output folder only contains
the TOC (K/4D) plus the new files, so installing it on top keeps the earlier files.
=> Two mods CAN coexist, but not as two independent packages in arbitrary order: PDIPFS has a single TOC, so the
second package must be BUILT against the state the first one produces (chained), or both must be packed together
(what build_reg.sh does today). The patched EBOOT.BIN is a separate file and independent of PDIPFS.

### 2026-09-22 - BONNET VIEW IN SPLIT SCREEN WORKS (id 7)

Walked the candidate camera ids in ONE run with a cave that hands out the next id from a table on every call of the
onboard view setter (0x485340), then pinned the winner: **view id 7 = the bonnet camera**, which shows the front of
the car inside the half-height split viewport (id 6, the roof camera, is cropped away; id 0x1a, the cockpit, shows
the underbody because car/interior is not loaded in split).
Final patch "GT5 split screen: bonnet view instead of the bumper view": the store at 0x485340 is redirected to a
cave at 0x1581900:
`cmpwi cr7,r30,0 / bne skip / li r30,7 / skip: stw r30,0x36c(r31) / b 0x485344`
In game (shots/bonnet_final): both players race with the bonnet in frame, SELECT still toggles to the chase view
per player, and the quadrant meter (speed/gear) stays visible - Sebastian's question about the tachometer answered:
the meter is HUD, independent of the camera.
Two ppcasm pitfalls hit again while writing the caves: `addi rX,r0,..` means literal 0 (use r11/r12 for counters),
and the branch-back target must be computed from the LAST instruction's address.

### 2026-09-22 - one combined release package built (not installed yet)

`gt6work/release/gt5_split_cars_v1/` (44 MB): EBOOT.BIN (294 words = the 288 split-screen words of release/4p plus
the 6 bonnet-camera words; built with tools/build_eboot.sh, round trip OK, NPDRM hashes verified),
EBOOT_patched.elf, words.txt, SHA1SUMS, README.md and mod/pdipfs = the `full` overlay (scripts + spec DB +
9 cars incl. the GT6 Model S).
Pitfall: `release/4p/words.txt` has five columns (address, orig, new, two disassembly columns) while
build_eboot.sh only accepts three - feeding it directly silently applies NOTHING but the other file's words
("6 words applied"). Converted with `awk '{print $1,$2,$3}'` -> 294 words applied.
Tested in RPCS3 by installing the new EBOOT into dev_hdd0 (backup: gt6work/build/EBOOT.BIN.rpcs3-backup, the
pre-patched 4P one) with ALL patch.yml groups disabled: split race runs, both players have the bonnet view, meter
visible, PPU hash is now PPU-ab75a53d2348725ceb3f1a9bfb251e7f6a6d055a.
Not installed on the PS3 yet - that replaces the console's EBOOT and needs Sebastian's go.
