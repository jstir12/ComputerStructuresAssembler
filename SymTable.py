class SymTable:
    def __init__(self):
        self.symbols = {}
        
    def add_symbol(self, symbol, address, block_number):
        if symbol in self.symbols:
            raise ValueError(f"Duplicate symbol: {symbol}")
        self.symbols[symbol] = [address, block_number]
            
    def get_address(self, symbol):
        if symbol not in self.symbols:
            raise KeyError(f"Symbol not found: {symbol}")
        return self.symbols[symbol][0]
    
    def exists(self, symbol):
        return symbol in self.symbols
    
            