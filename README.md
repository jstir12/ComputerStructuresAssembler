# ComputerStructuresAssembler

This is a two pass assembler in python

## Files and Directories

- **Assembly/**: Contains assembly language source files.
- **Object_Code_Files/**: Contains generated object code files.
- **ControlSection.py**: Implements the `ControlSection` class for managing control sections.
- **Macros.py**: Implements the `Macros` class for defining and expanding macros.
- **main.py**: Entry point of the assembler.
- **OpTable.py**: Implements the `OpTable` class for managing operation codes.
- **PassOne.py**: Implements the `PassOne` class for the first pass of the assembler.
- **PassTwo.py**: Implements the `PassTwo` class for the second pass of the assembler.
- **SymTable.py**: Implements the `SymTable` class for managing the symbol table.
- **.gitignore**: Specifies files and directories to be ignored by Git.

## Usage

1. **Run the Assembler**
  - Navigate to the Project Folder.

```sh
python ./main.py
```

2. **Input File**
   - The assembler will prompt you to enter the name of the assembly file (without extension) located in the `Assembly/` directory.
3. **Output**
   - The assembler will generate object code files in the Object_Code_Files/ directory.

## Classes and Methods

### `ControlSection.py`

- **ControlSection**:
  - `add_symbol(symbol_name, address, block_number)`
  - `add_macro()`
  - `update_macro(body)`
  - `set_external_refs(external_refs)`
  - `set_external_defs(external_defs)`
  - `set_external_defs_address(external_defs, address)`
  - `set_length(length)`
  - `set_start_address(start_address)`
  - `set_program_block(block)`
  - `get_symbol_address(symbol_name)`
  - `get_symbol_table()`
  - `get_program_block()`
  - `get_external_refs()`
  - `get_external_defs()`
  - `get_length()`
  - `get_start_address()`
  - `get_name()`
  - `get_symbols()`
  - `get_intermediate_code()`
  - `get_modification_records()`
  - `get_functions()`
  - `get_machine_code()`
  - `get_macros()`
  - `get_macro(macro_name)`
  - `get_immediates()`
  - `get_block_info()`
  - `add_block_info(block_name, block_number, address, length)`
  - `add_immediate(immediate)`
  - `resolve_external_reference(symbol_name, global_symbol_table)`
  - `update_location_counter(value)`
  - `get_location_counter()`
  - `get_location_counter_with_block(block)`
  - `update_current_block(value)`
  - `update_intermediate_code(value)`
  - `update_machine_code(value)`
  - `add_modification_record(value)`
  - `add_function(function)`
  - `add_literal(literal_name, literal_value, block)`
  - `add_expression(expression)`
  - `get_literal_keys()`
  - `get_literal_value(literal_name)`
  - `get_literal_table()`
  - `search_location_counter(block)`
  - `__repr__()`

### `Macros.py`

- **Macros**:
  - `define_macro(name, params, body)`
  - `expand_macros(name, args)`

### `PassOne.py`

- **PassOne**:
  - `process_line(line)`
  - `finalize_block_lengths()`
  - `get_instruction_length(operation, operands)`
  - `pre_process(file_path)`
  - `calcualte_X_C(operands)`
  - `calculate_EQU(operands, location_counter, label)`
  - `add_modification_record(operator, left_operand, right_operand, location_counter, label)`
  - `create_new_control_section(label)`
  - `run(input_file)`

### `PassTwo.py`

- **PassTwo**:
  - `generate_machine_code()`
  - `write_object_code_file()`
  - `calculate_object_code(opcode, format, operand, pc)`
  - `calculate_disp(label_address, format, base_register, pc)`
  - `get_label_address(operand, n, i)`
  - `determine_addressing_flags(operand)`
  - `get_register_code(register)`
  - `get_X_C(value)`
  - `calculate_EQU(operands, location_counter, label)`
  - `add_modification_record(operator, left_operand, right_operand, location_counter, label)`

### `SymTable.py`

- **SymTable**:
  - `add_symbol(symbol, address, block_number)`
  - `get_address(symbol)`
  - `get_address_and_block(symbol)`
  - `exists(symbol)`

### `OpTable.py`

- **OpTable**:
  - `getOpcode(mnemonic)`
  - `getFormat(mnemonic)`
  - `getOpcodeValue(mnemonic)`
