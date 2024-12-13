from SymTable import SymTable
class ControlSection:
    def __init__(self, name):
        """Initializes a control section with its name."""
        self.name = name  # Name of the control section
        self.symbols = SymTable()   # Local symbols (name -> address)
        self.external_refs = []  # External references (list of symbol names)
        self.external_defs = {}
        self.start_address = 0  # Starting address of the control section in memory
        self.length = 0  # Length of the control section in memory
        self.location_counters = {} #Store location counters for different blocks
        self.intermediate_code = [] #Store intermediate code for Pass Two
        self.modification_records = [] #Store modification records for Pass Two
        self.literal_table = {}
        self.program_block = None
        self.machine_code = []
        self.functions = []
    
    def add_symbol(self, symbol_name, address,block_number):
        """Adds a local symbol to the control section."""
        if symbol_name in self.external_defs and self.external_defs[symbol_name] is None:
            self.set_external_defs_address(symbol_name, address)
        self.symbols.add_symbol(symbol_name, address, block_number)
    
    def set_external_refs(self, external_refs):
        """Sets the external references for the control section."""
        self.external_refs = external_refs
    
    def set_external_defs(self, external_defs):
        """Sets the external definitions for the control section."""
        self.external_defs [external_defs] = None
    
    def set_external_defs_address(self, external_defs, address):
        """Sets the external definitions for the control section."""
        self.external_defs [external_defs] = address
    
    def set_length(self, length):
        """Sets the length of the control section."""
        self.length = length
    
    def set_start_address(self, start_address):
        """Sets the starting address of the control section in memory."""
        self.start_address = start_address
    
    def set_program_block(self, block):
        self.program_block = block 
    
    def set_functions(self, functions):
        self.functions = functions
    
    
    def get_symbol_address(self, symbol_name):
        """Retrieves the address of a symbol if it exists locally in this control section."""
        return self.symbols.get(symbol_name, None)
    
    def get_symbol_table(self):
        """Retrieves the symbol table for the control section."""
        return self.symbols
    
    def get_program_block(self):
        return self.program_block or 'Default'
    
    def get_external_refs(self):
        """Retrieves the external references for the control section."""
        return self.external_refs
    
    def get_external_defs(self):
        """Retrieves the external definitions for the control section."""
        return self.external_defs
    
    def get_length(self):
        """Retrieves the length of the control section."""
        return self.length
    
    def get_start_address(self):
        """Retrieves the starting address of the control section in memory."""
        return self.start_address
    
    def get_name(self):
        """Retrieves the name of the control section."""
        return self.name
    
    def get_symbols(self):
        """Retrieves the local symbols for the control section."""
        return self.symbols
    
    def get_symbol_address(self, symbol_name):
        """Retrieves the address of a symbol if it exists locally in this control section."""
        return self.symbols.get_address(symbol_name)
    
    def get_intermediate_code(self):
        """Retrieves the intermediate code for the control section."""
        return self.intermediate_code
    
    def get_modification_records(self):
        """Retrieves the modification records for the control section."""
        return self.modification_records
    
    def get_functions(self):
        return self.functions
    
    def get_machine_code(self): 
        return self.machine_code
    
    def resolve_external_reference(self, symbol_name, global_symbol_table):
        """Resolves an external reference to a symbol by looking it up in the global symbol table."""
        if symbol_name in global_symbol_table:
            return global_symbol_table[symbol_name]
        else:
            raise ValueError(f"Error: External symbol '{symbol_name}' cannot be resolved.")
    
    def update_location_counter(self, value):
        """Updates the location counter for a block."""
        self.location_counters[self.program_block] = value
    
    def get_location_counter(self):
        """Retrieves the location counter for a block."""
        return self.location_counters.get(self.program_block, None)
    
    def get_machine_code(self):
        """Retrieves the machine code for the control section."""
        return self.machine_code
    def update_current_block(self, value):
        """Updates the current block."""
        self.location_counters[self.program_block] += value
    
    def update_intermediate_code(self, value):
        """Updates the intermediate code."""
        self.intermediate_code.append(value)
    
    def update_machine_code(self, value):
        """Updates the machine code."""
        self.machine_code.append(value)
    
    def add_modification_record(self, value):
        """Adds a modification record."""
        self.modification_records.append(value)
    
    def add_function(self, function):
        self.functions.append(function)
    
    def add_literal(self, literal_name, literal_value):
        """Adds a literal to the literal table."""
        self.literal_table[literal_name] = literal_value
    
    def get_literal_keys(self):
        """Retrieves the keys of the literal table."""
        return self.literal_table.keys()
    
    def get_literal_value(self, literal_name):
        """Retrieves the value of a literal."""
        return self.literal_table.get(literal_name, None)
    
    def get_literal_table(self):
        """Retrieves the literal table."""
        return self.literal_table
    
    def search_location_counter(self, block):
        """Searches the location counter for a block."""
        return self.location_counters.get(self.program_block, None)
    
    def __repr__(self):
        """String representation of the Control Section."""
        return f"Control Section {self.name}:\n" \
               f"  Start Address: {self.start_address}\n" \
               f"  Length: {self.length}\n" \
               f"  Local Symbols: {self.symbols}\n" \
               f"  External References: {self.external_refs}\n"

