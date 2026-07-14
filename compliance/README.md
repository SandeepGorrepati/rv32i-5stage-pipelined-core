# RV32I Compliance Suite (self-checking)

A generated, **self-checking instruction-level test suite** for the core. Each test is
a tiny program that exercises one instruction (or hazard/branch case), ends in a
self-loop, and leaves a known result in `x10` (`a0`). A reference RV32I model computes
the expected value, so every test is checked against the spec — not against the DUT
itself.

## What's here
- `../scripts/gen_compliance.py` — RV32I assembler + reference ISA model. Emits one
  `<name>.hex` per test plus `manifest.txt` (`<name> <expected_x10>`).
- `../tb/tb_core_pipe5_compliance.sv` — generic runner; checks `dbg_x10` vs `+EXPECTED`.
- `../scripts/run_compliance.sh` — loops the manifest, runs each test under Icarus.

## Run it
```bash
sudo apt install -y iverilog
bash scripts/run_compliance.sh
```

Expected tail:
```text
PASS  addi           x10=7
PASS  add            x10=7
...
========================================
 COMPLIANCE: 14 passed, 0 failed
========================================
```

## Coverage of the suite
Fourteen self-checking programs cover ADDI, ADD, SUB, AND, OR, XOR, SLL, SRL, SRA,
SLT, LW/SW, BEQ (taken), BNE (not taken), and JAL. Every expected `x10` value is
computed by the independent reference model.

## Extending to the official riscv-tests
The official `riscv-tests` (`rv32ui`) are the industry-standard ISA suite. Running
them requires the RISC-V GNU toolchain plus a minimal `tohost`/ECALL mechanism, which
this CSR-less educational core does not yet implement. The committed suite is therefore
described as self-checking instruction-level compliance testing, not official
`riscv-tests` certification.
