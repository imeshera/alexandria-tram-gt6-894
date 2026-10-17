#!/bin/zsh
# Regenerates the GT6 894 lettering SVGs (mm) with the CoreText tool (tools/lettering/text2svg.swift).
# Usage: ./make_svgs.sh <path-to-compiled-text2svg> [car_no]
#   compile: swiftc -O text2svg.swift -o text2svg   (macOS; run from tools/lettering)
set -e
T=${1:-./text2svg}; N=${2:-894}
cd "$(dirname "$0")"
ar=$(echo $N | sed 's/0/٠/g;s/1/١/g;s/2/٢/g;s/3/٣/g;s/4/٤/g;s/5/٥/g;s/6/٦/g;s/7/٧/g;s/8/٨/g;s/9/٩/g')
for flip in 0 1; do
  s=$([ $flip = 0 ] && echo R || echo L)        # R = unflipped, L = mirrored
  $T svg/num${N}_$s.svg   "Helvetica-Bold" 100 $flip "$N"
  $T svg/numar${N}_$s.svg "GeezaPro-Bold"  100 $flip "$ar"
  $T svg/apta_$s.svg      "DecoType Naskh" 100 $flip "هيئة النقل العام بالإسكندرية"
  $T svg/route_$s.svg     "GeezaPro-Bold"  100 $flip "٤"
  $T svg/dest_$s.svg      "GeezaPro-Bold"  100 $flip "أبو الدرداء"
done
