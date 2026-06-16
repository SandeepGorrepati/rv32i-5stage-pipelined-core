# RV32I 5-Stage Pipelined Processor (SystemVerilog)

![RTL Lint](https://github.com/SandeepGorrepati/rv32i-5stage-pipelined-core/actions/workflows/lint.yml/badge.svg)

This project implements a simple RV32I processor using a classic five-stage pipeline.
The design was written in SystemVerilog and verified using simulation with Icarus Verilog.

The goal of this project was to understand how pipelined processors work in practice,
including datapath design, hazard handling, and basic verification using directed tests.

---

## Pipeline Stages

![RV32I 5-stage pipeline](docs/diagrams/pipeline.png)

The processor follows the standard five-stage pipeline structure.

| Stage | Description |
|------|-------------|
| IF | Instruction Fetch |
| ID | Instruction Decode and Register Read |
| EX | Execute (ALU operations) |
| MEM | Data Memory Access |
| WB | Write Back to Register File |

The program counter increments by 4 bytes for sequential instruction execution.

---

## Waveform (real simulation output)

![Branch + pipeline-flush waveform](docs/waveforms/branch_pipeline.png)

Captured from an actual Icarus simulation. It shows the **funct3-decoded branch
condition** (`idex_f3` → `ex_branch_cond`), the taken branch (`ex_take_branch`)
triggering a pipeline flush (`flush_ifid`), and `dbg_x10` settling to the correct
final value (`7`). This is the path of the real branch bug found and fixed by the
self-checking compliance suite — see `proof/BUG_NOTES.md`.

---

## Implemented Features

The processor supports a subset of the RV32I instruction set and includes:

- 5-stage pipelined datapath
- Register file (x0 hardwired to zero)
- Arithmetic and logical ALU operations
- Load and store instructions
- JAL (jump and link)
- Data hazard forwarding
- Load-use hazard stall logic
- Illegal instruction detection

---

## Hazard Handling

### Data Hazards (Forwarding)

Forwarding paths allow dependent instructions to use results from later pipeline
stages without waiting for writeback.

Example:

~~~text
add x1, x2, x3
add x4, x1, x5
~~~

The result from the first instruction is forwarded directly to the second instruction.

---

### Load-Use Hazard

If an instruction depends on a value loaded from memory,
the pipeline inserts a stall cycle.

Example:

~~~text
lw x5, 0(x1)
add x6, x5, x2
~~~

The dependent instruction waits until the loaded value becomes available.

---

### Control Hazards

When a branch is taken, instructions already in the pipeline are flushed
and execution resumes from the correct program counter.

---

## Verification

The processor was verified using directed simulation tests.

Each test loads a small RISC-V program into instruction memory and checks
the resulting register or memory state.

Test coverage includes:

- ALU operations
- Branch taken
- Branch not taken
- Forwarding hazards
- Load-use hazards
- Store forwarding
- Memory operations (LW/SW)
- JAL instruction
- Illegal instruction detection

All tests pass in the regression flow.

---

## Project Structure

~~~text
proj1_rv32i/
│
├── rtl/
│   ├── core_pipe5.sv
│   ├── core_single.sv
│   ├── regfile.sv
│   └── alu.sv
│
├── tb/
│   └── testbenches and directed test programs
│
├── scripts/
│   └── simulation and automation scripts
│
├── docs/
│   └── design notes
│
├── sim/
│   └── simulator configuration
│
├── Makefile
├── run_demo.sh
└── README.md
~~~

---

## Running the Project

Run the full verification suite:

~~~bash
make test
~~~

Run the short demo used for quick demonstrations:

~~~bash
./run_demo.sh
~~~

Example output:

~~~text
===== RV32I 5-Stage Pipeline Demo =====

[1/3] ALU test
PASS: x10=12

[2/3] Load-use hazard test
PASS

[3/3] Branch flush test
PASS

===== Demo complete =====
~~~
## Waveform Proof

### Forwarding Behavior
![Forwarding](docs/forwarding_waveform.png)

### Hazard Detection
![Hazard](docs/hazard_waveform.png)
---

## Performance & Lint Proof

This isn't just "it runs" — there's committed evidence in [`proof/`](proof/):
- **Verilator lint** logs across all five RTL modules (`verilator_lint_core_pipe5.log`).
- **Regression log** over the directed suite (`rv32i_pipe5_regression.log`).
- **Performance counters** wired into the testbench — core cycle count, retired
  instruction count, stall count, and **CPI** reporting (`rv32i_lint_and_perf_summary.md`).

CI: every push runs a Verilator lint via GitHub Actions (see `.github/workflows/lint.yml`).

## ISA Compliance — self-checking suite (✅ included)

A generated, **spec-checked** instruction-level test suite lives in [`compliance/`](compliance/):
a Python RV32I assembler + reference ISA model emits one program per instruction, each
leaving a known result in `x10`; the expected value is computed from the **spec**, not
the DUT. Run it:
```bash
bash scripts/run_compliance.sh        # -> "COMPLIANCE: 15 passed, 0 failed"
```
Covers ADDI/ADD/SUB/AND/OR/XOR/SLL/SRL/SRA/SLT/LUI/LW/SW/BEQ/BNE/JAL.

**Next level — official riscv-tests:** running the standard `rv32ui` suite needs the
riscv-gnu-toolchain + a minimal `ECALL`/`tohost` hook (this core is a CSR-less RV32I
subset). Steps are in [`compliance/README.md`](compliance/README.md). The self-checking
suite above already gives spec-checked per-instruction coverage with zero dependencies.

## Tools Used

- SystemVerilog
- Icarus Verilog
- GTKWave
- Ubuntu / WSL

---

## Author

Sandeep Gorrepati

## Pipeline diagram
```text
        +----+    +----+    +----+    +-----+    +----+
  PC -> | IF | -> | ID | -> | EX | -> | MEM | -> | WB | -> regfile
        +----+    +----+    +----+    +-----+    +----+
                    ^          ^         |
        load-use stall      forwarding (EX/MEM, MEM/WB -> EX)
        (hazard unit)       branch resolved in EX -> flush IF/ID & ID/EX on taken
```
- **Forwarding unit:** bypasses EX/MEM and MEM/WB results back to EX to resolve RAW hazards.
- **Hazard unit:** inserts one stall on a load-use dependency.
- **Branch handling:** not-taken by default; on a taken branch the younger stages are flushed.
- **Perf counters:** cycle / retired / stall / CPI (see `proof/`).
