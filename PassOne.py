import re
class PassOne:
    def __init__(self, OpTable, SymTable):
        #self.literal_table = LiteralTable()
        self.symbol_table = SymTable
        self.op_table = OpTable
        self.literal_table = {}
        self.location_counter = 0
        self.starting_address = 0
        self.program_length = 0
        self.intermediate_code = [] #Store intermediate code for Pass Two
        self.program_name = 'Basic' #Default program name

    def process_line(self, line): 
        #Next, process the line
        """Processes each line of the assembly code for Pass One."""
        #label, operation, operands = self.parse_line(line)
        label = None
        operation = None
        operands = None
        is_literal = False
        #Since the codes are stored in inside, arrays, we can use their length to determine labels, operations, and operands
        if len(line) == 3:
            label = line[0]
            operation = line[1] #The operation is the second element in the array
            operands = line[2] #The rest of the elements are operands
        elif len(line) == 2:
            operation = line[0]
            operands = line[1]
        elif len(line) == 1:
            operation = line[0]
        #Look for a START operation
        if operation == 'START':
            #Set the starting adress to the one found with start
            self.starting_address = int(operands[0], 16)
            self.location_counter = self.starting_address
            self.program_name = label
            return
        elif operation == 'LTORG' or operation == 'END': #Check for LTORG or END
            #Assign the literals to the location counter
            for key in self.literal_table.keys():
                if self.literal_table[key][0] == None:
                    self.literal_table[key][0] = f'{self.location_counter:04X}'
                    hex_location = f'{self.location_counter:04X}' #Convert location counter to hex string
                    self.intermediate_code.append([hex_location, '*', key, ''])
                    self.location_counter += self.calcualte_X_C(key[1:])
            return
        if label:
            try:
                if operation == 'EQU':
                    if operands.startswith('*'):
                        self.symbol_table.add_symbol(label, f'{self.location_counter:04X}')
                    else:
                        self.symbol_table.add_symbol(label, self.calculate_EQU(operands))
                    return          
                self.symbol_table.add_symbol(label, f'{self.location_counter:04X}')
            except ValueError as e:
                print(f"Error: {e}")
        # Check for literals
        if operands:
            if operands.startswith('=C') or operands.startswith('=X'):
                self.literal_table[operands] = [None]
            
        #Store the intermediate code for Pass Two
        hex_location = f'{self.location_counter:04X}' #Convert location counter to hex string
        if operation == "LDB":
            # Push Value of base register to symbol table
            self.symbol_table.add_symbol("BASE", operands)
        elif operation == 'RESW' or operation == 'RESB' or operation == 'RESD' or operation == 'RESQ' or operation == 'WORD' or operation == 'BASE' or operation == 'NOBASE':
            instruction_length = self.get_instruction_length(operation,operands)
            self.location_counter += instruction_length
            return
        self.intermediate_code.append([hex_location, label, operation, operands])

        #Updating location counter based on instruction length        
        instruction_length = self.get_instruction_length(operation,operands)
        self.location_counter += instruction_length
                

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
            return f'{result:04X}'
        
    def run(self, input_file):
        #Will process the input file and return the intermediate code for Pass Two
        #First, pre-process the file
        lines = self.pre_process(input_file)
        for line in lines:
            self.process_line(line)
        print (self.symbol_table.symbols)
        self.program_length = self.location_counter - self.starting_address #Final location counter - starting address
        return self.intermediate_code, f'{self.program_length:04X}', f'{self.starting_address:04X}', self.program_name #Return the intermediate code for Pass Two
