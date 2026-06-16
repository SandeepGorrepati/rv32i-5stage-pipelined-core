#!/usr/bin/env bash
# ============================================================
#  Runs the self-checking RV32I compliance suite with Icarus Verilog.
#  Each test loads its hex, runs the core, checks dbg_x10 vs the
#  manifest's expected value.
#
#  Prereq: iverilog + vvp (sudo apt install -y iverilog)
#  Usage:  bash scripts/run_compliance.sh
# ============================================================
set -e
cd "$(dirname "$0")/.."
mkdir -p build

# (re)generate tests + manifest
python3 scripts/gen_compliance.py >/dev/null

RTL="rtl/core_pipe5.sv rtl/alu.sv rtl/regfile.sv rtl/forwarding_unit.sv rtl/hazard_detection_unit.sv"
pass=0; fail=0

while read -r name exp; do
  [ -z "$name" ] && continue
  cp "compliance/$name.hex" build/padded.hex
  iverilog -g2012 -o build/comp.out $RTL tb/tb_core_pipe5_compliance.sv 2>/dev/null
  out=$(vvp build/comp.out +EXPECTED="$exp")
  if echo "$out" | grep -q "COMPLIANCE PASS"; then
    printf "PASS  %-14s x10=%s\n" "$name" "$exp"; pass=$((pass+1))
  else
    printf "FAIL  %-14s\n" "$name"; echo "$out"; fail=$((fail+1))
  fi
done < compliance/manifest.txt

echo "========================================"
echo " COMPLIANCE: $pass passed, $fail failed"
echo "========================================"
[ "$fail" -eq 0 ]
