from OpTable import OpTable
from SymTable import SymTable
from PassOne import PassOne
from PassTwo import PassTwo

def main():
    machine_code = []
    # Prompt the user for the file path
    
    #file_path = input("Please enter the path to the file you want to upload: ")
    # Create the OpTable and SymTable objects
    op_table = OpTable()
    # Create the PassOne object
    passOne = PassOne(op_table)
    control_sections = passOne.run("Assembly/literals.txt")
    # Create the PassTwo object
    passTwo = PassTwo(control_sections, op_table)
    passTwo.generate_machine_code()
    # Write the machine code to a file
    passTwo.write_object_code_file()
    print("Machine code written to object_code.txt")
    
    

if __name__ == "__main__":
    main()