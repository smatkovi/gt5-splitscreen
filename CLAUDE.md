# Working conventions for ~/gt5re (GT5 3P/4P splitscreen RE)

These rules come from Sebastian and apply to every session in this directory.

## Language
- Talk to Sebastian in **German**.
- Everything that goes into git and into source code — commit messages, code comments,
  READMEs, script help text — is written in **English**.

## File editing
- Edit files **with Python** (`python3 - <<'PY' ... PY` or a script). Never use
  `sed`/`perl` regex substitutions on project files.

## Commands handed to Sebastian
- **Read-only commands**: bundle all of them into a *single* block and pipe through `more`.
- **Action commands** (deploy, poke, measure): keep them separate from read commands, give
  them complete and in execution order.
- **`sudo`**: the assistant has no password. Check `sudo -n true` first; if that fails,
  prepare the full command and ask Sebastian to run it — **one sudo command per block**,
  each followed by a new block (his terminal swallows follow-up lines otherwise).

## Downloads
- Large downloads (firmware PUP, AppImages, ISOs) use `aria2c`, not curl/wget.

## PS3 hardware (192.168.1.11, webMAN MOD 1.47.48 + PS3MAPI)
- The console is the reference state. **Never change anything on it without saying so first.**
- Reading (getmem, FTP download) is allowed at any time.
- Code pokes only take effect when set **cold in the main menu** (I-cache).

## Reverse-engineering hygiene
- New patch words are always cross-checked with capstone (`ppcdis.py`) before deployment.
- `OpenAdhoc` is a reference checkout — never patch it directly. Per test run:
  `git clone OpenAdhoc mod_x`, then rename all `*.Ad` to `*.ad`.
- Reference EBOOT: `~/gt5re/EBOOT.elf` (-> `eboot/EBOOT_orig.elf`), load address 0x10000,
  sha1 `306f86c62b9f03041c903be96ac59e5c3f130452`. Verify every RPCS3 copy against it.

## Journal
- Record every test in `~/gt5re/JOURNAL.md`: date, patch state, result — so nothing is
  measured twice.

## Python environment
- capstone/evdev live in `~/gt5re/.venv` (system Python is externally managed).
  Use `~/gt5re/.venv/bin/python`.
