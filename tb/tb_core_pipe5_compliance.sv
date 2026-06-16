`timescale 1ns/1ps
//==============================================================================
// tb_core_pipe5_compliance.sv
// Generic self-checking runner for the compliance suite. Loads build/padded.hex
// (copied per-test by scripts/run_compliance.sh) and checks dbg_x10 against the
// expected value passed as +EXPECTED=<signed-decimal>.
//
//   vvp build/comp.out +EXPECTED=7
//==============================================================================
module tb_core_pipe5_compliance;

  reg         clk;
  reg         rst;
  wire [31:0] pc;
  wire        illegal;
  wire [31:0] x10;

  integer     expected;
  integer     cyc;

  core_pipe5 #(
    .IMEM_WORDS(64),
    .IMEM_HEX("build/padded.hex"),
    .DMEM_WORDS(64)
  ) dut (
    .clk(clk),
    .rst(rst),
    .pc(pc),
    .illegal_insn(illegal),
    .dbg_x10(x10)
  );

  initial clk = 0;
  always #5 clk = ~clk;

  initial begin
    if (!$value$plusargs("EXPECTED=%d", expected)) begin
      $display("COMPLIANCE FAIL: no +EXPECTED provided");
      $fatal;
    end

    rst = 1; #20 rst = 0;

    for (cyc = 0; cyc < 200; cyc = cyc + 1) begin
      @(posedge clk);

      if (illegal) begin
        $display("COMPLIANCE FAIL: illegal_insn at cyc=%0d pc=%h", cyc, pc);
        $fatal;
      end

      if ($signed(x10) == expected) begin
        $display("COMPLIANCE PASS: x10=%0d (expected=%0d) at cyc=%0d", $signed(x10), expected, cyc);
        $finish;
      end
    end

    $display("COMPLIANCE FAIL: timeout. x10=%0d expected=%0d pc=%h", $signed(x10), expected, pc);
    $fatal;
  end
endmodule
