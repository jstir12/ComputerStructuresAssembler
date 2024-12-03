class PassOne:
    def __init__(self, OpTable, SymTable):
        #self.literal_table = LiteralTable()
        self.symbol_table = SymTable
        self.op_table = OpTable
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
        if label:
            try:
                self.symbol_table.add_symbol(label, f'{self.location_counter:04X}')
            except ValueError as e:
                print(f"Error: {e}")
        """
        #Handling immediate addressing
        if operands.startswith('#'): #'#' indicates immediate addressing
            immediate_value = operands[1:]
            if not immediate_value.isdigit(): #Check if it is a digit
                #Check if it already exists in the symbol table
                if not self.symbol_table.get_address(immediate_value):
                    #If it doesn't exist, add it to the symbol table
                    self.symbol_table.add_symbol(immediate_value, None)
        """
        

        #Store the intermediate code for Pass Two
        hex_location = f'{self.location_counter:04X}' #Convert location counter to hex string
        if operation == "LDB":
            # Push Value of base register to symbol table
            self.symbol_table.add_symbol("BASE", operands)
        elif operation == 'RESW' or operation == 'RESB' or operation == 'RESD' or operation == 'RESQ' or operation == 'END' or operation == 'WORD' or operation == 'BASE' or operation == 'NOBASE':
            instruction_length = self.get_instruction_length(operation,operands)
            self.location_counter += instruction_length
            return
        self.intermediate_code.append([hex_location, label, operation, operands])

        #Updating location counter based on instruction length
        instruction_length = self.get_instruction_length(operation,operands)
        self.location_counter += instruction_length
        

        '''
        # Check for literals in operands
        for operand in operands:
            if operand.startswith('='):
                self.literal_table.add_literal(operand)

        # Update location counter based on instruction length
        self.location_counter += self.get_instruction_length(operation)

        # At the end of the program, assign addresses to literals
        if operation == 'END':
            self.literal_table.assign_addresses(self.location_counter)
         #I don't think we need to worry about literals yet
        '''

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
            if operands.startswith('X'):
                return (len(operands) - 3) // 2
            elif operands.startswith('C'):
                return len(operands) - 3
        elif operation == 'END':
            return 0
        elif operation == 'BASE':
            return 0
        elif operation == 'NOBASE':
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
    
    
    
    def run(self, input_file):
        #Will process the input file and return the intermediate code for Pass Two
        #First, pre-process the file
        lines = self.pre_process(input_file)
        for line in lines:
            self.process_line(line)
        print (self.symbol_table.symbols)
        self.program_length = self.location_counter - self.starting_address #Final location counter - starting address
        return self.intermediate_code, f'{self.program_length:04X}', f'{self.starting_address:04X}', self.program_name #Return the intermediate code for Pass Two
