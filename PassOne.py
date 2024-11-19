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
        print(line)
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

    def parse_line(self, line):
        """Basic line parsing to extract label, operation, and operands."""
        parts = line.split()
        label = None
        operation = None
        operands = []
        #See if there is even a label to begin with 
        if parts and not parts[0].startswith(' ','\t'):
            label = parts[0] #Label exists and the first thing in the line is the label
            parts = parts[1:] #rest of the line are used as the operation and operands
        if parts: #There are no labels
            operation = parts[0] #First thing in the line is the operation
            operands = parts[1:]
        
        return label, operation, operands
'''#Got rid of parse_line method since we are already splitting the line in process_line

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
        
        #Referring to the opTable class for the format type
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
