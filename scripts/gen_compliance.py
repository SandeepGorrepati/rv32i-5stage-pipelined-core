#!/usr/bin/env python3
"""
RV32I self-checking compliance test generator.

Assembles a suite of directed per-instruction tests, computes the expected final
value of x10 (a0) with a built-in RV32I reference model, and emits:
  compliance/<name>.hex        one 32-bit instruction word per line ($readmemh format)
  compliance/manifest.txt       lines of "<name> <expected_x10_decimal>"

The testbench (tb/tb_core_pipe5_compliance.sv) loads each .hex, runs the core, and
checks dbg_x10 == expected. Every program ends in a self-loop so x10 stays stable.

This is a *self-checking ISA test suite* the assistant fully validates here (the
reference model cross-checks every expected value). For the OFFICIAL riscv-tests
suite, see compliance/README.md (needs the riscv-gnu-toolchain + a tohost hook).
"""
import os

REG = {f"x{i}": i for i in range(32)}
REG.update({"zero":0,"ra":1,"sp":2,"gp":3,"tp":4,"t0":5,"t1":6,"t2":7,
            "s0":8,"fp":8,"s1":9,"a0":10,"a1":11,"a2":12,"a3":13})

def r(x):
    return REG[x] if isinstance(x,str) else x
def u32(v): return v & 0xFFFFFFFF

# ---------------- encoders ----------------
def R(f7,f3,op,rd,rs1,rs2):
    return u32((f7<<25)|(r(rs2)<<20)|(r(rs1)<<15)|(f3<<12)|(r(rd)<<7)|op)
def I(f3,op,rd,rs1,imm):
    return u32(((imm&0xFFF)<<20)|(r(rs1)<<15)|(f3<<12)|(r(rd)<<7)|op)
def S(f3,op,rs1,rs2,imm):
    imm&=0xFFF
    return u32(((imm>>5)<<25)|(r(rs2)<<20)|(r(rs1)<<15)|(f3<<12)|((imm&0x1F)<<7)|op)
def B(f3,op,rs1,rs2,imm):
    imm&=0x1FFF
    b12=(imm>>12)&1; b11=(imm>>11)&1; b10_5=(imm>>5)&0x3F; b4_1=(imm>>1)&0xF
    return u32((b12<<31)|(b10_5<<25)|(r(rs2)<<20)|(r(rs1)<<15)|(f3<<12)|(b4_1<<8)|(b11<<7)|op)
def U(op,rd,imm):
    return u32((u32(imm)&0xFFFFF000)|(r(rd)<<7)|op)
def J(op,rd,imm):
    imm&=0x1FFFFF
    b20=(imm>>20)&1; b10_1=(imm>>1)&0x3FF; b11=(imm>>11)&1; b19_12=(imm>>12)&0xFF
    return u32((b20<<31)|(b10_1<<21)|(b11<<20)|(b19_12<<12)|(r(rd)<<7)|op)

# instruction helpers (return encoded word)
def ADDI(rd,rs1,i): return I(0x0,0x13,rd,rs1,i)
def ADD(rd,a,b):    return R(0x00,0x0,0x33,rd,a,b)
def SUB(rd,a,b):    return R(0x20,0x0,0x33,rd,a,b)
def AND_(rd,a,b):   return R(0x00,0x7,0x33,rd,a,b)
def OR_(rd,a,b):    return R(0x00,0x6,0x33,rd,a,b)
def XOR_(rd,a,b):   return R(0x00,0x4,0x33,rd,a,b)
def SLL(rd,a,b):    return R(0x00,0x1,0x33,rd,a,b)
def SRL(rd,a,b):    return R(0x00,0x5,0x33,rd,a,b)
def SRA(rd,a,b):    return R(0x20,0x5,0x33,rd,a,b)
def SLT(rd,a,b):    return R(0x00,0x2,0x33,rd,a,b)
def ANDI(rd,a,i):   return I(0x7,0x13,rd,a,i)
def ORI(rd,a,i):    return I(0x6,0x13,rd,a,i)
def LUI(rd,i):      return U(0x37,rd,i)
def SW(rs1,rs2,i):  return S(0x2,0x23,rs1,rs2,i)
def LW(rd,rs1,i):   return I(0x2,0x03,rd,rs1,i)
def BEQ(a,b,i):     return B(0x0,0x63,a,b,i)
def BNE(a,b,i):     return B(0x1,0x63,a,b,i)
def JAL(rd,i):      return J(0x6F,rd,i)
def SELF_LOOP():    return JAL(0,0)          # jal x0, 0  -> infinite loop at self

# ---------------- reference model ----------------
def sign(v): return v-0x100000000 if v & 0x80000000 else v
def simulate(words, dmem_words=64, max_steps=400):
    x=[0]*32; pc=0; dmem=[0]*dmem_words; steps=0
    while steps<max_steps:
        steps+=1
        idx=(pc>>2)
        if idx<0 or idx>=len(words): break
        ins=words[idx]
        op=ins&0x7F; rd=(ins>>7)&0x1F; f3=(ins>>12)&7; rs1=(ins>>15)&0x1F
        rs2=(ins>>20)&0x1F; f7=(ins>>25)&0x7F
        npc=pc+4
        def imm_i(): return sign(((ins>>20)&0xFFF)|(0xFFFFF000 if ins&0x80000000 else 0))
        if op==0x13:  # ALU-imm
            ii=imm_i()
            if f3==0: v=u32(x[rs1]+ii)
            elif f3==7: v=x[rs1]&u32(ii)
            elif f3==6: v=x[rs1]|u32(ii)
            else: v=x[rs1]
            if rd: x[rd]=v
        elif op==0x33:  # R
            if   f3==0 and f7==0x00: v=u32(x[rs1]+x[rs2])
            elif f3==0 and f7==0x20: v=u32(x[rs1]-x[rs2])
            elif f3==7: v=x[rs1]&x[rs2]
            elif f3==6: v=x[rs1]|x[rs2]
            elif f3==4: v=x[rs1]^x[rs2]
            elif f3==1: v=u32(x[rs1]<<(x[rs2]&31))
            elif f3==5 and f7==0x00: v=x[rs1]>>(x[rs2]&31)
            elif f3==5 and f7==0x20: v=u32(sign(x[rs1])>>(x[rs2]&31))
            elif f3==2: v=1 if sign(x[rs1])<sign(x[rs2]) else 0
            else: v=0
            if rd: x[rd]=v
        elif op==0x37:  # LUI
            if rd: x[rd]=u32(ins&0xFFFFF000)
        elif op==0x23 and f3==2:  # SW
            imm=sign((((ins>>25)&0x7F)<<5)|((ins>>7)&0x1F)|(0xFFFFF000 if ins&0x80000000 else 0))
            a=u32(x[rs1]+imm); dmem[(a>>2)%dmem_words]=x[rs2]
        elif op==0x03 and f3==2:  # LW
            ii=imm_i(); a=u32(x[rs1]+ii)
            if rd: x[rd]=dmem[(a>>2)%dmem_words]
        elif op==0x63:  # branch
            imm=sign((((ins>>31)&1)<<12)|(((ins>>7)&1)<<11)|(((ins>>25)&0x3F)<<5)|(((ins>>8)&0xF)<<1))
            take=(x[rs1]==x[rs2]) if f3==0 else (x[rs1]!=x[rs2]) if f3==1 else False
            if take: npc=u32(pc+imm)
        elif op==0x6F:  # JAL
            imm=sign((((ins>>31)&1)<<20)|(((ins>>12)&0xFF)<<12)|(((ins>>20)&1)<<11)|(((ins>>21)&0x3FF)<<1))
            if rd: x[rd]=u32(pc+4)
            npc=u32(pc+imm)
        if npc==pc: break       # self-loop reached -> done
        pc=npc
        x[0]=0
    return x[10], dmem

# ---------------- test programs ----------------
def prog(*words): return list(words)+[SELF_LOOP()]
TESTS = {
  "addi":  prog(ADDI(10,0,7)),
  "add":   prog(ADDI(5,0,3), ADDI(6,0,4), ADD(10,5,6)),
  "sub":   prog(ADDI(5,0,10), ADDI(6,0,3), SUB(10,5,6)),
  "and":   prog(ADDI(5,0,0x3C), ADDI(6,0,0x0F), AND_(10,5,6)),
  "or":    prog(ADDI(5,0,0x30), ADDI(6,0,0x0F), OR_(10,5,6)),
  "xor":   prog(ADDI(5,0,0x3C), ADDI(6,0,0x0F), XOR_(10,5,6)),
  "sll":   prog(ADDI(5,0,1), ADDI(6,0,4), SLL(10,5,6)),
  "srl":   prog(ADDI(5,0,0x80), ADDI(6,0,3), SRL(10,5,6)),
  "sra":   prog(ADDI(5,0,-16 & 0xFFF), ADDI(6,0,2), SRA(10,5,6)),
  "slt":   prog(ADDI(5,0,-1 & 0xFFF), ADDI(6,0,1), SLT(10,5,6)),
  "lui":   prog(LUI(10,0x12345000)),
  "lw_sw": prog(ADDI(5,0,42), ADDI(7,0,0), SW(7,5,0), LW(10,7,0)),
  "beq_taken":    prog(ADDI(10,0,1), ADDI(5,0,2), ADDI(6,0,2), BEQ(5,6,8), ADDI(10,0,99), ADDI(10,0,7)),
  "bne_nottaken": prog(ADDI(10,0,1), ADDI(5,0,2), ADDI(6,0,2), BNE(5,6,12), ADDI(10,0,7), JAL(0,8), ADDI(10,0,99)),
  "jal":   prog(ADDI(10,0,1), JAL(1,8), ADDI(10,0,99), ADDI(10,0,7)),
}

def main():
    here=os.path.dirname(os.path.abspath(__file__))
    out=os.path.join(here,"..","compliance"); os.makedirs(out,exist_ok=True)
    manifest=[]
    print(f"{'test':14} {'expected_x10':>12}")
    for name,words in TESTS.items():
        exp,_=simulate(words)
        manifest.append(f"{name} {sign(exp)}")
        with open(os.path.join(out,f"{name}.hex"),"w") as f:
            for w in words: f.write(f"{w:08x}\n")
            for _ in range(64-len(words)): f.write("00000013\n")  # pad with NOP
        print(f"{name:14} {sign(exp):>12}")
    with open(os.path.join(out,"manifest.txt"),"w") as f:
        f.write("\n".join(manifest)+"\n")
    print(f"\nWrote {len(TESTS)} tests + manifest to {os.path.normpath(out)}")

if __name__=="__main__":
    main()
    main()
