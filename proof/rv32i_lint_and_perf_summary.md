# RV32I Pipeline RTL Lint and Performance Proof

## Scope
RTL lint and simulation proof for the RV32I 5-stage pipelined processor.

## RTL Files Checked
- rtl/alu.sv
- rtl/regfile.sv
- rtl/hazard_detection_unit.sv
- rtl/forwarding_unit.sv
- rtl/core_pipe5.sv

## Tooling
- Verilator lint
- Icarus Verilog simulation
- GTKWave waveform generation

## Regression Targets
- ALU execution
- Branch taken
- Branch not taken
- Forwarding
- Load-use hazard
- Store forwarding

## Added Performance Visibility
- Core cycle counter
- Retired instruction counter
- Stall counter
- CPI reporting in testbench

## Resume-Safe Claim
Performed Verilator lint and simulation-based RTL quality checks on RV32I 5-stage pipeline modules; added cycle count, retired instruction, stall count, and CPI reporting for pipeline performance visibility.
