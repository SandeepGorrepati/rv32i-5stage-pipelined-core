`timescale 1ns/1ps
module tb_oracle;
  reg clk=0,rst=1;
  always #5 clk=~clk;
  wire [31:0] pc,x10;
  wire illegal;
  core_pipe5 #(.IMEM_WORDS(256),.IMEM_HEX("build/oracle.hex")) dut(.clk(clk),.rst(rst),.pc(pc),.illegal_insn(illegal),.dbg_x10(x10));
  reg [31:0] expected[0:31];
  integer terminal,i;
  initial begin
    if(!$value$plusargs("terminal=%d",terminal)) $fatal(1,"terminal missing");
    $readmemh("build/expected.hex",expected);
    repeat(3) @(negedge clk); rst=0;
    do begin
      @(negedge clk);
      if(illegal) $fatal(1,"unexpected illegal");
    end while(!(dut.memwb_valid && dut.memwb_pc==terminal));
    repeat(2) @(negedge clk); #1;
    for(i=1;i<32;i=i+1)
      if(dut.u_rf.regs[i] !== expected[i])
        $fatal(1,"x%0d got=%h expected=%h",i,dut.u_rf.regs[i],expected[i]);
    $display("PASS: full register state"); $finish;
  end
  initial begin #20000; $fatal(1,"oracle watchdog"); end
endmodule
