from literal_table import LiteralTable

class PassOne:
    def __init__(self):
        self.literal_table = LiteralTable()
        self.location_counter = 0

    def process_line(self, line):
        """Processes each line of the assembly code for Pass One."""
        label, operation, operands = self.parse_line(line)

        # Check for literals in operands
        for operand in operands:
            if operand.startswith('='):
                self.literal_table.add_literal(operand)

        # Update location counter based on instruction length
        self.location_counter += self.get_instruction_length(operation)

        # At the end of the program, assign addresses to literals
        if operation == 'END':
            self.literal_table.assign_addresses(self.location_counter)

    def parse_line(self, line):
        """Basic line parsing to extract label, operation, and operands."""
        parts = line.split()
        label = parts[0] if parts else None
        operation = parts[1] if len(parts) > 1 else None
        operands = parts[2:] if len(parts) > 2 else []
        return label, operation, operands

    def get_instruction_length(self, operation):
        """Determine the length of an instruction based on its operation."""
        # For simplicity, assume each operation has a fixed length
        return 3  # Example: fixed length for each instruction
