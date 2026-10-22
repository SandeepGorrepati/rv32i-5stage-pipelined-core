# Upgrade validation - 2026-10-22

Validated code commit: 0bef57091ac102e5911eef32d7adc779421ce6f9. Six legacy cases, retirement, unsupported-decode test, and 44 Python-oracle programs passed.

[Recorded GitHub Actions run](https://github.com/SandeepGorrepati/rv32i-5stage-pipelined-core/actions/runs/39753849619). Subsequent documentation or path-filter changes do not extend the tested functionality. Re-run the workflow after code changes. Full logs are retained as Actions artifacts subject to GitHub retention limits.

## Observed log excerpts

```text
PASS: x10 = 12
PASS: x10 = 12
PASS: x10 = 12
PASS: x10 = 6
PASS: x10 = 6
PASS: x10 = 7
PASS: retirement order, NOP/x0, store, branch, JAL, flush, load-use, reset
PASS: five unsupported encodings flagged with no register/store/branch side effects
branch_f3_0_taken_True PASS: full register state
branch_f3_0_taken_False PASS: full register state
branch_f3_1_taken_True PASS: full register state
branch_f3_1_taken_False PASS: full register state
branch_f3_4_taken_True PASS: full register state
branch_f3_4_taken_False PASS: full register state
branch_f3_5_taken_True PASS: full register state
branch_f3_5_taken_False PASS: full register state
branch_f3_6_taken_True PASS: full register state
branch_f3_6_taken_False PASS: full register state
branch_f3_7_taken_True PASS: full register state
branch_f3_7_taken_False PASS: full register state
dependency_gap_0_rs1 PASS: full register state
dependency_gap_0_rs2 PASS: full register state
dependency_gap_1_rs1 PASS: full register state
dependency_gap_1_rs2 PASS: full register state
dependency_gap_2_rs1 PASS: full register state
dependency_gap_2_rs2 PASS: full register state
dependency_gap_3_rs1 PASS: full register state
dependency_gap_3_rs2 PASS: full register state
dependency_gap_4_rs1 PASS: full register state
dependency_gap_4_rs2 PASS: full register state
dependency_gap_5_rs1 PASS: full register state
dependency_gap_5_rs2 PASS: full register state
random_seed_0 PASS: full register state
random_seed_1 PASS: full register state
random_seed_2 PASS: full register state
random_seed_3 PASS: full register state
random_seed_4 PASS: full register state
random_seed_5 PASS: full register state
random_seed_6 PASS: full register state
random_seed_7 PASS: full register state
random_seed_8 PASS: full register state
random_seed_9 PASS: full register state
random_seed_10 PASS: full register state
random_seed_11 PASS: full register state
random_seed_12 PASS: full register state
random_seed_13 PASS: full register state
random_seed_14 PASS: full register state
random_seed_15 PASS: full register state
random_seed_16 PASS: full register state
random_seed_17 PASS: full register state
random_seed_18 PASS: full register state
random_seed_19 PASS: full register state
PASS: 12 branch + 12 dependency-distance + 20 arithmetic programs
```

These are observed excerpts, not illustrative expected output. Passing this finite suite does not establish exhaustive correctness.

