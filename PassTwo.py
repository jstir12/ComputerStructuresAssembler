import re
class PassTwo:
    def __init__(self, control_sections, op_table,block_info):
        """self.symbol_table = symbol_table
        self.intermediate_code = intermediate_code
        self.machine_code = []
        self.modifications = []  # To track modification records
        self.op_table = op_table
        self.basereg = basereg
        self.program_name = program_name
        self.functions = []
        self.start_address = int(start_address, 16)
        self.program_length = int(program_length, 16)
        self.literal_table = literal_table
        self.modification_records = modification_records"""
        self.control_sections = control_sections
        self.op_table = op_table
        self.current_section = None
        self.basereg = None
        self.block_info = block_info
        #self.block_table = block_table


#Find the value for current program block. Take starting address and add it to label adrresss


    def generate_machine_code(self):
        # Set Base register
        
        for control_section in self.control_sections.values():
            self.current_section = control_section
            intermediate_code = control_section.get_intermediate_code()
            symbol_table = control_section.get_symbol_table()
        
            if "BASE" in symbol_table.symbols:
                self.basereg = symbol_table.get_address("BASE")
                
            if self.basereg and not self.basereg.isdigit():
                self.basereg = symbol_table.get_address(self.basereg[1:])
                        
            for line in intermediate_code:
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
                    control_section.add_function(operand)
                    
                if label in control_section.get_functions():
                    is_function = True
                    
                if mnemonic == "RSUB" or mnemonic == "WORD" or mnemonic == "BYTE" or label == '*':
                    if mnemonic == 'RSUB':
                        object_code = "4F0000"
                    elif mnemonic == 'WORD':
                        for row in control_section.get_expressions():
                            if operand in row:
                                operand = row[0]
                                label = row[1]
                                operand = self.calculate_EQU(operand, pc, label)
                        object_code = f"{int(operand):06X}"
                    elif mnemonic == 'BYTE':
                        object_code = self.get_X_C(operand)
                    elif label == '*':
                        object_code = self.get_X_C(mnemonic[1:])
                        control_section.update_machine_code([True, None,f"{int(line[0],16):04X}", object_code])
                        continue
                        
                    control_section.update_machine_code([False, None,f"{int(line[0],16):04X}", object_code])
                    continue
                
                # Check if the mnemonic represents a format 4 instruction
                is_format_4 = mnemonic.startswith('+')
                if is_format_4:
                    opcode = self.op_table.getOpcodeValue(mnemonic[1:])
                    format = 4
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
                            new_object_code = [False, label, f"{int(line[0],16):04X}", object_code]
                        else:
                            new_object_code = [False, None, f"{int(line[0],16):04X}", object_code]
                        control_section.update_machine_code(new_object_code)
                        continue
                except ValueError as e:
                    print(f"Warning: {e} at PC {pc:04X}")
        return

    def write_object_code_file(self):
        amount = 0
        for control_section in self.control_sections.values():
            amount += 1
            program_name = control_section.get_name()
            file_name = f'Object_Code_Files/{program_name}.txt'
            modification_records = control_section.get_modification_records()
            external_refs = control_section.get_external_refs()
            external_defs = control_section.get_external_defs()
            machine_code = control_section.get_machine_code()
            start_address = control_section.get_start_address()
            program_length = control_section.get_length()
            
            with open(file_name, 'w') as obj_file:
                # Write the Header Record
                header_record = f"H^{program_name[:6]:<6}^{start_address:06X}^{program_length:06X}\n"
                obj_file.write(header_record)
                functions = 0
                
                #Write external defs and refs if they exist
                if external_defs:
                    line = "D"
                    for key, value in external_defs.items():
                        line += f"^{key[:6]:<6}^{int(value,16):06X}"
                    line += "\n"
                    obj_file.write(line)
                if external_refs:
                    line = "R"
                    for item in external_refs:
                        line += f"^{item[:6]:<6}"
                    line += "\n"
                    obj_file.write(line)
                
                # Write Text Records
                text_record = ""  # Stores object code for the current text record
                record_start_address = None  # Start address of the current text record
                record_length = 0  # Length of the current text record in bytes

                for literal_flag, function, pc, code in machine_code:
                    if record_start_address is None:
                        record_start_address = pc

                    # Check if adding this code would exceed 30 bytes
                    code_length = len(code) // 2  # Each 2 hex digits = 1 byte
                    if record_length + code_length > 30 or function is not None and functions == 0 or literal_flag:
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
                for address, length, symbol in modification_records:
                    if not symbol:
                        mod_record = f"M^{address}^{length}\n" 
                    else:
                        mod_record = f"M^{address}^{length}^{symbol}\n"
                    obj_file.write(mod_record) 
                
                
                # Write the End Record
                if amount >1:
                    end_record = f"E\n"       
                else:
                    end_record = f"E^{start_address:06X}\n"
                obj_file.write(end_record)


    def calculate_object_code(self, opcode, format, operand, pc):
        object_code = ""
        external_refs = self.current_section.get_external_refs()
        
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
            x, operand = (1, operand[:-2]) if ',X' in operand else (0, operand)

            # Determine the address
            if operand in external_refs:
                disp = 0
                b, p = 0, 0
                
            else:
                label_address = self.get_label_address(operand, n, i)
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

    def get_label_address(self, operand, n, i):
        """Retrieve the address of a label, handling different addressing modes."""
        
        symbol_table = self.current_section.get_symbol_table()
        literal_table = self.current_section.get_literal_table()

        block_number = 0 #Default block number

        # Direct (simple) addressing
        if n == 1 and i == 1:
            if operand.startswith('='):
                label_address = literal_table[operand]
            else:
                #label_address = symbol_table.get_address(operand)
                label_address, block_number = symbol_table.get_address_and_block(operand)

        # Immediate or indirect addressing
        elif i == 1 and n == 0 and operand[1:].isdigit():
            label_address = f"{int(operand[1:]):04X}"
        elif i == 0 and n == 1:
            label_address = symbol_table.get_address(operand[1:])
        else:
            label_address = symbol_table.get_address(operand[1:])
        
        if label_address is None:
            raise ValueError(f"Label '{operand}' not found in symbol table.")

        block_start_address = int(self.block_info[block_number][1], 16) #fetching the starting addres of the bloock whre the symbol is defined

        absolute_address = block_start_address + int(label_address, 16)
        return absolute_address
    #label_address

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
        return object_code
    
    def calculate_EQU(self, operands, location_counter, label):
        # Split the expression into tokens (operands and operators)
        tokens = re.findall(r"[A-Za-z0-9]+|[+\-*/()]", operands)
        operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x // y  # Integer division for addresses
        }

        external_refs = self.current_section.get_external_refs()
        stack = []  # Use a stack for evaluating expressions
        operator_stack = []  # Stack for operators to handle precedence

        def apply_operator():
            # Apply the operator on the stack
            operator = operator_stack.pop()
            right_operand = stack.pop()
            left_operand = stack.pop()

            if not left_operand[0] or not right_operand[0]:
                # One or both operands are unresolved (external references)
                stack.append([0, right_operand[1]])  # Placeholder value
                self.add_modification_record(operator, left_operand[1], right_operand[1], location_counter, label)
            else:
                # Both operands are resolved values
                result = operations[operator](left_operand[0], right_operand[0])
                stack.append([result, right_operand[1]])
                # Always add a modification record for resolved addresses if relocation is needed
                if operator == '+':
                    self.add_modification_record(operator, left_operand[1], right_operand[1], location_counter, label)

        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '(': 0}

        for token in tokens:
            if token in operations:
                # Handle operator precedence
                while operator_stack and precedence[operator_stack[-1]] >= precedence[token]:
                    apply_operator()
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    apply_operator()
                operator_stack.pop()  # Remove the '('
            else:
                # It's an operand; determine if it's external, local, or undefined
                if token in external_refs:
                    # It's an external reference; leave it as a string
                    stack.append([None, token])
                elif token in self.current_section.get_symbol_table().symbols:
                    # It's a local symbol; resolve it to a numeric value
                    resolved_value = int(self.current_section.get_symbol_address(token), 16)
                    stack.append([resolved_value, token])
                else:
                    # It's an undefined symbol; handle the error
                    raise ValueError(f"Undefined symbol: {token}")

        while operator_stack:
            apply_operator()

        # Final result should be the only item left in the stack
        result = stack.pop()
        return f'{result[0]:04X}'
    
    def add_modification_record(self, operator, left_operand, right_operand, location_counter, label):
        if isinstance(left_operand, str):  # External reference
            self.current_section.add_modification_record([
                f'{location_counter:06X}', f'{len(label):02X}', '+' + left_operand
            ])
        else:
            # Add record for resolved left operand
            self.current_section.add_modification_record([
                f'{location_counter:06X}', f'{len(label):02X}', f'+{left_operand:04X}'
            ])

        if isinstance(right_operand, str):  # External reference
            self.current_section.add_modification_record([
                f'{location_counter:06X}', f'{len(label):02X}', f'{operator}{right_operand}'
            ])
        else:
            # Add record for resolved right operand
            self.current_section.add_modification_record([
                f'{location_counter:06X}', f'{len(label):02X}', f'{operator}{right_operand:04X}'
            ])    
    