#!/usr/bin/env bash
# Runs the RV32I compliance suite with Icarus. Reports every test + a summary
# (does NOT abort on a failing/unsupported instruction).
cd "$(dirname "$0")/.."
mkdir -p build
python3 scripts/gen_compliance.py >/dev/null
RTL="rtl/core_pipe5.sv rtl/alu.sv rtl/regfile.sv rtl/forwarding_unit.sv rtl/hazard_detection_unit.sv"
pass=0; fail=0; failed=""
while read -r name exp; do
  [ -z "$name" ] && continue
  cp "compliance/$name.hex" build/padded.hex
  if ! iverilog -g2012 -o build/comp.out $RTL tb/tb_core_pipe5_compliance.sv 2>build/comp_err.log; then
    printf "FAIL  %-14s (compile error)\n" "$name"; fail=$((fail+1)); failed="$failed $name"; continue
  fi
  out=$(vvp build/comp.out +EXPECTED="$exp" 2>&1)
  if echo "$out" | grep -q "COMPLIANCE PASS"; then
    printf "PASS  %-14s x10=%s\n" "$name" "$exp"; pass=$((pass+1))
  else
    printf "FAIL  %-14s (x10!=%s)\n" "$name" "$exp"; fail=$((fail+1)); failed="$failed $name"
  fi
done < compliance/manifest.txt
echo "========================================"
echo " COMPLIANCE: $pass passed, $fail failed"
[ -n "$failed" ] && echo " failing:$failed"
echo "========================================"
