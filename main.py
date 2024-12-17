from OpTable import OpTable
from SymTable import SymTable
from PassOne import PassOne
from PassTwo import PassTwo
import os

def main():
    machine_code = []
    
    # Prompt the user for the file path
    file_path = input("Please enter the name of the file you want to upload: ")
    full_path = f'Assembly/{file_path}.txt'

    # Check if the file exists before proceeding
    if not os.path.exists(full_path):
        print(f"Error: The file '{full_path}' was not found. Exiting program.")
        return  # Exit the program

    # Create the OpTable and SymTable objects
    op_table = OpTable()
    
    # Create the PassOne object
    passOne = PassOne(op_table)
    control_sections = passOne.run(full_path)
    
    # Create the PassTwo object
    passTwo = PassTwo(control_sections, op_table)
    passTwo.generate_machine_code()
    
    # Write the machine code to a file
    passTwo.write_object_code_file()
    print(f"File: {file_path}, successfully processed.")
