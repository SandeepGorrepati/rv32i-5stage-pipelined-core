# Bug found & fixed — branch unit ignored funct3

## How it was found
The self-checking ISA compliance suite (`scripts/run_compliance.sh`) flagged
`bne_nottaken` as FAIL (`x10=99`, expected `7`) while every other test passed.

## Root cause
The EX-stage branch condition only compared equality and ignored `funct3`:
```systemverilog
wire ex_beq         = (ex_rs1_fwd == ex_rs2_fwd);
wire ex_take_branch = idex_is_branch && ex_beq;   // every branch behaved as BEQ
```
So **all conditional branches behaved as BEQ**. `BNE x5,x6` with `x5==x6` was wrongly
*taken* (BNE should be taken only when operands differ), skipping the fall-through path.

## Debug flow
Reproduced under Icarus → tb reported `x10=99` (poison value), meaning the not-taken
path's `addi x10,7` was skipped → branch was taken when it shouldn't be → inspected the
branch RTL → found `funct3` was decoded into `idex_f3` but never used in the condition.

## Fix
Decode `funct3` in the EX branch condition (full RV32I branch set):
```systemverilog
wire ex_eq  = (ex_rs1_fwd == ex_rs2_fwd);
wire ex_lt  = ($signed(ex_rs1_fwd) < $signed(ex_rs2_fwd));
wire ex_ltu = (ex_rs1_fwd < ex_rs2_fwd);
case (idex_f3)
  3'b000: ex_branch_cond = ex_eq;   // BEQ
  3'b001: ex_branch_cond = ~ex_eq;  // BNE
  3'b100: ex_branch_cond = ex_lt;   // BLT
  3'b101: ex_branch_cond = ~ex_lt;  // BGE
  3'b110: ex_branch_cond = ex_ltu;  // BLTU
  3'b111: ex_branch_cond = ~ex_ltu; // BGEU
  default: ex_branch_cond = 1'b0;
endcase
```

## Result
After the fix: **compliance suite 14/14 PASS** (Icarus). See `proof/compliance_log.txt`.
A directed-test-only flow would have missed this; the self-checking compliance suite
caught it because BNE's not-taken behavior was explicitly checked against a reference.
