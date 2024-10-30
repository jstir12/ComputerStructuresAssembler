class PassTwo:
    def __init__(self, symbol_table, intermediate_code, op_table, basereg):
        self.symbol_table = symbol_table
        self.intermediate_code = intermediate_code
        self.machine_code = []
        self.op_table = op_table
        self.basereg = basereg
        
    def generate_machine_code(self):
        for line in self.intermediate_code:
            # Assume the first element in line is the location counter (PC)
            pc = line[0]  # Set the current PC for this instruction

            # Parse line for label, mnemonic, and operand as before
            label, mnemonic, operand = (None, None, None)
            if len(line) == 4:
                _, label, mnemonic, operand = line  # Ignore the loc_counter here
            elif len(line) == 3:
                _, mnemonic, operand = line
            else:
                mnemonic = line[1]
                
            is_format_4 = mnemonic.startswith('+')
            if is_format_4:
                opcode = self.op_table.getOpcodeValue(mnemonic[1:])
                format = 4
            else:
                if mnemonic in self.op_table.optable:
                    opcode, format = self.op_table.getOpcode(mnemonic)
                else:
                    raise ValueError(f"Error: Mnemonic '{mnemonic}' not found in opcode table.")

            # Pass `pc` to calculate object code
            # Add format to PC for the next instruction
            pc = int(pc, 16) + int(format)  # Update PC for next instruction
            object_code = self.calculate_object_code(opcode, format, operand, pc)
            if object_code:
                self.machine_code.append(object_code)

        return self.machine_code


    def calculate_object_code(self, opcode, format, operand, pc):
        object_code = ""
        
        if format == 1:
            object_code = f"{opcode:02X}"
        
        elif format == 2:
            reg1, reg2 = operand.split(",")
            reg1_code = self.get_register_code(reg1)
            reg2_code = self.get_register_code(reg2)
            object_code = f"{opcode:02X}{reg1_code}{reg2_code}" 
        
        elif format in [3, 4]:
            # Set up n, i, x, e flags based on addressing mode and format
            e = 1 if format == 4 else 0
            n, i = (1, 0) if operand.startswith('@') else (0, 1) if operand.startswith('#') else (1, 1)
            x = 1 if ',X' in operand else 0

            # Determine the address
            if operand.startswith('='):
                literal = operand[1:] 
                address = self.symbol_table.get_address(literal)
            else:
                label_address = self.get_label_address(operand, n, i, x)
                
            disp, b, p = self.calculate_disp(label_address, format, self.basereg, pc)
            
            opcode_ni = (opcode | (n << 1) | i) & 0xFF  # Combine opcode with n and i flags
            xbpe = (x << 3) | (b << 2) | (p << 1) | e  # Combine x, b, p, and e flags
            
            # Combine into the final object code
            if format == 3:
                object_code = f"{opcode_ni:02X}{xbpe:01X}{disp:03X}"
            elif format == 4:
                object_code = f"{opcode_ni:02X}{xbpe:01X}{disp:05X}"
        
        return object_code

    def calculate_disp(self, label_address, format, base_register, pc):
        b, p = 0, 0

        if format == 4:
            return f"{int(label_address, 16):05X}", b, p

        disp = int(label_address, 16) - pc
        
        if -2048 <= disp <= 2047:
            disp_hex = disp & 0xFFF
            p = 1
            return f"{disp_hex:03X}", b, p
        else:
            disp = int(label_address, 16) - int(base_register, 16)
            if 0 <= disp < 4096:
                disp_hex = disp & 0xFFF
                b = 1
                return f"{disp_hex:03X}", b, p
            else:
                raise ValueError(f"Displacement out of range for label address {label_address}")

    def get_label_address(self, operand, n, i, x):
        if n == 1 and i == 1:  # Direct or simple addressing
            label_address = self.symbol_table.get_address(operand if x == 0 else operand[:-2])
        else:  # Immediate or indirect addressing
            label_address = self.symbol_table.get_address(operand[1:])
        return label_address

    def get_register_code(self, register):
        register_codes = {"A": 0, "X": 1, "L": 2, "B": 3, "S": 4, "T": 5, "F": 6}
        return f"{register_codes.get(register, 0):X}"
