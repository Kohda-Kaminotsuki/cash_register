import sys
import math

CURRENCYLIST: list[list[str]] = [["USD", "Dollar", "United States Dollar", "Half Dollar", "$", "Half Dollar", "Quarter", "Dime", "Nickel", "Penny", "Pennies", "Cent", "¢"],
                                 ["EUR", "Euro", "European Euro",],
                                 ["GBP", "Pound", "Pounds", "British Pound", "British Pounds"],
                                 ["JPY", "Yen", "Yens", "Japanese Yen", "Japanese Yens","￥", "円",],
                                 ["CNY", "Yuan", "Yuans", "Chinese Yuan", "Chinese Yuans", "元"],
                                 ["RUB", "Ruble", "Rubles", "Russian Ruble", "Russian Rubles", "₽", "рубль",],
                                 ["INR", "Rupee", "Rupees", "Indian Rupee", "Indian Rupees", "₹"],
                                 ["AUD", "Australian Dollar", "Australian Dollars"],
                                 ["CAD", "Canadian Dollar", "Canadian Dollars", "Loonie", "Toonie", ],
                                 ["CHF", "Swiss Franc", "Swiss Francs"],
                                 ["NZD", "New Zealand Dollar", "New Zealand Dollars"],
                                 ["ZAR", "South African Rand", "South African Rands"],
                                 ["SEK", "Swedish Krona", "Swedish Kronas"],
                                 ["NOK", "Norwegian Krone", "Norwegian Krones"],
                                 ["DKK", "Danish Krone", "Danish Krones"],
                                 ["HKD", "Hong Kong Dollar", "Hong Kong Dollars"],
                                 ["SGD", "Singapore Dollar", "Singapore Dollars"],
                                 ["KRW", "South Korean Won", "South Korean Wons"],
                                 ["MXN", "Mexican Peso", "Mexican Pesos"],
                                 ["WIZ", "Galleon", "Sickle", "Knut", "Wizarding Currency"],

                ]
CURRENCYLISTLOOKUP: list[str] = ["USD", "EUR", "GBP", "JPY", "CNY", "RUB", "INR", "AUD", "CAD", "CHF", "NZD", "ZAR", "SEK", "NOK", "DKK", "HKD", "SGD", "KRW", "MXN", "WIZ"]
class CashRegister:
    def __init__(self, **kwargs) -> None:
        self.currency_code: str = kwargs.get("currency_code", "USD")
        assert self.currency_code in CURRENCYLISTLOOKUP, f"Invalid currency code: {self.currency_code: str}"
        lookup_index: int = CURRENCYLISTLOOKUP.index(self.currency_code)
        self.currency_strings: list = CURRENCYLIST[lookup_index]
        self.total: float = 100.0
        self.bill_partitions: list[int] = kwargs.get("bill_partitions") if kwargs.get("bill_partitions") is not None else [100, 50, 20, 10, 5, 1] # type: ignore
        assert isinstance(self.bill_partitions, list), f"Bill partitions must be a list: {self.bill_partitions: list}"
        self.coin_partitions: list[float] = kwargs.get("coin_partitions") if kwargs.get("coin_partitions") is not None else [0.50, 0.25, 0.10, 0.05, 0.01] # type: ignore
        assert isinstance(self.coin_partitions, list), f"Coin partitions must be a list: {self.coin_partitions: list}"
        for i in self.bill_partitions:
            self.bill_partitions[self.bill_partitions.index(i)] = round(i, 2)
        for i in self.coin_partitions:
            self.coin_partitions[self.coin_partitions.index(i)] = round(i, 2)
        for partition in self.bill_partitions + self.coin_partitions:
            if partition < 0: raise ValueError("Partition values must be non-negative")
            setattr(self, f"partition_{str(partition).replace('.', '_')}_stack", [])
            setattr(self, f"partition_{str(partition).replace('.', '_')}_count", 0)
        # Testing Defaults
        self.partition_50_count: int = 1
        self.partition_50_stack: list[float] = [50.0]
        self.partition_20_count: int = 2
        self.partition_20_stack: list[float] = [20.0, 10.0]
        self.partition_10_count: int = 0
        self.partition_10_stack: list[float] = []
        self.partition_5_count: int = 1
        self.partition_5_stack: list[float] = [10.0]
        self.partition_1_count: int = 4
        self.partition_1_stack: list[float] = [2.0]
        self.partition_0_50_count: int = 1
        self.partition_0_50_stack: list[float] = [0.50]
        self.partition_0_25_count: int = 1
        self.partition_0_25_stack: list[float] = [0.25]
        self.partition_0_10_count: int = 1
        self.partition_0_10_stack: list[float] = [0.10]
        self.partition_0_05_count: int = 2
        self.partition_0_05_stack: list[float] = [0.05, 0.05]
        self.partition_0_01_count: int = 5
        self.partition_0_01_stack: list[float] = [0.01, 0.01, 0.01, 0.01, 0.01]

    # Core of the program is just a float that is added and removed from
    def add_money(self, amount: float) -> None:
        if amount < 0: raise ValueError("Add can't be negative")
        if amount == float("inf"): raise ValueError("Add can't be infinite")
        self.total += round(amount, 2)
        setattr(self, f"partition_{amount}_count", getattr(self, f"partition_{amount}_count") + 1)
        getattr(self, f"partition_{amount}_stack").append(round(amount, 2))
        
    def remove_money (self, remove_amount: float) -> float:
        if remove_amount < 0: raise ValueError("Remove can't be negative")
        if remove_amount == float("inf"): raise ValueError("Remove can't be infinite")
        if remove_amount > self.total: 
            remove_amount -= round(self.total, 2); self.total = round(0.0, 2); return remove_amount
        self.total -= remove_amount; return 0.0
           
    def get_actual_money(self, checklist=None) -> float:
        checking_sum = 0.0
        if checklist is None: checklist = self.bill_partitions + self.coin_partitions
        for arg in checklist:
            for item in getattr(self, f"partition_{str(arg)}_stack"):
                checking_sum += float(item)
        return checking_sum

    def get_percieved_money(self, checklist = None) -> float:
        checking_sum = 0.0
        if checklist is None: checklist = self.bill_partitions + self.coin_partitions
        for arg in checklist:
            checking_sum += arg * len(getattr(self, f"partition_{str(arg)}_stack")) # Potential Error Point, I believe pylance is overreacting here though
        return checking_sum
    
sample_cash_register = CashRegister(currency_code="USD", 
                                    bill_partitions=[100, 50, 20, 10, 5, 1], 
                                    coin_partitions=[0.50, 0.25, 0.10, 0.05, 0.01])

def main():
    try:
        while len(sys.argv) < 4: sys.argv.append("")
        match sys.argv[1].lower():
            case "get":
                assert sys.argv[2] in ["actual", "percieved"], f'Invalid argument: second argument must be "actual" or "percieved"'
                assert sys.argv[3] == None or (sys.argv[3].startswith("[") and sys.argv[3].endswith("]")), f'Invalid argument: third argument must be a list of floats or ints'
                if sys.argv[3]: sys.argv[3] = [float(x) for x in (sys.argv[3].strip("[]").split(","))] # type: ignore
                if isinstance(sys.argv[3], list) and sys.argv[2] == "actual": print(sample_cash_register.get_actual_money(sys.argv[3]))
                if sys.argv[2] == "actual": print(sample_cash_register.get_actual_money())
                if isinstance(sys.argv[3], list) and sys.argv[2] == "percieved": print(sample_cash_register.get_percieved_money(sys.argv[3]))
                if sys.argv[2] == "percieved": print(sample_cash_register.get_percieved_money())
                sys.exit(0)

            case "set":
                try:
                    sys.argv[2] = float(sys.argv[2]) # type: ignore
                    assert sys.argv[2] > 0, f'Invalid argument: second argument must be a positive number'
                    if sys.argv[2] == float("inf"): raise ValueError("Set can't be infinite")
                except TypeError: 
                    print("Second Argument of set must be a positive number and not infinite")
                    sys.exit(1)
                except ValueError:
                    print("Second Argument of set must be a positive number and not infinite")
                    sys.exit(1)
                for unit in sample_cash_register.bill_partitions + sample_cash_register.coin_partitions: setattr(sample_cash_register, f"partition_{str(unit)}_count", 0)
                sample_cash_register.total = round(0.0, 2)
                for unit in sample_cash_register.bill_partitions + sample_cash_register.coin_partitions:
                    while sys.argv[2] - unit >= round(0.0, 2):
                        print(unit)
                        sample_cash_register.add_money(round(unit, 2))
                        sample_cash_register.total = round(sample_cash_register.total, 2)
                        sys.argv[2] -= unit # type: ignore
                    print(sample_cash_register.total)
                print(f"Total set to {sample_cash_register.total}")
                if sys.argv[2] > 0:
                    print(f"Warning: {sys.argv[2]} was left over after setting total, this may be due to rounding errors or insufficient denominations")
                    sys.exit(1)
                sys.exit(0)

            case "add": 
                adder_count: float = 0.0
                sys.argv[2] = float(sys.argv[2]) # type: ignore
                assert sys.argv[2] >= 0, f'Invalid argument: second argument must be a positive float'
                if sys.argv[2] == float("inf"): raise ValueError("Add can't be infinite")
                for unit in sample_cash_register.bill_partitions + sample_cash_register.coin_partitions:
                    while sys.argv[2] - unit >= 0:
                        sample_cash_register.add_money(unit)
                        adder_count += unit
                        sys.argv[2] -= unit # type: ignore
                print(f"Added {adder_count} to total, new total is {sample_cash_register.total}")
                if sys.argv[2] > 0:
                    print(f"Warning: {sys.argv[2]} was left over after adding, this may be due to rounding errors or insufficient denominations")
                    sys.exit(1)
                sys.exit(0)

            case "remove": 
                sys.argv[2] = float(sys.argv[2]) # type: ignore
                assert sys.argv[2] > 0, f'Invalid argument: second argument must be a positive float'
                if sys.argv[2] == float("inf"): raise ValueError("Remove can't be infinite")
                current_denomination: int|float = 0
                remaining_debt: float = sys.argv[2] #gonna need to review all sys argv types later
                for current_denomination in sample_cash_register.bill_partitions + sample_cash_register.coin_partitions: # order these just in case enduser goes out of order
                    while remaining_debt > current_denomination and getattr(sample_cash_register, f"partition_{str(current_denomination)}_count") > 0:
                        sample_cash_register.remove_money(current_denomination)
                        remaining_debt -= current_denomination
                        setattr(sample_cash_register, f"partition_{str(current_denomination)}_count", getattr(sample_cash_register, f"partition_{str(current_denomination)}_count") - 1)
                        getattr(sample_cash_register, f"partition_{str(current_denomination)}_stack").pop()
                if remaining_debt < 0: print(remaining_debt)
                if remaining_debt > 0:
                    print(f"Tried removing {sys.argv[2]} from total, new total is {sample_cash_register.total}, but {remaining_debt} was left over")
                else:
                    print(f"Removed {sys.argv[2]} from total, new total is {sample_cash_register.total}")
                sys.exit(0)

            case "adjust":
                sys.argv[2] = float(sys.argv[2]) # type: ignore
                assert float(sys.argv[2]) is float, f'second argument must be a float'
                if sys.argv[2] < 0: 
                    sys.argv[1] = "remove"
                    sys.argv[2] = abs(sys.argv[2]) # type: ignore
                elif sys.argv[2] > 0:
                    sys.argv[1] = "add"
                else:
                    print("No adjustment made, value is 0")
                    sys.exit(0)
                main()
            
            case _:
                print("Usage: python main.py 'command_string'")
                print('"get": argv[2] should be "actual" or "percieved" based on if you want to have each bill or coin checked in their stack')
                print('"set": argv[2] should be a positive float to set actual total to')
                print('"add": argv[2] should be a positive float to add to the total')
                print('"remove": argv[2] should be a positive float to remove from the total')
                print('"adjust": argv[2] should be a float to adjust the total by, can be negative')
                sys.exit(0)
    except IndexError:
        print("Usage: python main.py 'command_string'")
        print('"get": argv[2] should be "actual" or "percieved" based on if you want to have each bill or coin checked in their stack')
        print('"set": argv[2] should be a positive float to set actual total to')
        print('"add": argv[2] should be a positive float to add to the total')
        print('"remove": argv[2] should be a positive float to remove from the total')
        print('"adjust": argv[2] should be a float to adjust the total by, can be negative')
        sys.exit(0)
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)
