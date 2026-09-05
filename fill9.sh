#!/bin/bash
# Completes PDIPFS/9 from the PS3: fetch missing dirs, then re-check counts until clean.
cd ~/gt5re
R=ftp://192.168.1.11/dev_hdd0/game/BCES00569/USRDIR/PDIPFS/9
L=update/USRDIR/PDIPFS/9
LFTP_SET="set net:timeout 30; set net:max-retries 2; set net:persist-retries 0; set net:reconnect-interval-base 3"
get() { echo "hole 9/$1 $(date +%H:%M:%S)"; timeout 600 lftp -e "$LFTP_SET; mirror /dev_hdd0/game/BCES00569/USRDIR/PDIPFS/9/$1 $L/$1; quit" 192.168.1.11; sleep 1; }
for round in 1 2 3 4 5 6 7 8; do
  echo "=== Runde $round $(date +%H:%M) ==="
  until curl -s -m 10 $R/ | grep -q "^d"; do echo "PS3-FTP antwortet nicht, warte 2 min"; sleep 120; done
  for n in $(diff <(curl -s -m 10 $R/ | awk '/^d/ && $NF !~ /^\.\.?$/ {print $NF}' | sort) <(ls $L | sort) | awk '/^</ {print $2}'); do get $n; done
  : > 9_fehlt.txt
  for d in $L/*/; do n=$(basename $d); r=$(curl -s -m 10 $R/$n/ | grep -c '^-'); l=$(find $d -type f | wc -l); [ "$r" -eq "$l" ] || echo "$n" >> 9_fehlt.txt; done
  echo "fehlend: $(wc -l < 9_fehlt.txt)"
  [ -s 9_fehlt.txt ] || { echo "9/ vollständig $(date +%H:%M)"; exit 0; }
  for n in $(cat 9_fehlt.txt); do get $n; done
  sleep 60
done
echo "aufgegeben nach 8 Runden"
