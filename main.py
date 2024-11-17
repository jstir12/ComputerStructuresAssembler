from OpTable import OpTable
from SymTable import SymTable

def pre_process(file_path):
    # Try to open the file and read it line by line
    try:
        with open(file_path, 'r') as file:
            print("Reading file line by line:")
            lines = []
            for line in file:
                line = line.split(".")[0].strip()  # Remove comments and strip leading/trailing spaces
                line = line.replace('\t', ' ')     # Replace tabs with a single space
                if line != "":
                    code = line.split(" ")
                lines.append(code)
            return lines   
    except FileNotFoundError:
        print("Error: The file was not found. Please check the path and try again.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    

def main():
    # Prompt the user for the file path
    file_path = input("Please enter the path to the file you want to upload: ")
    codeLines = pre_process(file_path)
    print(codeLines)
    

if __name__ == "__main__":
    main()