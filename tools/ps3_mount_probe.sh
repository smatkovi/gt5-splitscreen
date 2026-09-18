#!/bin/bash
# Mount a game on the PS3 through webMAN's web interface while watching whether the
# console stays alive (ping, webMAN HTTP, temperatures, /dev_bdvd contents).
#
# Usage: PS3=<ip> tools/ps3_mount_probe.sh "<absolute game path on the console>" [seconds]
#   e.g. PS3=192.168.1.11 tools/ps3_mount_probe.sh \
#          "/dev_hdd0/PS3ISO/LittleBigPlanet Karting (Europe) (En,Fr,De,Es,It,Nl,Pt,Sv,No,Da,Fi,Pl,Ru).iso" 90
#
# The mount request is sent 10 s after the start; everything is logged to stdout and to
# $LOG (default: ps3_mount_probe_<timestamp>.log in the current directory).
# NOTE: this changes the console state (mounts a game). Run it only with Sebastian's OK.

set -u
PS3="${PS3:-192.168.1.11}"
GAME="${1:?game path required}"
DUR="${2:-90}"
LOG="${LOG:-ps3_mount_probe_$(date +%Y%m%d_%H%M%S).log}"

urlenc() { python3 -c 'import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1], safe="/"))' "$1"; }

status() {
    local t; t=$(date +%T)
    local p="ping:-"; ping -c1 -W1 "$PS3" >/dev/null 2>&1 && p="ping:ok" || p="ping:FAIL"
    local h; h=$(curl -s -m 4 "http://$PS3/cpursx.ps3" | python3 -c '
import sys,re,html
t=html.unescape(re.sub(r"<[^>]+>"," ",sys.stdin.read()))
m=re.search(r"CPU: (\d+)°C \(MAX: \d+°C\)\s+RSX: (\d+)°C",t); f=re.search(r"FAN SPEED:\s+(\d+)%",t)
u=re.search(r"(\d\d:\d\d:\d\d)(?=\s*\d+d )",t)
print("http:ok cpu=%s rsx=%s fan=%s%% up=%s"%(m.group(1),m.group(2),f.group(1),u.group(1)) if m and f and u else "http:ok(unparsed)")' 2>/dev/null)
    [ -z "$h" ] && h="http:FAIL"
    echo "$t $p $h" | tee -a "$LOG"
}

bdvd() {
    echo "--- /dev_bdvd:" | tee -a "$LOG"
    curl -s -m 8 "ftp://$PS3/dev_bdvd/" | awk '{print "    " $NF}' | tee -a "$LOG"
    curl -s -m 8 "ftp://$PS3/dev_bdvd/PS3_GAME/PARAM.SFO" -o /tmp/ps3_probe_param.sfo 2>/dev/null && python3 - <<'PY' | tee -a "$LOG"
import struct
d=open('/tmp/ps3_probe_param.sfo','rb').read()
if d[:4]==b'\0PSF':
    kt,dt,n=struct.unpack('<III',d[8:20])
    for i in range(n):
        ko,fmt,ln,ml,do=struct.unpack('<HHIII',d[20+i*16:36+i*16])
        k=d[kt+ko:d.index(b'\0',kt+ko)].decode(); v=d[dt+do:dt+do+ln]
        if k in ('TITLE','TITLE_ID'): print('    ',k,'=',v.rstrip(b'\0').decode('utf-8','replace'))
PY
}

echo "== mount probe $(date '+%F %T') PS3=$PS3 game=$GAME" | tee -a "$LOG"
echo "-- before" | tee -a "$LOG"
status; bdvd
for i in 1 2 3 4; do sleep 2; status; done
echo "-- sending mount request" | tee -a "$LOG"
curl -s -m 30 "http://$PS3/mount.ps3$(urlenc "$GAME")" -o /tmp/ps3_probe_mount.html
echo "   mount request returned rc=$? ($(wc -c </tmp/ps3_probe_mount.html) bytes)" | tee -a "$LOG"
python3 -c '
import re,html,sys
s=open("/tmp/ps3_probe_mount.html",encoding="utf-8",errors="replace").read()
t=html.unescape(re.sub(r"<[^>]+>"," ",re.sub(r"<script.*?</script>","",s,flags=re.S)))
t=" ".join(t.split()); i=t.lower().find("mount")
print("   response:", t[max(0,i-80):i+200])' 2>/dev/null | tee -a "$LOG"
END=$((SECONDS + DUR))
while [ $SECONDS -lt $END ]; do sleep 2; status; done
echo "-- after" | tee -a "$LOG"
bdvd
echo "== done, log: $LOG" | tee -a "$LOG"
