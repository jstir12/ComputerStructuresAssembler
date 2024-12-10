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

    def process_line(self, line): 
        #Next, process the line
        """Processes each line of the assembly code for Pass One."""
        #label, operation, operands = self.parse_line(line)
        label = None
        operation = None
        operands = []
        
        #Since the codes are stored in inside, arrays, we can use their length to determine labels, operations, and operands
        if len(line) == 3:
            label = line[0]
            operation = line[1] #The operation is the second element in the array
            operands = line[2].split(',') #The rest of the elements are operands
        elif len(line) == 2:
            operation = line[0]
            operands = line[1].split(',') #Split the operands by comma
        elif len(line) == 1:
            operation = line[0]
        #Look for a START operation
        if operation == 'START':
            # Create new control section
            self.global_starting_address = int(operands[0], 16)
            self.create_new_control_section(label)
            return
        elif operation == 'CSECT':
            self.create_new_control_section(label)
            return
        elif operation == 'EXTDEF':
            for symbol in operands:
                self.cs.set_external_defs(symbol)
            return
        elif operation == 'EXTREF':
            self.cs.set_external_refs(operands)
            return
        
        # Set location counter for the current block
        location_counter = self.cs.get_location_counter()
        
        #Check for USE directive. This indicates program switching
        if operation == 'USE':
            self.cs.update_location_counter(location_counter) #Update the location counter for the new block
            self.cs.set_program_block(operands or 'Default')
            #Initialize the location counter for the new block (If neeeded)
            if self.cs.get_location_counter() == None:
                self.cs.update_location_counter(0)
                return

        elif operation == 'LTORG' or operation == 'END': #Check for LTORG or END
            #Assign the literals to the location counter
            for key in self.cs.get_literal_keys():
                if self.cs.get_literal_value(key) == None:
                    self.cs.add_literal(key, f'{location_counter:04X}')
                    hex_location = f'{location_counter:04X}' #Convert location counter to hex string
                    self.cs.update_intermediate_code([hex_location, '*', key, ''])
                    self.cs.update_current_block(self.calcualte_X_C(key[1:]))
            return
        if label:
            try:
                if operation == 'EQU':
                    if operands[0].startswith('*'):
                        self.cs.add_symbol(label, f'{location_counter:04X}')
                    else:
                        value ,parts = self.calculate_EQU(operands[0])
                        self.cs.add_symbol(label, value)
                        groups = parts.groups()
                        for i, part in enumerate(groups):  # Enumerate through groups
                            if part in {"+", "-", "*", "/"}:
                                continue  # Skip operators

                            # Handle the first part differently
                            if i == 0:
                                self.cs.add_modification_record([f'{location_counter:06X}', f'{len(label):02X}', "+" + part])
                            else:
                                self.cs.add_modification_record([f'{location_counter:06X}', f'{len(label):02X}', groups[i-1] + part])                  
                    return          
                self.cs.add_symbol(label, f'{location_counter:04X}')
            except ValueError as e:
                print(f"Error: {e}")
                
        # Check for literals
        if operands:
            if operands[0].startswith('=C') or operands[0].startswith('=X'):
                self.cs.add_literal(operands[0], None)
            
        #Store the intermediate code for Pass Two
        hex_location = f'{location_counter:04X}' #Convert location counter to hex string
        if operation == "LDB":
            # Push Value of base register to symbol table
            self.cs.add_symbol("BASE", f'{location_counter:04X}')
        elif operation == 'RESW' or operation == 'RESB' or operation == 'RESD' or operation == 'RESQ' or operation == 'WORD' or operation == 'BASE' or operation == 'NOBASE':
            instruction_length = self.get_instruction_length(operation,operands[0])
            self.location_counters[self.current_block] += instruction_length
            self.cs.update_location_counter(instruction_length)
            return
        self.intermediate_code.append([hex_location, label, operation, operands[0]])
        self.cs.update_intermediate_code([hex_location, label, operation, operands[0]])

        #Updating location counter based on instruction length        
        instruction_length = self.get_instruction_length(operation,operands[0])
        self.cs.update_location_counter(instruction_length)
                

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
    
    def calculate_EQU(self, operands):
        string_pattern = r"([A-Za-z0-9]+)([+\-*/])([A-Za-z0-9]+)"
        match = re.match(string_pattern, operands)
        operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y
        }
        if match:
            left_operand = self.symbol_table.get_address(match.group(1))
            operator = match.group(2)
            right_operand = self.symbol_table.get_address(match.group(3))
            
            
            result = operations[operator](int(left_operand, 16), int(right_operand, 16))
            return f'{result:04X}', match
    
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
        print (self.symbol_table.symbols)
        self.program_length = self.location_counters[self.current_block] - self.starting_address #Final location counter - starting address
        return self.intermediate_code, f'{self.program_length:04X}', f'{self.starting_address:04X}', self.program_name, self.literal_table, self.modification_records #Return the intermediate code for Pass Tw


"""op_table = OpTable()
sym_table = SymTable()
 # Create the PassOne object
passOne = PassOne(op_table, sym_table)

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
   
