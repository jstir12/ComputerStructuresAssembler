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
        self.program_blocks_maps = {"Default": 0}
        self.program_block_amount = 0
        self.block_info = {} #Dictionary to store block name, number, address, and length




#Create 2 dict: 1 that maps to numbers to names, 1 maps name to starting address and length
#Add new variable up top to keep track of program block amount
#Add the end, calcularte each program starting block based of length of previos rogram block
#Anytime we're referencing symtable getting address, we need to ensure the correct index and not just the array


    def process_line(self, line): 
        #Next, process the line
        """Processes each line of the assembly code for Pass One."""
        #label, operation, operands = self.parse_line(line)
        label = None
        operation = None
        operands = None
        
        #Since the codes are stored in inside, arrays, we can use their length to determine labels, operations, and operands
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
        
        # Set location counter for the current block
        location_counter = self.cs.get_location_counter()
        
        #Check for USE directive. This indicates program switching
        if operation == 'USE':
            self.cs.update_location_counter(location_counter) #Update the location counter for the new block
            self.cs.set_program_block(operands if operands else 'Default')
            #Initialize the location counter for the new block (If neeeded)
            if self.cs.get_location_counter() == None:
                self.cs.update_location_counter(0)

            
            #Map numbers to names
            if operands is None:
                operands = 'Default'
            if operands not in self.program_blocks_maps:
                self.program_block_amount += 1
                self.program_blocks_maps[operands] = self.program_block_amount
            else:
                operands = self.program_blocks_maps[operands]

            print(self.program_blocks_maps)
            '''
            #Calculate the starting address and legnth block
            if operands not in self.block_info:
                #Get the block number based on the program blocks map
                block_number = self.program_blocks_maps[operands]
                
                if block_number == 0:
                    starting_address = self.global_starting_address  #Set the starting address for the first block
                else:
                    if self.block_info:
                        last_block = list(self.block_info.values())[-1]  #Set the last block in block_info
                        starting_address = last_block['address'] + last_block['length']  #Calculate starting address for the new block
                    else:
                        starting_address = self.global_starting_address
                
                #Set the length to 0 for now (will be updated later)
                length = 0

                #Store the block information
                self.block_info[operands] = {
                    'block_number': block_number,
                    'address': starting_address,
                    'length': length
                }

                print(self.program_blocks_maps)'''
            
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
                        self.cs.add_symbol(label, f'{location_counter:04X}', self.cs.get_program_block())
                    else:
                        value = self.calculate_EQU(operands, location_counter, label)
                        self.cs.add_symbol(label, value, self.cs.get_program_block())
                        
                        
                    return
                elif any(op in operands for op in ['+', '-', '/', '*']):
                    value = self.calculate_EQU(operands, location_counter, label)
                    self.cs.add_symbol(label, f'{location_counter:04X}', self.cs.get_program_block()) 
                    operands = value
                else: 
                    self.cs.add_symbol(label, f'{location_counter:04X}',self.cs.get_program_block())
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
            self.cs.add_symbol("BASE", f'{location_counter:04X}',self.cs.get_program_block())
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
        #Anytime I come across the EQU satement, add it to an arry or dictionary of unresolved addresses that need to be fixed
        #At the end, I will calculate teh unresolved addresses and 
        #IF you're subtracting, you change the program block number of that symbol to the default program block number
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
            self.process_line(line)
            #IF operator is = minus, set the program  block number to default program block number
        for cs in self.controlSections.values():
            cs.set_length(cs.get_location_counter() - cs.get_start_address())
        return self.controlSections
    
    
    

"""op_table = OpTable()
sym_table = SymTable()
# Create the PassOne object
passOne = PassOne(op_table, sym_table)

#print(passOne.run('Assembly/basic.txt'))

print(passOne.run('Assembly/prog_blocks.txt'))
from Macros import MacroTable

class PassOne:
    def __init__(self):
        self.macro_table = MacroTable()  # Initialize the MacroTable
        self.symbol_table = {}
        self.code = []  # Store the code for the next pass

    def process_line(self, line):
        # Check if the line defines a macro
        if line.startswith("MACRO"):
            # Example: MACRO MACRO_NAME param1, param2
            macro_name = line.split()[1]
            params = line.split()[2].split(",")  # Assuming parameter format is "param1,param2"
            body = []

            # Collect the body of the macro
            while True:
                line = self.get_next_line()  # Read next line
                if line == "ENDMACRO":
                    break
                body.append(line)

            # Add macro to the macro table
            self.macro_table.define_macro(macro_name, params, body)
            return None  # Don't process this line further, macro is defined

        # Otherwise, expand macros if necessary
        expanded_code = self.macro_table.expand_macros([line])
        if expanded_code:
            return expanded_code[0]  # Return the expanded line
        return line  # Otherwise, return the original line

    def process_code(self, code):
        for line in code:
            # First, handle macro expansion
            expanded_line = self.process_line(line)
            
            if expanded_line is None:
                continue  # Skip macro definition lines
            
            # Now process the expanded or original line as needed
            # Here you would typically process labels and generate the symbol table
            self.process_labels_and_symbols(expanded_line)
    
    def process_labels_and_symbols(self, line):
        # Handle labels and add them to the symbol table
        pass
from ControlSection import ControlSection

class PassOne:
    def __init__(self):
        self.control_sections = {}  # Dictionary to store control sections by name
        self.global_symbol_table = {}  # Global symbol table to store all symbols
        self.current_cs = None  # Current control section being processed
        self.current_address = 0  # Current memory address for the code
        self.code = []  # Store the code for the next pass

    def process_line(self, line):
        # Skip empty lines or comments
        if not line.strip() or line.startswith(';'):  # Assuming semicolon is used for comments
            return None
        
        # Check if the line defines a new control section (e.g., a section header)
        if line.startswith("CSECT"):
            cs_name = line.split()[1]  # Extract the name of the control section
            
            # Create a new control section object if it's not already defined
            if cs_name not in self.control_sections:
                new_cs = ControlSection(cs_name)
                new_cs.set_start_address(self.current_address)  # Set the start address
                self.control_sections[cs_name] = new_cs
                self.current_cs = new_cs  # Set the current control section
            
            return None  # Skip further processing, as this is a control section header
        
        # If the line defines a symbol, add it to the current control section's symbol table
        if ":" in line:  # This indicates a label (symbol definition)
            label = line.split(":")[0]
            if self.current_cs:
                self.current_cs.add_symbol(label, self.current_address)
            self.global_symbol_table[label] = self.current_address  # Add to global symbol table
            
        # If the line references an external symbol, add it to the external references
        if "EXTERNAL" in line:
            external_symbol = line.split()[1]
            if self.current_cs:
                self.current_cs.add_external_reference(external_symbol)
            
        # Process the instruction (increment address, process symbols, etc.)
        if self.current_cs:
            self.current_address += 4  # Assuming each instruction occupies 4 bytes
        
        return line  # Return the processed line
    
    def process_code(self, code):
        for line in code:
            # Process each line in the assembly code
            expanded_line = self.process_line(line)
            
            if expanded_line is None:
                continue  # Skip the control section header line
            
            # Here, you would typically handle other parsing tasks (like instruction decoding)
            # But since this is Pass One, we focus on control sections and symbols.

    def finalize_control_sections(self):
         Finalize the control sections by setting their lengths. 
        for cs_name, cs in self.control_sections.items():
            # The length is calculated based on the current memory address
            cs.set_length(self.current_address - cs.start_address)

    def get_global_symbol_table(self):
         Returns the global symbol table that includes all symbols from all control sections. 
        return self.global_symbol_table"""
   
