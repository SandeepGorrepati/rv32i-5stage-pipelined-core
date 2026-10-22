`timescale 1ns/1ps
module tb_retirement;
  reg clk=0, rst=1;
  always #5 clk=~clk;
  wire [31:0] pc, x10;
  wire illegal;
  core_pipe5 dut(.clk(clk),.rst(rst),.pc(pc),.illegal_insn(illegal),.dbg_x10(x10));
  integer expected_pc[0:7];
  integer n=0;
  initial begin
    #1;
    // NOP, x1=7, store, taken branch, flushed write, x3=3,
    // JAL x0, flushed write, load, dependent add.
    dut.imem[0]=32'h00000013;
    dut.imem[1]=32'h00700093;
    dut.imem[2]=32'h00102023;
    dut.imem[3]=32'h00000463;
    dut.imem[4]=32'h06300113;
    dut.imem[5]=32'h00300193;
    dut.imem[6]=32'h0080006f;
    dut.imem[7]=32'h06300113;
    dut.imem[8]=32'h00002203;
    dut.imem[9]=32'h001202b3;
    expected_pc[0]=0; expected_pc[1]=4; expected_pc[2]=8;
    expected_pc[3]=12; expected_pc[4]=20; expected_pc[5]=24;
    expected_pc[6]=32; expected_pc[7]=36;
    repeat(3) @(negedge clk);
    rst=0;
    while(n<8) begin
      @(posedge clk);
      if(illegal) $fatal(1,"unexpected illegal instruction");
      if(dut.memwb_valid) begin
        if(dut.memwb_pc !== expected_pc[n])
          $fatal(1,"retirement %0d pc=%h expected=%h",n,dut.memwb_pc,expected_pc[n]);
        n=n+1;
      end
    end
    #1;
    if(dut.instr_count !== 8) $fatal(1,"retirement count=%0d",dut.instr_count);
    if(dut.stall_count !== 1) $fatal(1,"load-use stalls=%0d",dut.stall_count);
    if(dut.dmem[0] !== 7 || dut.u_rf.regs[2] !== 0)
      $fatal(1,"store or flush failure");
    // WB data is registered on this edge and written on the next negedge.
    @(negedge clk); #1;
    if(dut.u_rf.regs[5] !== 14) $fatal(1,"load-use result");
    rst=1;
    repeat(2) @(negedge clk);
    #1;
    if(dut.instr_count !== 0 || dut.memwb_valid !== 0)
      $fatal(1,"reset did not clear retirement state");
    $display("PASS: retirement order, NOP/x0, store, branch, JAL, flush, load-use, reset");
    $finish;
  end
  initial begin #5000; $fatal(1,"retirement timeout"); end
endmodule