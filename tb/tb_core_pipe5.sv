`timescale 1ns/1ps
module tb_core_pipe5;

  reg clk;
  reg rst;
  wire [31:0] pc;
  wire illegal;
  wire [31:0] x10;

  integer cycle_count;
  real cpi;

  // Default expected value if not passed from compiler
`ifndef EXPECT_X10
  `define EXPECT_X10 0
`endif

  // DUT
  core_pipe5 #(
    .IMEM_WORDS(64),
    .IMEM_HEX("build/padded.hex")
  ) dut (
    .clk(clk),
    .rst(rst),
    .pc(pc),
    .illegal_insn(illegal),
    .dbg_x10(x10)
  );

  // Clock
  initial clk = 0;
  always #5 clk = ~clk;

  // Testbench cycle counter
  always @(posedge clk) begin
    if (rst)
      cycle_count <= 0;
    else
      cycle_count <= cycle_count + 1;
  end

  // Main simulation
  initial begin
    $dumpfile("build/core_pipe5.vcd");
    $dumpvars(0, tb_core_pipe5);

    $display("=== SIM START ===");
    $display("EXPECTED x10 = %0d", `EXPECT_X10);

    cycle_count = 0;
    cpi = 0.0;
    rst = 1;
    #20;
    rst = 0;

    // Let pipeline execute
    #400;

    if (illegal) begin
      $display("FAIL: illegal instruction detected");
    end
    else if (x10 !== `EXPECT_X10) begin
      $display("FAIL: x10 = %0d, expected = %0d", x10, `EXPECT_X10);
    end
    else begin
      $display("PASS: x10 = %0d", x10);
    end

    $display("TB Cycle count      = %0d", cycle_count);
    $display("Core cycle count    = %0d", dut.cycle_count);
    $display("Retired instructions= %0d", dut.instr_count);
    $display("Stall count         = %0d", dut.stall_count);

    if (dut.instr_count != 0) begin
      cpi = dut.cycle_count * 1.0 / dut.instr_count;
      $display("CPI                 = %0f", cpi);
    end
    else begin
      $display("CPI                 = N/A (no retired instructions)");
    end

    $display("Final PC            = 0x%08h", pc);

    $finish;
  end

endmodule
