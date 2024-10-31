#from literal_table import LiteralTable
from SymTable import SymTable
from OpTable import OpTable

class PassOne:
    def __init__(self):
        #self.literal_table = LiteralTable()
        self.symbol_table = SymTable()
        self.op_table = OpTable()
        self.location_counter = 0
        self.intermediate_code = [] #Store intermediate code for Pass Two

    def process_line(self, line):
        #First step is to ignore the comment
        line = self.remove_comments(line) 
        #Next, process the line
        """Processes each line of the assembly code for Pass One."""
        label, operation, operands = self.parse_line(line)

        #If there is a label
        if label:
            try:
                self.symbol_table.add_symbol(label, self.location_counter)
            except ValueError as e:
                print(f"Error: {e}")

        hex_location = f'{self.location_counter:04X}' #Convert location counter to hex string
        self.intermediate_code.append([self.location_counter, label, operation, operands])


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
        ''' #I don't think we need to worry about literals yet

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

    def get_instruction_length(self, operation,operands):
        """Determine the length of an instruction based on its operation."""
        #For now, just check if the operation is RESW. Using basic.txt as a reference
        if operation == 'RESW':
            return 3 * int(operands[0]) #Since each word is 3 bytes
        #Referring to the opTable class for the format type
        opcode_format = self.op_table.getFormat(operation)
        if opcode_format: #If the format is found
            return int(opcode_format)
        else:
            return 3 #Default length for instructions
    
    def remove_comments(self, line): 
        #Will remove comments from the line. The comments come after a '.'
        return line.split('.')[0].strip()
    
    def run(self, input_file):
        #Will process the input file and return the intermediate code for Pass Two
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip() #Remove leading and trailing whitespace
                if line:
                    self.process_line(line)

        return self.intermediate_code #Return the intermediate code for Pass Two

        
