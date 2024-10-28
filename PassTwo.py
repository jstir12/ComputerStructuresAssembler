class PassTwo:
    def __init__(self, symbol_table, intermediate_code, op_table):
        self.symbol_table = symbol_table
        self.intermediate_code = intermediate_code
        self.machine_code = []
        self.op_table = op_table

    def generate_machine_code(self):
        for line in self.intermediate_code:
            # Initialize variables for label, mnemonic, and operand
            label = None
            mnemonic = None
            operand = None
            
            # Parse line for label, mnemonic, and operand
            if len(line) == 3:
                label, mnemonic, operand = line
            elif len(line) == 2:
                mnemonic, operand = line
            else:
                mnemonic = line[0]

            # Get opcode and format
            if mnemonic in self.op_table.optable:
                opcode, format = self.op_table.getOpcode(mnemonic)
                # Handle extended format if '+' prefix exists
                if operand and operand[0] == '+':
                    format = 4  # Extended format
            else:
                # Handle error if mnemonic not found in op_table
                print(f"Error: Mnemonic '{mnemonic}' not found in opcode table.")
                continue

            # Calculate object code for the mnemonic
            object_code = self.calculate_object_code(opcode, format, operand)
            if object_code:
                self.machine_code.append(object_code)

        return self.machine_code

    def calculate_object_code(self, opcode, format, operand):
        object_code = ""

        # Calculate object code based on format
        if format == 1:
            object_code = f"{opcode:02X}"
        
        elif format == 2:
            reg1, reg2 = operand.split(",")
            reg1_code = self.get_register_code(reg1)
            reg2_code = self.get_register_code(reg2)
            object_code = f"{opcode:02X}{reg1_code}{reg2_code}" 
        
        elif format == 3 or format == 4:
            # Get n, i, and x flags
            if format == 3:
                e = 0
                if operand and operand[0] == '@':
                    n, i = 1, 0  # indirect addressing
                elif operand and operand[0] == '#':
                    n, i = 0, 1  # immediate addressing
                elif operand and operand[0] == '=':
                    n, i = 1, 1  # Literal addressing
                else:
                    n, i = 1, 1  # direct addressing
            else:
                n, i, e = 1, 1, 1  # For format 4

            x = 1 if ',X' in operand else 0  # Check for indexed addressing
            
            # Determine the address
            if operand and operand[0] == '=':
                # Handle literals
                literal = operand[1:]  # Remove '=' from the literal
                address = self.symbol_table.get_address(literal)  # Assume literal address is in symbol table
            else:
                if x == 0:
                    if n == 1 and i == 1:
                        address = self.symbol_table.get_address(operand)
                    elif n == 0 or i == 0:
                        address = operand[1:]  # Remove '#' or '@'
                else:
                    if n == 1 and i == 1:
                        address = self.symbol_table.get_address(operand[:-2])  # Remove ',X'
                    elif n == 0 or i == 0:
                        address = operand[1:-2]  # Remove '#' or '@' and ',X'

            # Calculate displacement (assume PC relative for simplicity)
            if address is not None:
                if format == 3:
                    # For format 3, we need a 12-bit address
                    object_code = f"{opcode:02X}{(n << 3) | (i << 2) | (x << 1)}{address:03X}"
                elif format == 4:
                    # For format 4, we need a 20-bit address
                    object_code = f"{opcode:02X}{(n << 3) | (i << 2) | (x << 1) | e}{address:05X}"

        return object_code

    def get_register_code(self, register):
        register_codes = {"A": "0", "X": "1", "L": "2", "B": "3", "S": "4", "T": "5", "F": "6"}
        return register_codes.get(register, "0")

            
