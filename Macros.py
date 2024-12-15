import re

class Macros:
    def __init__(self):
        self.macros = {}

    def define_macro(self, name, params, body):
        if name in self.macros:
            raise ValueError(f"Macro {name} is already defined.")
        self.macros[name] = [body, params]

    def expand_macros(self, name, args):
        expanded_code = []
        code, params = self.macros[name]
        for line in code:
            # Make a copy of the line to prevent changes to the original array
            line_copy = list(line)
            
            if len(line_copy) == 3:
                if any(param in line_copy[2] for param in params):  # Check if any param is in line[2]
                    for param in params:
                        if param in line_copy[2]:
                            # Replace only the part of line_copy[2] that matches param
                            line_copy[2] = line_copy[2].replace(param, args[params.index(param)])

            elif len(line_copy) == 2:
                if any(param in line_copy[1] for param in params):  # Check if any param is in line[1]
                    for param in params:
                        if param in line_copy[1]:
                            # Replace only the part of line_copy[1] that matches param
                            line_copy[1] = line_copy[1].replace(param, args[params.index(param)])
                            break

            # Append the modified copy of the line to expanded_code
            expanded_code.append(line_copy)

        return expanded_code

