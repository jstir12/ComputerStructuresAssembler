import re

class MacroTable:
    def __init__(self):
        self.macros = {}

    def define_macro(self, name, params, body):
        if name in self.macros:
            raise ValueError(f"Macro {name} is already defined.")
        self.macros[name] = {"params": params, "body": body}

    def expand_macros(self, code):
        expanded_code = []
        for line in code:
            line_parts = line.split()
            if line_parts[0] in self.macros:
                macro_name = line_parts[0]
                macro = self.macros[macro_name]
                
                # Substitute parameters in the macro body
                if len(line_parts) > 1:
                    args = line_parts[1].split(",")  # Handle comma-separated arguments
                    if len(args) != len(macro["params"]):
                        raise ValueError(f"Incorrect number of arguments for macro {macro_name}. Expected {len(macro['params'])}, got {len(args)}.")
                    
                    expanded = []
                    for instruction in macro["body"]:
                        for param, arg in zip(macro["params"], args):
                            # Use regular expressions to ensure we are replacing whole words only
                            instruction = re.sub(rf'\b{param}\b', arg, instruction)
                        expanded.append(instruction)
                    expanded_code.extend(expanded)
            else:
                expanded_code.append(line)
        return expanded_code

