# Gran Turismo 5 (BCES00569, update 2.17) — 4-player split battle

RAM patch + Adhoc script mod that turns the 2-player "2P Split Screen" arcade mode into a
4-player race (four viewports in quadrants, four human-controlled cars on controller ports 0-3).

Status (2026-09-05): **verified in RPCS3** (0.0.42-19916, LLVM PPU, ASMJIT SPU) — four views in a
quadrant layout, four cars, all four pads steer their car, ~47 FPS, no crash through the race.
**PS3 hardware test still pending** (see "Testing on the PS3").

## What is in here

| file | purpose |
|------|---------|
| `rpcs3-patch.yml` | RPCS3 patch groups (`~/.config/rpcs3/patches/patch.yml`), key `PPU-223cc85f…` |
| `deploy_4p.sh` | PS3 script (webMAN PS3MAPI pokes): `PS3=<ip> ./deploy_4p.sh apply\|off\|verify` |
| `words.txt` | every patched word: address, original, new, capstone disassembly of both |
| `mod/openadhoc-split.diff` | Adhoc script changes against the OpenAdhoc GT5 sources (arcade + race projects) |
| `mod/arcade.adc`, `mod/race.adc` | compiled scripts |
| `mod/pdipfs/` | packed PDIPFS overlay (header/TOC + the two scripts) for `USRDIR/PDIPFS/` |

Addresses are PPU virtual addresses of the decrypted 2.17 EBOOT (load base 0x10000,
sha1 `306f86c62b9f03041c903be96ac59e5c3f130452`).

## What the patch does

The engine already carries three players through the whole loading chain (that part is the
script mod: `createSplitBattle` builds 2..4 entries, each with its own `MCarDriverParameter`
and controller port, and sets `window_max` to the number of human players, clamped to 4 — the same script build serves the 3P and 4P releases). Two engine structures were hard-wired to two:

1. **MOrganizer player entries.** The organizer object (0x35030 bytes, allocated at 0x177110)
   holds an inline array of two 0x290-byte player-entry objects at +0x2b8. Creating the third
   player's context (`0x170b74`: `entry = MOrg + 0x2b8 + index*0x290`) read organizer fields as
   an entry and dereferenced a bogus pointer (`0x48e1c0/0x48deb4`) — silent memory corruption on
   the PS3 (the "third car never finishes loading" hang), an access violation in RPCS3.
   The patch allocates four entries externally in the constructor (cave 0x1580f00), keeps the
   base/end pointers at +0x2b8/+0x2bc in the now-dead inline area and rewrites every
   `addi rX, rMOrg, 0x2b8` to `lwz rX, 0x2b8(rMOrg)` (constructor, four iterators, the factory,
   both destructors); loop bounds 2 → 4.
2. **WindowManager window slots.** The window manager (inline at MOrganizer+0xa90) has two
   inline `{window*, node*}` slots at +0x1c/+0x24 with `window_max` at +0x2c. Script code calls
   `ORG.setCameraTarget(2, …)`, which read `window_max` as the third window pointer. The patch
   mirrors the slots into an external 4-slot array (pointer at MOrganizer+0x2c0 = WM-0x7d0),
   constructs windows 2 and 3 in the constructor (cave 0x1581000), and redirects all index
   accessors / window loops in the window-manager code to the external array; `setWindowMax`
   is rewritten as a loop over four windows. Direct reads of windows 0/1 are unchanged.
3. **Viewport count.** `0x379c30` / `0x37b250`: the "+2 human players" constant becomes +4.
   (The 3P release uses +3; everything else is identical.)

Not needed any more: the earlier load fix ("cave4") — the slot-2 reset it worked around was a
consequence of (1).

Known cosmetic issues: the HUD (speedometer/gear) still uses the 2-window layout and sits over
the bottom two views; timer and standings are drawn over the top-right view.

## How it was tested

RPCS3 with firmware 4.93, disc dump + 2.17 update folder, keyboard pad handler for pads 0-3.
Menu path automated by `tools/nav.sh` (image-based state machine): Arcade → 2P Split Screen →
High Speed Ring → cars → options → mod dialog "Spieler 3 … ?" = yes, "Spieler 4 … ?" = yes.
Evidence: `doc/emu_4p_race_2026-09-05.png`.
The RPCS3 crash logs (`Access violation`) plus host-gdb guest backtraces (`tools/ppubt.py`) were
what located both structures; see `JOURNAL.md` for the full trail.

## Testing on the PS3

Code pokes only take effect when set **cold** in the main menu (instruction cache), so:

1. Install the script mod once: upload `mod/pdipfs/*` into `/dev_hdd0/game/BCES00569/USRDIR/PDIPFS/`
   (same paths), e.g. with `deploy_mod.sh`-style FTP uploads. The console already carries an
   equivalent build (`mod_mem`).
2. Start GT5 from cold, stay in the main menu.
3. `PS3=192.168.1.11 ./deploy_4p.sh apply` — it pokes the caves first, the hooks last, then runs
   `verify` (expect `patched=250 original=0 unexpected=0`).
4. Arcade → 2P Split Screen → track → cars for players 1 and 2 → options → answer "Spieler 3
   (Controller 3) faehrt mit?" with **Yes**, "Spieler 4" with **Yes** → race.
5. Expected: four views (quadrants), four cars, controllers 3 and 4 drive cars 3 and 4.
6. Back out with `./deploy_4p.sh off` or restart the game. `./deploy_4p.sh verify` reports the
   patched/original word counts at any time.
