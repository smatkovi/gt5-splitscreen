# Gran Turismo 5 (BCES00569, update 2.17) — 4-player split battle

RAM patch + Adhoc script mod that turns the 2-player "2P Split Screen" arcade mode into a
4-player race (four viewports in quadrants, four human-controlled cars on controller ports 0-3).

Status (2026-09-05): **verified in RPCS3** (0.0.42-19916, LLVM PPU, ASMJIT SPU) — four views in a
quadrant layout, four cars, all four pads steer their car, ~47 FPS, no crash through the race.
**PS3 hardware test still pending** (see "Testing on the PS3").

## What is in here

| file | purpose |
|------|---------|
| `EBOOT.BIN` | **patched, re-encrypted 2.17 update EBOOT** (NPDRM UEXEC, key revision 0x19, licence FREE, unsigned) — the PS3 deliverable |
| `EBOOT_patched.elf` | the decrypted patched ELF the EBOOT was built from (`tools/build_eboot.sh`), `SHA1SUMS` |
| `rpcs3-patch.yml` | RPCS3 patch groups (`~/.config/rpcs3/patches/patch.yml`), key `PPU-223cc85f…` |
| `deploy_4p.sh` | PS3 RAM-poke script (`apply\|off\|verify`) — **only useful for `verify`**, see below |
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

## Why the PS3 needs the patched EBOOT (and not RAM pokes)

Both external arrays are created in the **MOrganizer constructor**, and the script bootstrap
creates that object at game start (`bootstrap_phase2.ad: main::ORG = gtengine::MOrganizer()`).
Poking the words into a running game therefore leaves the arrays uninitialised: the first race
after a warm `apply` hung on the console (attract-mode demo, 2026-09-05). The patch has to be in
the code before boot, i.e. in the EBOOT. `deploy_4p.sh verify` is still handy to confirm that a
running game carries the patched words (`patched=250`).

## Testing on the PS3

1. Back up `/dev_hdd0/game/BCES00569/USRDIR/EBOOT.BIN` (the original 2.17 update EBOOT,
   9505120 bytes, sha1 of its decrypted form `306f86c6…0452`).
2. Upload this folder's `EBOOT.BIN` to `/dev_hdd0/game/BCES00569/USRDIR/EBOOT.BIN` (FTP).
   The script mod (`mod/pdipfs/*`) must be in `USRDIR/PDIPFS/` as before.
3. Start GT5 from the XMB. If the console refuses the SELF (error 80010007) the SELF type/key
   revision is not accepted by this firmware — report the error code.
4. (Optional) `PS3={ip} ./deploy_4p.sh verify` → expect `patched=250 original=0 unexpected=0`.
5. Arcade → 2P Split Screen → track → cars → options → "Spieler 3 (Controller 3) faehrt mit?"
   **Yes**, "Spieler 4" **Yes** → race. Do not idle in the main menu (the attract demo also
   exercises the race code).
6. Expected: four views (quadrants), four cars, controllers 3 and 4 drive cars 3 and 4.
7. Back out by restoring the backed-up EBOOT.BIN.
