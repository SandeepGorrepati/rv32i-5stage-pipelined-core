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
sudo apt install -y iverilog          # if needed
bash scripts/run_compliance.sh
```
Expected tail:
```
PASS  addi           x10=7
PASS  add            x10=7
...
========================================
 COMPLIANCE: 15 passed, 0 failed
========================================
```

## Coverage of the suite
ADDI, ADD, SUB, AND, OR, XOR, SLL, SRL, SRA, SLT, LUI, LW/SW, BEQ (taken),
BNE (not-taken), JAL — each with a spec-computed expected result.

## Extending to the OFFICIAL riscv-tests
The official `riscv-tests` (`rv32ui`) are the industry-standard ISA suite. To run them:
1. Install the **riscv-gnu-toolchain** (`riscv32-unknown-elf-gcc`).
2. Add a minimal **`tohost` hook**: the standard tests signal pass/fail by writing to a
   `tohost` symbol via `ECALL`. This core is a pure RV32I subset without CSR/trap, so
   either (a) add minimal `ECALL` + a `tohost` store-detect in the testbench, or (b)
   build the tests with a bare-metal linker script that redirects `tohost` to a fixed
   DMEM address the testbench polls.
3. `objcopy` each test ELF to hex, load into `imem`, run, and check the pass code.

That path needs the toolchain + the small `tohost`/`ECALL` addition, so it's a guided
next step. The self-checking suite above already gives spec-checked per-instruction
coverage today with zero external dependencies.
