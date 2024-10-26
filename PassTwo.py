class PassTwo:
    def __init__(self, symbol_table, intermediate_code, op_table):
        self.symbol_table = symbol_table
        self.intermediate_code = intermediate_code
        self.machine_code = []
        self.op_table = op_table
    
    def generate_machine_code(self):
        for line in self.intermediate_code:
            if len(line) == 3:
                label, mnemonic, operand = line
            else:
                mnemonic, operand =line
            
            #Figure out opcode of mnemonic and format
            if mnemonic in self.op_table.opcodes:
                opcode, format  = self.op_table.getOpcodes(mnemonic)
            
            # Figure out if mneumonic can be 4
            if format == "3":
                if operand[0] == '+':
                    format = 4