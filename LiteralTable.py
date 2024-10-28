class LiteralTable:
    def __init__(self):
        # Dictionary to store literals with their properties
        # Key: literal string (e.g., "=C'EOF'")
        # Value: dictionary containing address, length, and value
        self.literals = {}
        # Track the current position in memory for literal pool
        self.current_address = 0
        # Keep track of literals in order of appearance
        self.literal_order = []

    def add_literal(self, literal):
        """
        Add a literal to the table if it doesn't exist.
        Returns True if it's a new literal, False if it already exists.
        """
        if literal not in self.literals:
            # Strip the '=' prefix for processing
            literal_value = literal[1:]
            
            # Calculate the length and actual value based on literal type
            if literal_value.startswith('C'):
                # Character literal (e.g., C'EOF')
                value = literal_value[2:-1]  # Remove C' and final '
                length = len(value)
                byte_value = ''.join([format(ord(c), '02X') for c in value])
            elif literal_value.startswith('X'):
                # Hexadecimal literal (e.g., X'F1')
                value = literal_value[2:-1]  # Remove X' and final '
                length = len(value) // 2
                byte_value = value
            else:
                # Decimal literal (e.g., =5)
                value = int(literal_value)
                length = 3  # Standard length for numeric literals
                byte_value = format(value, '06X')

            self.literals[literal] = {
                'address': None,  # Address will be assigned during literal pool generation
                'length': length,
                'value': byte_value
            }
            self.literal_order.append(literal)
            return True
        return False

    def assign_addresses(self, start_address):
        """
        Assign addresses to all literals in the literal pool.
        Called at the end of pass one.
        """
        self.current_address = start_address
        
        for literal in self.literal_order:
            self.literals[literal]['address'] = self.current_address
            self.current_address += self.literals[literal]['length']

    def get_literal_address(self, literal):
        """Return the address assigned to a literal."""
        if literal in self.literals:
            return self.literals[literal]['address']
        return None

    def get_literal_pool_size(self):
        """Return the total size of all literals."""
        return sum(lit['length'] for lit in self.literals.values())

    def get_object_code(self, literal):
        """Return the object code for a given literal."""
        if literal in self.literals:
            return self.literals[literal]['value']
        return None

    def generate_literal_pool(self):
        """
        Generate the literal pool object code.
        Returns a list of tuples (address, object_code).
        """
        pool = []
        for literal in self.literal_order:
            lit_info = self.literals[literal]
            pool.append((lit_info['address'], lit_info['value']))
        return pool
