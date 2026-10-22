# Five-stage RV32I-subset core

![Functional regression](https://github.com/SandeepGorrepati/rv32i-5stage-pipelined-core/actions/workflows/regression.yml/badge.svg)
![RTL lint](https://github.com/SandeepGorrepati/rv32i-5stage-pipelined-core/actions/workflows/lint.yml/badge.svg)

An educational SystemVerilog processor with forwarding, a load-use stall, branch/JAL redirects, pipeline valid bits, and self-checking verification. The primary deliverable is a reproducible implementation with tests that expose and prevent real bugs.

## Implemented scope

- R-type ADD/SUB, AND/OR/XOR, SLL/SRL/SRA, SLT/SLTU.
- Immediate arithmetic/logical/shift operations, aligned LW/SW, JAL.
- All six conditional branches: BEQ/BNE/BLT/BGE/BLTU/BGEU.
- EX/MEM and MEM/WB forwarding, one-cycle load-use stalls, wrong-path flushes.
- x0 reads as zero; writes to x0 are discarded.
- Pipeline-valid retirement counts include real NOPs, branches, stores, and x0 writes. Reset/stall/flush bubbles are excluded.
- Unsupported opcode/funct encodings raise an `illegal_insn` indication and suppress their register, memory, branch, and retirement effects.

This is not a complete RV32I implementation or an ISA-certified core. LUI, AUIPC, JALR, byte/halfword memory operations, traps, CSRs, interrupts, caches, misalignment handling, and privilege are not implemented. Illegal instructions produce an indication, not an architectural trap. Word-addressed memories are finite and high address bits are truncated. Use the default 32-bit datapath; arbitrary XLEN values are not validated.

## Reproduce with free tools

Install Python 3, Icarus Verilog, GNU Make, and Bash. From the repository root:

```bash
chmod +x scripts/*.sh
bash scripts/run_all_pipe5.sh
iverilog -g2012 -s tb_retirement -o build/retirement rtl/*.sv tb/tb_retirement.sv
vvp build/retirement
iverilog -g2012 -s tb_decode -o build/decode rtl/*.sv tb/tb_decode.sv
vvp build/decode
python3 scripts/run_oracle.py
```

GitHub Actions executes these commands and retains logs. Any data mismatch or watchdog expires with a nonzero status.

## Verification evidence

| Layer | Checks |
|---|---|
| Existing regression | Six directed ALU, branch, forwarding, load-use, and store-forward cases |
| Retirement | Ordered PCs through NOP/x0, store, taken branch, JAL, flushed writes, load-use, and reset |
| Decode | Five unsupported encodings must raise indications without architectural side effects |
| Python instruction oracle | 12 branch programs, 12 dependency-distance programs, 20 deterministic arithmetic programs; compare all nonzero registers |

The instruction oracle decodes machine words and computes final state using Python integers, independently of pipeline scheduling. Its random programs use ADDI and R-type operations; they do not claim randomized coverage of every supported instruction. The legacy `compliance/` directory contains custom tests, not the official RISC-V architectural certification suite.

## Bugs found and fixed

1. Retirement previously counted only writes to nonzero registers. Pipeline valid bits now distinguish real instructions from injected bubbles.
2. An extra registered WB stage delayed register-file writes and broke dependency distances missed by short tests. MEM/WB now drives the falling-edge register file directly. The Python oracle exposed the original failure.
3. The old testbench printed FAIL without failing the process. Failures now use `$fatal`; CI uses Bash `pipefail`.
4. Unsupported load/store/ALU encodings could execute as other operations. Decode now checks supported encodings before enabling side effects.

The register file writes on the falling edge. This is an explicit educational timing choice, not a claim of a production standard-cell implementation. Reported CPI includes fetched padding NOPs and pipeline fill/control effects; it is not a workload benchmark. See [upgrade validation](proof/UPGRADE_VALIDATION.md) for dated evidence.
