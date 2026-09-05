#!/bin/bash
: "${PS3:?Bitte PS3=<ip> setzen}"
PID=$(curl -s --max-time 10 "http://$PS3/home.ps3mapi" | grep -oiE 'proc=0x[0-9a-f]+' | head -1 | cut -d= -f2)
rd() { curl -s --max-time 20 "http://$PS3/getmem.ps3mapi?proc=$PID&addr=$1&len=4" | grep -oiE '\b[0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}\b' | head -1 | tr -d ' '; }
LR=$(rd 0x1949080); CNT=$(rd 0x1949084)
echo "Aufrufer-LR (schreibt 22 auf Slot 2): 0x$LR"
echo "Anzahl:                               $((16#${CNT:-0}))"
echo "-> Resetter-Funktion enthaelt den bl kurz vor 0x$LR"
