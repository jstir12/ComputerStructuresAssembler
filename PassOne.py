import re

from OpTable import OpTable
from SymTable import SymTable
from ControlSection import ControlSection

class PassOne:
    def __init__(self, OpTable):
        self.op_table = OpTable
        self.controlSections = {}
        self.cs = None
        self.global_starting_address = 0
        self.macro_code = []
        self.is_macro = False
        self.line_count = 0
        self.program_blocks_maps = {"Default": 0}
        self.program_block_amount = 0

    def process_line(self, line): 
        #Next, process the line
        """Processes each line of the assembly code for Pass One."""
        #label, operation, operands = self.parse_line(line)
        label = None
        operation = None
        operands = None
        self.line_count += 1
        
        #Since the codes are stored in inside, arrays, we can use their length to determine labels, operations, and operands
        if self.is_macro:
            if line[0] == 'MEND':
                self.is_macro = False
                self.cs.update_macro(self.macro_code)
                self.macro_code = []
                return
            else:
                self.macro_code.append(line)
                return
        if len(line) == 3:
            label = line[0]
            operation = line[1] #The operation is the second element in the array
            operands = line[2]#The rest of the elements are operands
        elif len(line) == 2:
            operation = line[0]
            operands = line[1] #Split the operands by comma
        elif len(line) == 1:
            operation = line[0]
        #Look for a START operation
        if operation == 'START':
            # Create new control section
            self.global_starting_address = int(operands, 16)
            self.create_new_control_section(label)
            return
        elif operands and operands == 'CSECT':
            self.finalize_block_lengths()
            self.create_new_control_section(operation)
            return
        elif operation == 'EXTDEF':
            operands = operands.split(',')
            for symbol in operands:
                self.cs.set_external_defs(symbol)
            return
        elif operation == 'EXTREF':
            operands = operands.split(',')
            self.cs.set_external_refs(operands)
            return
        elif operation == 'MACRO':
            macro_name = label
            self.is_macro = True
            params = operands.split(',')
            self.cs.set_macro_name(macro_name)
            self.cs.set_params(params)
            self.cs.add_macro()
            return
        elif self.line_count == 1:
            self.global_starting_address = 0
            self.create_new_control_section('Default')   
        
        # Set location counter for the current block
        location_counter = self.cs.get_location_counter()
        
        #Check for USE directive. This indicates program switching
        if operation == 'USE':
            block_name = operands if operands else 'Default'
            
            block_info = self.cs.get_block_info()
            #Finalize the length of the current block
            if self.cs.get_program_block():
                current_block = self.cs.get_program_block() or 0
                if current_block in block_info:
                    block_info[current_block]['length'] = (self.cs.get_location_counter() - block_info[current_block]['address'])

            #Switch to the new block
            self.cs.set_program_block(block_name)

            #Initialize the block if it is not in the block inforomation
            if block_name not in block_info:
                block_number = self.program_blocks_maps.get(block_name,len(self.program_blocks_maps))
                self.program_blocks_maps[block_name] = block_number

                
            #Calculate the starting address of the new block
                if block_number == 0:
                    starting_address = self.global_starting_address
                elif block_info:
                    previous_block = list(block_info.values())[-1]
                    starting_address = previous_block['address'] + previous_block['length']
                else:
                    #Handling just in case the block is empty
                    starting_address = self.global_starting_address
                    

                #Initialize the block information
                self.cs.add_block_info(block_name, block_number, self.global_starting_address, 0)
            if self.cs.get_location_counter() == None:
                self.cs.update_location_counter(block_info[block_name]['address'])
            
            location_counter = self.cs.get_location_counter()
            
            return
            

        elif operation == 'LTORG' or operation == 'END': #Check for LTORG or END
            #Assign the literals to the location counter
            for key in self.cs.get_literal_keys():
                if self.cs.get_literal_value(key)[1] is None:
                    location_counter = self.cs.get_location_counter()
                    self.cs.add_literal(key, f'{location_counter:04X}', self.cs.get_program_block())
                    hex_location = f'{location_counter:04X}' #Convert location counter to hex string
                    self.cs.update_intermediate_code([self.cs.get_program_block(), hex_location, '*', key, ''])
                    self.cs.update_current_block(self.calculate_X_C(key[1:]))
            return
        if label:
            try:
                if operation == 'EQU':
                    if operands.startswith('*'):
                        self.cs.add_symbol(label, f'{location_counter:04X}', self.cs.get_program_block())
                    else:
                        value = self.calculate_EQU(operands, location_counter, label)
                        self.cs.add_symbol(label, value, "Default")
                        self.cs.add_immediate(label)
                        
                        
                    return
                elif any(op in operands for op in ['+', '-', '/', '*']):
                    self.cs.add_expression([operands, label])
                    self.cs.add_symbol(label, f'{location_counter:04X}', self.cs.get_program_block()) 
                else:     
                    self.cs.add_symbol(label, f'{location_counter:04X}', self.cs.get_program_block())
            except ValueError as e:
                print(f"Error: {e}")
                
        # Check for literals
        if operands:
            if operands.startswith('=C') or operands.startswith('=X'):
                self.cs.add_literal(operands, None, None)
            
        #Store the intermediate code for Pass Two
        hex_location = f'{location_counter:04X}' #Convert location counter to hex string
        if operation == "LDB":
            # Push Value of base register to symbol table
            self.cs.add_symbol("BASE",operands,self.cs.get_program_block())
        elif operation == 'RESW' or operation == 'RESB' or operation == 'RESD' or operation == 'RESQ' or operation == 'BASE' or operation == 'NOBASE':
            instruction_length = self.get_instruction_length(operation,operands)
            self.cs.update_current_block(instruction_length)
            return
        self.cs.update_intermediate_code([self.cs.get_program_block(), hex_location, label, operation, operands if operands else ''])

        #Updating location counter based on instruction length        
        instruction_length = self.get_instruction_length(operation, operands if operands else None)
        self.cs.update_current_block(instruction_length)
                
    def finalize_block_lengths(self):
        #Finalizes the lengths of the program blocks.
        block_info = self.cs.get_block_info()
        for key, values in block_info.items():
            values['length'] = self.cs.get_location_counter_with_block(key) - values['address']
        
        # Initialize the starting address
        current_address = self.global_starting_address

        # Iterate through the dictionary in sorted order of block_number
        for block_name, block_data in sorted(block_info.items(), key=lambda x: x[1]['block_number']):
            # Set the starting address for the current block
            block_data['address'] = current_address
            # Update the current_address for the next block
            current_address += block_data['length']

        return

    def get_instruction_length(self, operation,operands):
        """Determine the length of an instruction based on its operation."""
        #For now, just check if the operation is RESW. Using basic.txt as a reference
        if operation == 'RESW':
            return 3 * int(operands) #Since each word is 3 bytes
        elif operation == 'RESB':
            return int(operands) #Each byte is 1 byte
        elif operation == 'RESD':
            return 4 * int(operands)
        elif operation == 'RESQ':
            return 8 * int(operands)
        elif operation == 'WORD':
            return 3
        elif operation == 'BYTE':
            return self.calculate_X_C(operands)
        elif operation == 'BASE':
            return 0
        elif operation == 'NOBASE':
            return 0
        elif operation == 'EQU':
            if operands.startswith('*'):
                return 0
        
        #Referring to the opTable class for the format type
        if operation.startswith('+'):
            opcode_format = 4
            if not operands.startswith('#'):
                if ',X' in operands:
                    operands = operands[:-2]
                if operands in self.cs.get_external_refs():    
                    self.cs.add_modification_record([f'{self.cs.get_location_counter()+1:06X}',f'{5:02X}', f'+{operands}'])
                else:
                    self.cs.add_modification_record([f'{self.cs.get_location_counter()+1:06X}',f'{5:02X}', None])
        else:
            opcode_format = self.op_table.getFormat(operation)
            
        if opcode_format: #If the format is found
            return int(opcode_format)
        else:
            return 3 #Default length for instructions
    
    def pre_process(self, file_path):
        #Will read and pre-process the input file to remove comments and white-spaces
        try:
            with open(file_path, 'r') as file:
                lines = []
                for line in file:
                    line = line.split('.')[0].strip() #Remove comments
                    line = line.replace('\t',' ') #Replace tabs with spaces
                    if line != '':
                        code = line.split(' ')
                        lines.append(code) 
            return lines
        except FileNotFoundError:
            print('Error: File was not found.')
            return []
    
    def calculate_X_C(self, operands):
        #Calculate the length of the string
        if operands.startswith('X'):
            return (len(operands) - 3) // 2
        elif operands.startswith('C'):
            return len(operands) - 3
        return 0
    


    def calculate_EQU(self, operands, location_counter, label):
        # Split the expression into tokens (operands and operators)
        tokens = re.findall(r"[A-Za-z0-9]+|[+\-*/()]", operands)
        operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x // y  # Integer division for addresses
        }

        external_refs = self.cs.get_external_refs()
        stack = []  # Use a stack for evaluating expressions
        operator_stack = []  # Stack for operators to handle precedence
        #Anytime I come across the EQU satement, add it to an arry or dictionary of unresolved addresses that need to be fixed
        #At the end, I will calculate teh unresolved addresses and 
        #IF you're subtracting, you change the program block number of that symbol to the default program block number
        def apply_operator():
            # Apply the operator on the stack
            operator = operator_stack.pop()
            right_operand = stack.pop()
            left_operand = stack.pop()

            if left_operand[0] is None or right_operand[0] is None:
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
                elif token in self.cs.get_symbol_table().symbols:
                    # It's a local symbol; resolve it to a numeric value
                    resolved_value = int(self.cs.get_symbol_address(token), 16)
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
            self.cs.add_modification_record([
                f'{location_counter:06X}', f'{len(label):02X}', '+' + left_operand
            ])
        else:
            # Add record for resolved left operand
            self.cs.add_modification_record([
                f'{location_counter:06X}', f'{len(label):02X}', f'+{left_operand:04X}'
            ])

        if isinstance(right_operand, str):  # External reference
            self.cs.add_modification_record([
                f'{location_counter:06X}', f'{len(label):02X}', f'{operator}{right_operand}'
            ])
        else:
            # Add record for resolved right operand
            self.cs.add_modification_record([
                f'{location_counter:06X}', f'{len(label):02X}', f'{operator}{right_operand:04X}'
            ])


    
    def create_new_control_section(self, label):
        #Create a new control section
        self.cs = ControlSection(label)
        self.cs.set_start_address(self.global_starting_address)
        self.controlSections[label] = self.cs
        self.cs.set_program_block('Default')
        self.cs.update_location_counter(self.global_starting_address)
        self.cs.add_block_info('Default', 0, self.global_starting_address, 0)      
    
    def run(self, input_file):
        #Will process the input file and return the intermediate code for Pass Two
        #First, pre-process the file
        lines = self.pre_process(input_file)
        for line in lines:
            if self.cs :
                macros = self.cs.get_macros()
                line_length = len(line)
                args = [] 
                if line[0] in macros or line_length >= 2 and line[1] in macros:
                    if line_length == 3:
                        macro_name = line[1]
                        args = line[2].split(',')
                    else:
                        macro_name = line[0]
                        args = line[1].split(',')
                    macro = self.cs.get_macro(macro_name)    
                    macro_line_number = 0
                    # Need to expand macro and only process those lines
                    code = macro.expand_macros(macro_name, args)
                    if line_length == 3:
                        code[0].insert(0, line[0])
                    for line in code:
                        self.process_line(line)
                    continue    
            self.process_line(line)
            #IF operator is = minus, set the program  block number to default program block number
        for cs in self.controlSections.values():
            cs.set_length(cs.get_location_counter() - cs.get_start_address())
            block_info = cs.get_block_info()
            self.finalize_block_lengths()
            for block, info in block_info.items():
                info['address'] = hex(info['address']).upper()[2:].zfill(4)  # Convert to hex and format
                info['length'] = hex(info['length']).upper()[2:].zfill(4)    # Convert to hex and format
    
        return self.controlSections