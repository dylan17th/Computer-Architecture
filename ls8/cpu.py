"""CPU functionality."""

import sys

class CPU:
    def __init__(self):
        self.ram= [0] * 256
        self.reg = [0] * 8
        self.SP = 244
        self.pc = 0
        self.ir = 0 
        self.MDR = 0
        self.MAR = 0 
        self.instructions = {
            1: self.handle_HLT,
            130: self.handle_LDI,
            71: self.handle_PRNT,
            162: self.handle_MUL,
            69: self.handle_PUSH,
            70: self.handle_POP,
            80: self.handle_CALL,
            17: self.handle_RET,
            160: self.handle_ADD
        }
        self.running = True
 

    def load(self):
        address = 0
        program = []
        if len(sys.argv) is 2:
            filename = sys.argv[1]
            with open(f"examples/{filename}") as raw_program:
                for line in raw_program:
                    numbers = line.split("#")[0].strip()
                    if numbers is "":
                        continue
                    program.append(int(numbers, 2))
            for instruction in program:
                self.ram[address] = instruction
                address += 1
        else:
            print(f"Template: ls8.py filename")


    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def run(self):
        while self.running:
            self.ir = self.ram[self.pc]
            my_bin_len = int(bin(self.ir >> 6), 2)
            self.instructions[self.ir]()
            if self.ir == 17 or self.ir == 80:
                continue
            else:
                self.pc += my_bin_len + 1

    def handle_LDI(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b

    def handle_PRNT(self):
        index = self.ram_read(self.pc + 1)
        print(self.reg[index])

    def handle_MUL(self):
        self.alu("MUL", self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))

    def handle_ADD(self):
        self.alu("ADD", self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))

    def handle_HLT(self):
        self.running = False
    
    def handle_PUSH(self):
        # 1. Decrement the `SP`.
        self.SP -= 1
        # 2. Copy the value in the given register to the address pointed to by`SP`.
        value = self.reg[self.ram[self.pc + 1]]
        self.ram[self.SP] = value

    
    def handle_POP(self):
        value = self.ram[self.SP]
        self.SP += 1
        self.reg[self.ram[self.pc + 1]] = value
    
    def handle_CALL(self):
        next_index = self.pc + 2
        self.SP -= 1
        self.ram[self.SP] = next_index

        go_to_index = self.pc + 1
        self.pc = self.reg[self.ram[go_to_index]] 

    def handle_RET(self):
        self.pc = self.ram[self.SP]
        self.SP += 1

    def ram_read(self, MAR):
        return self.ram[MAR]
    
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR