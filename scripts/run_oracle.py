"""Generate dependency-heavy RV32I-subset programs with a Python oracle."""
from pathlib import Path
import random
import subprocess

ROOT=Path(__file__).resolve().parents[1]
MASK=(1<<32)-1
def signed(v): return v if v<1<<31 else v-(1<<32)
def addi(rd,rs,imm): return ((imm&4095)<<20)|(rs<<15)|(rd<<7)|0x13
def branch(f3):
    # rs1=x1, rs2=x2, offset=8
    return (2<<20)|(1<<15)|(f3<<12)|(8<<7)|0x63

def execute(program):
    regs=[0]*32; pc=0; count=0
    while pc < (len(program)-1)*4:
        ins=program[pc//4]; op=ins&127; rd=(ins>>7)&31; f3=(ins>>12)&7
        a=regs[(ins>>15)&31]; b=regs[(ins>>20)&31]; nxt=pc+4
        if op==0x13:
            imm=ins>>20; imm=imm-4096 if imm&2048 else imm
            regs[rd]=(a+imm)&MASK
        elif op==0x33:
            sh=b&31
            if f3==0: val=a-b if ins>>30&1 else a+b
            elif f3==1: val=a<<sh
            elif f3==2: val=int(signed(a)<signed(b))
            elif f3==3: val=int(a<b)
            elif f3==4: val=a^b
            elif f3==5: val=signed(a)>>sh if ins>>30&1 else a>>sh
            elif f3==6: val=a|b
            else: val=a&b
            regs[rd]=val&MASK
        elif op==0x63:
            taken={0:a==b,1:a!=b,4:signed(a)<signed(b),5:signed(a)>=signed(b),6:a<b,7:a>=b}[f3]
            if taken: nxt=pc+8
        else: raise ValueError(hex(ins))
        regs[0]=0; pc=nxt; count+=1
        if count>1000: raise RuntimeError('oracle failed to terminate')
    return regs

def run_case(name,program):
    program=program+[0x0000006f] # JAL x0,0 is the terminal sentinel
    regs=execute(program)
    padded=program+[0x13]*(256-len(program))
    (ROOT/'build/oracle.hex').write_text(''.join(f'{i:08x}\n' for i in padded))
    (ROOT/'build/expected.hex').write_text(''.join(f'{i:08x}\n' for i in regs))
    result=subprocess.run(['vvp','build/oracle',f'+terminal={(len(program)-1)*4}'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=10)
    print(name,result.stdout.strip(),flush=True)
    if result.returncode or 'PASS: full register state' not in result.stdout:
        raise RuntimeError(f'{name} failed')

def main():
    (ROOT/'build').mkdir(exist_ok=True)
    src=[str(p.relative_to(ROOT)) for p in (ROOT/'rtl').glob('*.sv')]
    subprocess.run(['iverilog','-g2012','-s','tb_oracle','-o','build/oracle',*src,'tb/tb_oracle.sv'],cwd=ROOT,check=True)
    # All six conditions, both outcomes, including signed/unsigned disagreement.
    conditions=[(0,1,1),(1,1,2),(4,-1,1),(5,1,-1),(6,1,-1),(7,-1,1)]
    for f3,a,b in conditions:
        for taken in (True,False):
            if not taken: a,b=b,a if f3 not in (0,1) else b
            # Equality needs distinct/equal operands explicitly.
            aa,bb=((1,1) if (taken==(f3==0)) else (1,2)) if f3 in (0,1) else (a,b)
            run_case(f'branch_f3_{f3}_taken_{taken}',[addi(1,0,aa),addi(2,0,bb),branch(f3),addi(3,0,99),addi(4,0,7)])
    for seed in range(20):
        rng=random.Random(seed); program=[addi(i,0,rng.randrange(-2048,2048)) for i in range(1,16)]
        for _ in range(96):
            rd=rng.randrange(16); r1=rng.randrange(16); r2=rng.randrange(16)
            if rng.randrange(3)==0: ins=addi(rd,r1,rng.randrange(-2048,2048))
            else:
                f3=rng.randrange(8); f7=32 if f3 in (0,5) and rng.randrange(2) else 0
                ins=(f7<<25)|(r2<<20)|(r1<<15)|(f3<<12)|(rd<<7)|0x33
            program.append(ins)
        run_case(f'random_seed_{seed}',program)
    print('PASS: 12 branch programs + 20 dependency-heavy arithmetic programs')

if __name__=='__main__': main()
