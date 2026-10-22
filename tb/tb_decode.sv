`timescale 1ns/1ps
module tb_decode;
  reg clk=0,rst=1;
  always #5 clk=~clk;
  wire [31:0] pc,x10;
  wire illegal;
  core_pipe5 dut(.clk(clk),.rst(rst),.pc(pc),.illegal_insn(illegal),.dbg_x10(x10));
  integer errors=0;
  always @(negedge clk) if(!rst && illegal) errors=errors+1;
  initial begin
    #1;
    dut.imem[0]=32'h00700093; // x1=7
    dut.imem[1]=32'h00100023; // SB unsupported
    dut.imem[2]=32'h00000383; // LB unsupported
    dut.imem[3]=32'h021081b3; // MUL unsupported
    dut.imem[4]=32'h02009113; // reserved SLLI encoding
    dut.imem[5]=32'h00002463; // reserved branch funct3
    dut.imem[6]=32'h00500413; // x8=5 (must not be skipped)
    dut.imem[7]=32'h0000006f; // terminal loop
    repeat(3) @(negedge clk); rst=0;
    repeat(40) @(negedge clk); #1;
    if(errors !== 5) $fatal(1,"illegal indications=%0d expected=5",errors);
    if(dut.u_rf.regs[2] !== 0 || dut.u_rf.regs[3] !== 0 || dut.u_rf.regs[7] !== 0 || dut.dmem[0] !== 0)
      $fatal(1,"unsupported instruction changed architectural state");
    if(dut.u_rf.regs[8] !== 5) $fatal(1,"reserved branch redirected PC");
    $display("PASS: five unsupported encodings flagged with no register/store/branch side effects");
    $finish;
  end
  initial begin #10000; $fatal(1,"decode timeout"); end
endmodule
