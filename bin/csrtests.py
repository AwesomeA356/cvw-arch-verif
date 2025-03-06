#!/usr/bin/env python3
##################################
# csrtests.py
#
# David_Harris@hmc.edu 13 October 2024
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
#
# Emit tests of all 4096 CSRs for Zicsr functional coverage tests
##################################

import random
from random import randint
from random import seed
import os, sys
from os import environ

def csrwalk(pathname, regs):
    outfile = open(pathname, 'w')
    sys.stdout = outfile
    for reg in regs:
        if reg == "satp": # satp requires a special case to avoid accidentally turning on vmem
            continue
        print("\n// Testing walking zeros and ones for CSR "+reg)
        print("\tcsrr s0, "+reg+"\t# save CSR")
        print("\tli t1, -1           # all 1s")
        print("\tli t0, 1            # 1 in lsb")
        print("\t1: csrrc t6, "+reg+", t1    # clear all bits")
        print("\tcsrrs t6, "+reg+", t0    # set walking 1")
        print("\tslli t0, t0, 1      # walk the 1")
        print("\tbnez t0, 1b         # repeat until all bits are walked")
        print("\tli t0, 1            # 1 in lsb")
        print("1:  csrrs t6, "+reg+", t1    # set all bits")
        print("\tcsrrc t6, "+reg+", t0    # clear walking 1")
        print("\tslli t0, t0, 1      # walk the 1")
        print("\tbnez t0, 1b         # repeat until all bits are walked")
        print("\tcsrrw t6, "+reg+", s0    # restore CSR")
    outfile.close

def csrtests(pathname, skipCsrs):
    outfile = open(pathname, 'w')
    sys.stdout = outfile
    for i in range(4096):
        if (i in skipCsrs): 
            continue # skip custom CSRs
        reg1 = randint(1, 31)
        reg2 = randint(1, 31)
        reg3 = randint(1, 31)
        while (reg2 == reg1):
            reg2 = randint(1, 31)
        while (reg3 == reg1 or reg3 == reg2):
            reg3 = randint(1, 31)
        reg1 = str(reg1)
        reg2 = str(reg2)
        reg3 = str(reg3)
        ih = hex(i)

        print("\n// Testing CSR "+ih)
        print("\tcsrr x"+str(reg1)+", "+ ih + "\t// Read CSR")
        print("\tli x"+reg2+", -1")
        print("\tcsrrw x"+reg3+", "+ih+", x"+reg2+"\t// Write all 1s to CSR")
        print("\tcsrrw x"+reg3+", "+ih+", x0\t// Write all 0s to CSR")
        print("\tcsrrs x"+reg3+", "+ih+", x"+reg2+"\t// Set all CSR bits")
        print("\tcsrrc x"+reg3+", "+ih+", x"+reg2+"\t// Clear all CSR bits")
        print("\tcsrrw x"+reg3+", "+ih+", x"+reg1+"\t// Restore CSR")
    outfile.close

# setup
seed(0) # make tests reproducible

# generate repetitive assembly language tests

# writable registers to test with walking 1s and 0s
mregs = ["mstatus", "mcause", "misa", "medeleg", "mideleg", "mie", "mtvec", "mcounteren", "mscratch", "mepc", "mtval", "mip", "menvcfg", "mstatush", "mseccfg", "mseccfgh", "menvcfgh", "0x312"] # 0x312 is medelegeh; RV64 compiler isn't accepting the name
sregs = ["sstatus", "scause", "sie", "stvec", "scounteren", "senvcfg", "sscratch", "sepc", "stval", "sip", "0x120"] # 0x120 is scountinhibit, currently unsupported
uregs = ["fflags", "frm", "fcsr"]

uCsrSkip = list(range(0x800, 0x900)) + list(range(0xCC0, 0xD00))
sCsrSkip = list(range(0x5C0, 0x600)) + list(range(0x6C0, 0x700)) + \
           list(range(0x9C0, 0xA00)) + list(range(0xAC0, 0xB00)) + \
           list(range(0xDC0, 0xE00)) + list(range(0xEC0, 0xF00))
mCsrSkip = list(range(0x7A0, 0x7B0)) + list(range(0x7C0, 0x800)) + \
           list(range(0xBC0, 0xC00)) + list(range(0xFC0, 0x1000))

ARCH_VERIF = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))

pathname = f"{ARCH_VERIF}/tests/lockstep/priv/headers/ZicsrM-CSR-Tests.h"
csrtests(pathname, mCsrSkip + sCsrSkip + uCsrSkip)

pathname = f"{ARCH_VERIF}/tests/lockstep/priv/headers/ZicsrS-CSR-Tests.h"
csrtests(pathname, sCsrSkip + uCsrSkip + [0x180]) # 0x180 is satp, turns on virtual memory

pathname = f"{ARCH_VERIF}/tests/lockstep/priv/headers/ZicsrU-CSR-Tests.h"
csrtests(pathname, uCsrSkip)

pathname = f"{ARCH_VERIF}/tests/lockstep/priv/headers/ZicsrM-Walk.h"
csrwalk(pathname, mregs + sregs + uregs + ["satp"])

pathname = f"{ARCH_VERIF}/tests/lockstep/priv/headers/ZicsrS-Walk.h"
csrwalk(pathname, sregs + uregs);
