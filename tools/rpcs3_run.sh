#!/bin/bash
# Launch RPCS3 with GT5 the way the emulator work expects it:
#   - MEMLOCK raised to 2 GiB first (RPCS3 needs it for its "sudo memory" mirror; without it
#     the log fills with "Failed to lock sudo memory" and the first run froze in the main menu)
#   - fresh RPCS3.log, GUI kept (debugger), game window in windowed mode.
# Usage: rpcs3_run.sh [--no-gui]
export DISPLAY="${DISPLAY:-:0}"
LOG="$HOME/.cache/rpcs3/RPCS3.log"
EBOOT="$HOME/gt5re/disc/game/PS3_GAME/USRDIR/EBOOT.BIN"
pkill -x rpcs3 2>/dev/null && sleep 3
sudo -n prlimit --pid $$ --memlock=2147483648:2147483648 || echo "warning: could not raise memlock" >&2
: > "$LOG"
cd "$HOME/gt5re" || exit 1
nohup rpcs3 "$@" "$EBOOT" > "$HOME/gt5re/logs/rpcs3_stdout.log" 2>&1 &
echo "rpcs3 pid $!  (memlock $(ulimit -l) KB)"
