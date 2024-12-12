import re

from OpTable import OpTable
from SymTable import SymTable
from ControlSection import ControlSection

class PassOne:
    def __init__(self, OpTable):
        #self.literal_table = LiteralTable()
        #self.symbol_table = SymTable
        self.op_table = OpTable
        #self.literal_table = {}
        #self.location_counters = {"Default": 0} #Store location counters for different blocks
        #self.current_block = "Default" #Current block: Default
        #self.location_counter = 0
        #self.starting_address = 0
        #self.program_length = 0
        #self.intermediate_code = [] #Store intermediate code for Pass Two
        #self.program_name = 'Basic' #Default program name
        #self.modification_records = [] #Store modification records for Pass Two
        self.controlSections = {}
        self.cs = None
        self.global_starting_address = 0
        self.macro_code = []
        self.is_macro = False
        

    def process_line(self, line): 
        #Next, process the line
        """Processes each line of the assembly code for Pass One."""
        #label, operation, operands = self.parse_line(line)
        label = None
        operation = None
        operands = None
        
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
            
        
        # Set location counter for the current block
        location_counter = self.cs.get_location_counter()
        
        #Check for USE directive. This indicates program switching
        if operation == 'USE':
            self.cs.update_location_counter(location_counter) #Update the location counter for the new block
            self.cs.set_program_block(operands if operands else 'Default')
            #Initialize the location counter for the new block (If neeeded)
            if self.cs.get_location_counter() == None:
                self.cs.update_location_counter(0)
            return
            

        elif operation == 'LTORG' or operation == 'END': #Check for LTORG or END
            #Assign the literals to the location counter
            for key in self.cs.get_literal_keys():
                if self.cs.get_literal_value(key) == None:
                    location_counter = self.cs.get_location_counter()
                    self.cs.add_literal(key, f'{location_counter:04X}')
                    hex_location = f'{location_counter:04X}' #Convert location counter to hex string
                    self.cs.update_intermediate_code([hex_location, '*', key, ''])
                    self.cs.update_current_block(self.calcualte_X_C(key[1:]))
            return
        if label:
            try:
                if operation == 'EQU':
                    if operands.startswith('*'):
                        self.cs.add_symbol(label, f'{location_counter:04X}')
                    else:
                        value = self.calculate_EQU(operands, location_counter, label)
                        self.cs.add_symbol(label, value)
                        
                    return
                elif any(op in operands for op in ['+', '-', '/', '*']):
                    value = self.calculate_EQU(operands, location_counter, label)
                    self.cs.add_symbol(label, f'{location_counter:04X}') 
                    operands = value
                else:     
                    self.cs.add_symbol(label, f'{location_counter:04X}')
            except ValueError as e:
                print(f"Error: {e}")
                
        # Check for literals
        if operands:
            if operands.startswith('=C') or operands.startswith('=X'):
                self.cs.add_literal(operands, None)
            
        #Store the intermediate code for Pass Two
        hex_location = f'{location_counter:04X}' #Convert location counter to hex string
        if operation == "LDB":
            # Push Value of base register to symbol table
            self.cs.add_symbol("BASE", f'{location_counter:04X}')
        elif operation == 'RESW' or operation == 'RESB' or operation == 'RESD' or operation == 'RESQ' or operation == 'BASE' or operation == 'NOBASE':
            instruction_length = self.get_instruction_length(operation,operands)
            self.cs.update_current_block(instruction_length)
            return
        self.cs.update_intermediate_code([hex_location, label, operation, operands if operands else ''])

        #Updating location counter based on instruction length        
        instruction_length = self.get_instruction_length(operation, operands if operands else None)
        self.cs.update_current_block(instruction_length)
                

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
            return self.calcualte_X_C(operands)
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
    
    def calcualte_X_C(self, operands):
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
        for cs in self.controlSections.values():
            cs.set_length(cs.get_location_counter() - cs.get_start_address())
        return self.controlSections
