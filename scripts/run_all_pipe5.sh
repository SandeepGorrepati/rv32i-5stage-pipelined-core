#!/bin/bash
set -e

echo "===== Running RV32I PIPE5 regression ====="

echo
echo "=== ALU ==="
make alu

echo
echo "=== BRANCH TAKEN ==="
make branch_taken

echo
echo "=== BRANCH NOT TAKEN ==="
make branch_not_taken

echo
echo "=== FORWARDING ==="
make forward

echo
echo "=== LOAD-USE HAZARD ==="
make load_use

echo
echo "=== STORE FORWARD ==="
make store_forward

echo
echo "===== RV32I PIPE5 regression completed ====="
