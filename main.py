import sys
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
        self.currency_strings: list = CURRENCYLIST[CURRENCYLISTLOOKUP.index(self.currency_code: str): int]
        self.total: float = 0.0
        self.bill_partitions: list = kwargs.get("bill_partitions") if kwargs.get("bill_partitions") is not None else [100, 50, 20, 10, 5, 1] 
        assert self.bill_partitions is list, f"Bill partitions must be a list: {self.bill_partitions: list}"
        self.coin_partitions: list = kwargs.get("coin_partitions") if kwargs.get("coin_partitions") is not None else [0.50, 0.25, 0.10, 0.05, 0.01]
        assert self.coin_partitions is list, f"Coin partitions must be a list: {self.coin_partitions: list}"
        for partition in self.bill_partitions + self.coin_partitions:
            if partition < 0: raise ValueError("Partition values must be non-negative")
            setattr(self, f"partition_{partition}_stack", [])
            setattr(self, f"partition_{partition}_count", 0)


    # Core of the program is just a float that is added and removed from
    def add_money(self, amount: float) -> None:
        if amount < 0: raise ValueError("Add can't be negative")
        self.total += amount
        
    def remove_money (self, remove_amount: float) -> float:
        if remove_amount < 0: raise ValueError("Remove can't be negative")
        
        if remove_amount > self.total: 
            remove_amount -= self.total; self.total = 0; return remove_amount
        self.total -= remove_amount; return 0.0

    def set_money(self, set_amount: float) -> None:
        if set_amount < 0: raise ValueError("Set can't be negative")
        self.total = set_amount

    def adjust_money(self, adjust_amount: float) -> None: self.total += adjust_amount

    def get_actual_money(self, *args: None | float) -> float:
        checking_sum = 0.0
        for arg in args():
            for item in getattr(f"partition_{str(arg)}_stack"):
                checking_sum += float(item)
        return checking_sum

    def get_percieved_money(self, *args: float | int) -> float:
        checking_sum = 0.0
        if args is tuple():
            args = tuple(self.bill_partitions + self.coin_partitions)
        for arg in args:
            checking_sum += arg * len(getattr(f"partition_{str(arg)}_stack")) # Potential Error Point, I believe pylance is overreacting here though
        return checking_sum
    
sample_cash_register = CashRegister(currency_code="USD", bill_partitions=[100, 50, 20, 10, 5, 1], coin_partitions=[0.50, 0.25, 0.10, 0.05, 0.01])

if __name__ == "__main__":
    match sys.argv[1]:
        case "get":
            assert sys.argv[2] in ["actual", "percieved"], f'Invalid argument: second argument must be "actual" or "percieved"'
            assert sys.argv[3] is list or sys.argv[3] is None, f'Invalid argument: third argument must be a list of floats or None'
            if sys.argv[3] is list and sys.argv[2] is "actual": print(sample_cash_register.get_actual_money(argv[3]))
            if sys.argv[3] is not list and sys.argv[2] is "actual": print(sample_cash_register.get_actual_money())

        case _:
            print("Usage: python main.py 'command_string'")
            print('"get": argv[2] should be "actual" or "percieved" based on if you want to have each bill or coin checked in their stack')
            print('"set": argv[2] should be a positive float to set actual total to')
            print('"add": argv[2] should be a positive float to add to the total')
            print('"remove": argv[2] should be a positive float to remove from the total')
            print('"adjust": argv[2] should be a float to adjust the total by, can be negative')
            sys.exit(0)

