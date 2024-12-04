class PassTwo:
    def __init__(self, symbol_table, intermediate_code, op_table, basereg, program_name, start_address, program_length):
        self.symbol_table = symbol_table
        self.intermediate_code = intermediate_code
        self.machine_code = []
        self.modifications = []  # To track modification records
        self.op_table = op_table
        self.basereg = basereg
        self.program_name = program_name
        self.functions = []
        self.start_address = int(start_address, 16)
        self.program_length = int(program_length, 16)

    def generate_machine_code(self):
        # Set Base register
        if "BASE" in self.symbol_table.symbols:
            self.basereg = self.symbol_table.symbols["BASE"]
            if not self.basereg.isdigit():
                self.basereg = self.symbol_table.get_address(self.basereg[1:])
                
        for line in self.intermediate_code:
            # Assume the first element in line is the location counter (PC)
            pc = int(line[0], 16)
            is_function = False
            # Parse line for label, mnemonic, and operand
            label, mnemonic, operand = (None, None, None)
            if len(line) == 4:
                _, label, mnemonic, operand = line
            elif len(line) == 3:
                _, mnemonic, operand = line
            else:
                mnemonic = line[1]
            
            # Need to keep track of subroutines
            if mnemonic == 'JSUB' or mnemonic[1:] == "JSUB":
                self.functions.append(operand) 
            if label in self.functions:
                is_function = True
            if mnemonic == "RSUB" or mnemonic == "WORD" or mnemonic == "BYTE" or label == '*':
                if mnemonic == 'RSUB':
                    object_code = "4F0000"
                elif mnemonic == 'WORD':
                    object_code = f"{int(operand):06X}"
                elif mnemonic == 'BYTE':
                    object_code = self.get_X_C(operand)
                elif label == '*':
                    object_code = self.get_X_C(mnemonic[1:])
                    
                self.machine_code.append([None,f"{int(line[0],16):04X}", object_code])
                continue
            
            # Check if the mnemonic represents a format 4 instruction
            is_format_4 = mnemonic.startswith('+')
            if is_format_4:
                opcode = self.op_table.getOpcodeValue(mnemonic[1:])
                format = 4
                if not operand.startswith('#'):
                    self.modifications.append([f"{pc+1:06X}", f"{5:02X}"])
            else:
                # Get opcode and format if mnemonic is in the opcode table
                if mnemonic in self.op_table.optable:
                    opcode, format = self.op_table.getOpcode(mnemonic)
                    format = int(format)
                    
                else:
                    raise ValueError(f"Error: Mnemonic '{mnemonic}' not found in opcode table.")

            # Generate the object code for this line
            try:
                # Update the program counter for the next instruction
                pc += format
                object_code = self.calculate_object_code(opcode, format, operand, pc)
                if object_code:
                    if is_function:
                        new_object_code = [label, f"{int(line[0],16):04X}", object_code]
                    else:
                        new_object_code = [None, f"{int(line[0],16):04X}", object_code]
                    self.machine_code.append(new_object_code)
                    continue
            except ValueError as e:
                print(f"Warning: {e} at PC {pc:04X}")
        return self.machine_code

    def write_object_code_file(self, filename):
        with open(filename, 'w') as obj_file:
            # Write the Header Record
            header_record = f"H^{self.program_name[:6]:<6}^{self.start_address:06X}^{self.program_length:06X}\n"
            obj_file.write(header_record)
            functions = 0
            # Write Text Records
            text_record = ""  # Stores object code for the current text record
            record_start_address = None  # Start address of the current text record
            record_length = 0  # Length of the current text record in bytes

            for function, pc, code in self.machine_code:
                if record_start_address is None:
                    record_start_address = pc

                # Check if adding this code would exceed 30 bytes
                code_length = len(code) // 2  # Each 2 hex digits = 1 byte
                if record_length + code_length > 30 or function is not None and functions == 0:
                    # Write the current text record to the file
                    if function is not None:
                        functions += 1
                    record_start_address = int(record_start_address,16)
                    text_record_line = f"T^{record_start_address:06X}^{record_length:02X}^{text_record}\n"
                    obj_file.write(text_record_line)

                    # Reset for the next text record
                    text_record = ""
                    record_start_address = pc
                    record_length = 0
                # Add the object code to the current text record
                text_record += code
                record_length += code_length

            # Write the final text record, if any
            if text_record:
                record_start_address = int(record_start_address,16)
                text_record_line = f"T^{record_start_address:06X}^{record_length:02X}^{text_record}\n"
                obj_file.write(text_record_line)

            for address, value in self.modifications:
                mod_record = f"M^{address}^{value}\n"
                obj_file.write(mod_record)
            # Write the End Record
            end_record = f"E^{self.start_address:06X}\n"
            obj_file.write(end_record)


    def calculate_object_code(self, opcode, format, operand, pc):
        object_code = ""

        if format == 1:
            # Format 1: opcode only
            object_code = f"{int(opcode,16):02X}"

        elif format == 2:
            # Format 2: opcode + register codes
            if ',' not in operand:
                reg1_code = self.get_register_code(operand)
                reg2_code = "0"
            else:
                reg1, reg2 = operand.split(",")
                reg1_code = self.get_register_code(reg1)
                reg2_code = self.get_register_code(reg2)
            reg1_code, reg2_code, opcode = int(reg1_code), int(reg2_code), int(opcode, 16)
            object_code = f"{opcode:02X}{reg1_code}{reg2_code}"
        
        elif format in [3, 4]:
            # Set up n, i, x, e flags
            e = 1 if format == 4 else 0
            n, i = self.determine_addressing_flags(operand)
            x = 1 if ',X' in operand else 0

            # Determine the address
            label_address = self.get_label_address(operand, n, i, x)
            if i == 0 and n == 0 or i == 0 and n == 1 or i == 1 and n == 1 or i == 1 and not operand[1:].isdigit():
                disp, b, p = self.calculate_disp(label_address, format, self.basereg, pc)
                disp = int(disp)
            else:
                disp = int(label_address, 16)
                b, p = 0, 0

            # Combine opcode and flags into final object code
            opcode = int(opcode, 16)
            opcode_ni = (opcode | (n << 1) | i) & 0xFF
            xbpe = (x << 3) | (b << 2) | (p << 1) | e
            if format == 3:
                object_code = f"{opcode_ni:02X}{xbpe:01X}{disp:03X}"
            elif format == 4:
                object_code = f"{opcode_ni:02X}{xbpe:01X}{disp:05X}"
        
        return object_code

    def calculate_disp(self, label_address, format, base_register, pc):
        """Calculate displacement and addressing mode flags."""
        b, p = 0, 0

        if format == 4:
            return f"{int(label_address, 16)}", b, p

        disp = int(label_address, 16) - pc

        # PC-relative addressing
        if -2048 <= disp <= 2047:
            p = 1
            return f"{disp & 0xFFF}", b, p
        # Base-relative addressing
        else:
            disp = int(label_address, 16) - int(base_register, 16)
            if 0 <= disp < 4096:
                b = 1
                return f"{disp & 0xFFF:03X}", b, p
            else:
                raise ValueError(f"Displacement out of range for label address {label_address}")

    def get_label_address(self, operand, n, i, x):
        """Retrieve the address of a label, handling different addressing modes."""
        # Direct (simple) addressing
        if n == 1 and i == 1:
            label_address = self.symbol_table.get_address(operand if x == 0 else operand[:-2])
        # Immediate or indirect addressing
        elif i == 1 and n == 0 and operand[1:].isdigit():
            label_address = f"{int(operand[1:]):04X}"
        elif i == 0 and n == 1:
            label_address = self.symbol_table.get_address(operand[1:] if x==0 else operand[1:-2])
        else:
            label_address = self.symbol_table.get_address(operand[1:] if x==0 else operand[1:-2])
        
        if label_address is None:
            raise ValueError(f"Label '{operand}' not found in symbol table.")
        return label_address

    def determine_addressing_flags(self, operand):
        """Determine addressing flags n and i based on operand format."""
        if operand.startswith('@'):  # Indirect addressing
            return 1, 0
        elif operand.startswith('#'):  # Immediate addressing
            return 0, 1
        else:  # Simple addressing
            return 1, 1

    def get_register_code(self, register):
        """Get the machine code for a register by its name."""
        register_codes = {"A": 0, "X": 1, "L": 2, "B": 3, "S": 4, "T": 5, "F": 6}
        if register not in register_codes:
            raise ValueError(f"Unknown register '{register}'")
        return f"{register_codes[register]:X}"
    
    # Calculate object code for X and C values
    def get_X_C(self, value):
        if value.startswith('X'):
            object_code = value[2:-1]
        elif value.startswith('C'):
            object_code = ''.join([f"{ord(char):02X}" for char in value[2:-1]])