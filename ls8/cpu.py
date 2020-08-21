import sys

class CPU:
    def __init__(self):
        self.ram= [0] * 256
        self.reg = [0] * 8
        self.SP = 244
        self.PC = 0
        self.IR = 0 
        self.FL = {
            "E": 0,
            "G": 0, 
            "L": 0
        } 
        self.instructions = {
            1: self.handle_HLT,
            130: self.handle_LDI,
            71: self.handle_PRNT,
            162: self.handle_MUL,
            69: self.handle_PUSH,
            70: self.handle_POP,
            80: self.handle_CALL,
            17: self.handle_RET,
            160: self.handle_ADD,
            85: self.handle_JEQ,
            167: self.handle_CMP,
            86: self.handle_JNE,
            84: self.handle_JMP,
            168: self.handle_AND,
            170: self.handle_OR,
            171: self.handle_XOR,
            105: self.handle_NOT,
            172: self.handle_SHL,
            173: self.handle_SHR,
            164: self.handle_MOD,
            "HLT": self.handle_HLT
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
        elif op == "CMP":
            if reg_a == reg_b:
                self.FL["E"] = 1
                self.FL["L"] = 0
                self.FL["G"] = 0
            if reg_a < reg_b:
                self.FL["L"] = 1
                self.FL["G"] = 0
                self.FL["E"] = 0
            if reg_a > reg_b:
                self.FL["G"] = 1
                self.FL["L"] = 0
                self.FL["E"] = 0
        elif op == "SHL":
            self.reg[reg_a] = int(bin(self.reg[reg_a] << self.reg[reg_b]), 2)
        elif op == "SHR":
            self.reg[reg_a] = int(bin(self.reg[reg_a] >> self.reg[reg_b]), 2)
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] = int(bin(self.reg[reg_a] & self.reg[reg_b]), 2)
        elif op == "OR":
            self.reg[reg_a] = int(bin(self.reg[reg_a] | self.reg[reg_b]), 2)
        elif op == "XOR":
            self.reg[reg_a] = int(bin(self.reg[reg_a] ^ self.reg[reg_b]), 2)
        elif op == "NOT":
            self.reg[reg_a] = int(bin(~self.reg[reg_a]), 2)
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            #self.fl,
            #self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def run(self):
        while self.running:
            self.IR = self.ram[self.PC]
            self.instructions[self.IR]()

    def handle_LDI(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        operand_a = self.ram_read(self.PC + 1)
        operand_b = self.ram_read(self.PC + 2)
        self.reg[operand_a] = operand_b
        self.PC += my_bin_len + 1

    def handle_PRNT(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        index = self.ram_read(self.PC + 1)
        print(self.reg[index])
        self.PC += my_bin_len + 1

    def handle_MUL(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        self.alu("MUL", self.ram_read(self.PC + 1), self.ram_read(self.PC + 2))
        self.PC += my_bin_len + 1

    def handle_ADD(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        self.alu("ADD", self.ram_read(self.PC + 1), self.ram_read(self.PC + 2))
        self.PC += my_bin_len + 1

    def handle_HLT(self):
        self.running = False
    
    def handle_PUSH(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        self.SP -= 1
        value = self.reg[self.ram[self.PC + 1]]
        self.ram[self.SP] = value
        self.PC += my_bin_len + 1

    def handle_POP(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        value = self.ram[self.SP]
        self.SP += 1
        self.reg[self.ram[self.PC + 1]] = value
        self.PC += my_bin_len + 1
    
    def handle_CALL(self):
        next_index = self.PC + 2
        self.SP -= 1
        self.ram[self.SP] = next_index

        go_to_index = self.PC + 1
        self.PC = self.reg[self.ram[go_to_index]] 

    def handle_RET(self):
        self.PC = self.ram[self.SP]
        self.SP += 1

    def handle_JEQ(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        if self.FL["E"] == 1:
            jump_to_pc = self.ram[self.PC + 1]
            self.PC = self.reg[jump_to_pc]
        else:
            self.PC += my_bin_len + 1
    
    def handle_JNE(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        if self.FL["E"] == 0:
            jump_to_pc = self.ram[self.PC + 1]
            self.PC = self.reg[jump_to_pc]
        else:
            self.PC += my_bin_len + 1

    def handle_CMP(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        reg_a = self.ram[self.PC + 1]
        reg_b = self.ram[self.PC + 2]

        self.alu("CMP", self.reg[reg_a], self.reg[reg_b])
        self.PC += my_bin_len + 1

    def handle_JMP(self):
        reg_spot = self.ram[self.PC + 1]
        self.PC = self.reg[reg_spot]

    def handle_AND(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        reg_a = self.ram[self.PC + 1]
        reg_b = self.ram[self.PC + 2]
        self.alu("AND", reg_a, reg_b)
        self.PC += my_bin_len + 1
    
    def handle_OR(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        reg_a = self.ram[self.PC + 1]
        reg_b = self.ram[self.PC + 2]
        self.alu("OR", reg_a, reg_b)
        self.PC += my_bin_len + 1
    
    def handle_XOR(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        reg_a = self.ram[self.PC + 1]
        reg_b = self.ram[self.PC + 2]
        self.alu("XOR", reg_a, reg_b)
        self.PC += my_bin_len + 1
    
    def handle_NOT(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        reg_a = self.ram[self.PC + 1]
        self.alu("NOT", reg_a, None)
        self.PC += my_bin_len + 1

    def handle_SHL(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        reg_a = self.ram[self.PC + 1]
        reg_b = self.ram[self.PC + 2]
        self.alu("SHL", reg_a, reg_b)
        self.PC += my_bin_len + 1

    def handle_SHR(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        reg_a = self.ram[self.PC + 1]
        reg_b = self.ram[self.PC + 2]
        self.alu("SHR", reg_a, reg_b)
        self.PC += my_bin_len + 1

    def handle_MOD(self):
        my_bin_len = int(bin(self.IR >> 6), 2)
        reg_a = self.ram[self.PC + 1]
        reg_b = self.ram[self.PC + 2]
        if self.reg[reg_b] is 0:
            print("Error: The value in reg_b is zero")
            self.PC = "HLT"
        else:
            self.alu("MOD", reg_a, reg_b)
            self.PC += my_bin_len + 1

    def ram_read(self, MAR):
        return self.ram[MAR]
    
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR