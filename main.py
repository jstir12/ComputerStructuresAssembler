from OpTable import OpTable
from SymTable import SymTable
from PassOne import PassOne
from PassTwo import PassTwo

def main():
    machine_code = []
    # Prompt the user for the file path
    file_path = input("Please enter the path to the file you want to upload: ")
    # Create the OpTable and SymTable objects
    op_table = OpTable()
    sym_table = SymTable()
    # Create the PassOne object
    passOne = PassOne(op_table, sym_table)
    intermediate_code, program_length, starting_address, program_name = passOne.run(file_path)
    # Create the PassTwo object
    passTwo = PassTwo(sym_table, intermediate_code, op_table, '0', program_name, starting_address, program_length, )
    machine_code = passTwo.generate_machine_code()
    
    
    

if __name__ == "__main__":
    main()