
class ControlSection:
    def __init__(self, name):
        """Initializes a control section with its name."""
        self.name = name  # Name of the control section
        self.symbols = {}  # Local symbols (name -> address)
        self.external_refs = []  # External references (list of symbol names)
        self.start_address = 0  # Starting address of the control section in memory
        self.length = 0  # Length of the control section in memory
    
    def add_symbol(self, symbol_name, address):
        """Adds a local symbol to the control section."""
        self.symbols[symbol_name] = address
    
    def add_external_reference(self, symbol_name):
        """Marks a symbol as being externally referenced in this control section."""
        if symbol_name not in self.external_refs:
            self.external_refs.append(symbol_name)
    
    def set_length(self, length):
        """Sets the length of the control section."""
        self.length = length
    
    def set_start_address(self, start_address):
        """Sets the starting address of the control section in memory."""
        self.start_address = start_address
    
    def get_symbol_address(self, symbol_name):
        """Retrieves the address of a symbol if it exists locally in this control section."""
        return self.symbols.get(symbol_name, None)
    
    def resolve_external_reference(self, symbol_name, global_symbol_table):
        """Resolves an external reference to a symbol by looking it up in the global symbol table."""
        if symbol_name in global_symbol_table:
            return global_symbol_table[symbol_name]
        else:
            raise ValueError(f"Error: External symbol '{symbol_name}' cannot be resolved.")
    
    def __repr__(self):
        """String representation of the Control Section."""
        return f"Control Section {self.name}:\n" \
               f"  Start Address: {self.start_address}\n" \
               f"  Length: {self.length}\n" \
               f"  Local Symbols: {self.symbols}\n" \
               f"  External References: {self.external_refs}\n"

