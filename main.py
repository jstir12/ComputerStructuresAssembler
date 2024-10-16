from OpTable import OpTable
from SymTable import SymTable

def interpret_line(line):
    # Check if the line is a comment
    print(line)

def main():
    # Prompt the user for the file path
    file_path = input("Please enter the path to the file you want to upload: ")

    # Try to open the file and read it line by line
    try:
        with open(file_path, 'r') as file:
            print("Reading file line by line:")
            for line in file:
                # Alright we will place logic for understanding the line here. Most likely will be a method call?
                interpret_line(line.strip())
    except FileNotFoundError:
        print("Error: The file was not found. Please check the path and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()