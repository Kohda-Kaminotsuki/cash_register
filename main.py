# Limitations ?
# 1. Inputs can't be complex for demo, sys.argv, unlike actual implementation, is limited to string type 
# and I am very hesitant to use eval() when copilot screams at me every time I try to use it
# 2. Don't have time in the hackathon to implement non-calculator specs without feature locking and risking no time left for debug.

import sys
import math
import ast

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
            formatted = "{:.2f}".format(partition).replace('.', '_')
            setattr(self, f"partition_{str(partition).replace('.', '_')}_stack", [])
            setattr(self, f"partition_{str(partition).replace('.', '_')}_count", 0)
        # Testing Defaults
        self.partition_100_00_count: int = 0
        self.partition_100_00_stack: list[float] = []
        self.partition_50_00_count: int = 1
        self.partition_50_00_stack: list[float] = [50.0]
        self.partition_20_00_count: int = 2
        self.partition_20_00_stack: list[float] = [20.0, 10.0]
        self.partition_10_00_count: int = 0
        self.partition_10_00_stack: list[float] = []
        self.partition_5_00_count: int = 1
        self.partition_5_00_stack: list[float] = [10.0]
        self.partition_1_00_count: int = 4
        self.partition_1_00_stack: list[float] = [2.0, 1.0, 1.0, 1.0]
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
        amount_formatted = ("{:.2f}".format(amount)).replace('.', '_')
        setattr(self, f"partition_{amount_formatted}_count", getattr(self, f"partition_{amount_formatted}_count") + 1)
        getattr(self, f"partition_{amount_formatted}_stack").append(round(amount, 2))
        
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
            formatted_arg = ("{:.2f}".format(arg)).replace('.', '_')
            try:
                for item in getattr(self, f"partition_{formatted_arg}_stack"):
                    checking_sum += float(item)
            except Exception as e:
                print("Error: an item in the checklist is not a valid denomination")
                sys.exit(1)
        return round(checking_sum, 2)

    def get_percieved_money(self, checklist = None) -> float:
        checking_sum = 0.0
        if checklist is None: checklist = self.bill_partitions + self.coin_partitions
        for arg in checklist:
            formatted_arg = ("{:.2f}".format(arg)).replace('.', '_')
            checking_sum += arg * len(getattr(self, f"partition_{formatted_arg}_stack")) # Potential Error Point, I believe pylance is overreacting here though
        return round(checking_sum, 2)
    
sample_cash_register = CashRegister(currency_code="USD", 
                                    bill_partitions=[100, 50, 20, 10, 5, 1], 
                                    coin_partitions=[0.50, 0.25, 0.10, 0.05, 0.01])

def main(adjust_amount=0, adjust_skip=False):
    super_go_horse_trigger = False
    action = ""
    if adjust_skip == "remove":
        adjust_skip = True
        action = "remove"
    elif adjust_skip == "add":
        adjust_skip = True
        action = "add"
    else:
        print("You stand before an open cashregister.")
        print("You feel the power to adjust the contents of the cash register flowing through you.")
        print("[adjust], [get], [set], [add], [remove]")
        while action not in ["adjust", "get", "set", "add", "remove"]: # type: ignore
            action = input("What would you like to do?")
            if action.lower() in ["adjust", "get", "set", "add", "remove"]:
                break
            else:
                print('Invalid action, please choose from "adjust", "get", "set", "add", "remove"')
    try:
        match action.lower(): # type: ignore

            case "get": #gud and done and checked
                get_type = ""
                while get_type.lower() not in ["actual", "percieved"]:
                    get_type = input('Do you want the "actual" or "percieved" amount?')
                    if get_type.lower() in ["actual", "percieved"]:
                        break
                    else:
                        print('Invalid type, please choose "actual" or "percieved"')
                while True:
                    denomination_list = input("Enter a list of denominations to check, empty will check all")
                    try:
                        if denomination_list == "":
                            break
                        denomination_list = ast.literal_eval(denomination_list)
                        if not isinstance(denomination_list, list):
                            print("Error: Denomination list must be a list")
                            continue
                        for denomination in denomination_list:
                            if denomination not in sample_cash_register.bill_partitions + sample_cash_register.coin_partitions:
                                print(f"Error: {denomination} not in list of denominations")
                                super_go_horse_trigger = True
                                break
                        if super_go_horse_trigger:
                            super_go_horse_trigger = False
                            continue
                        break
                    except Exception:
                        print("Error: Invalid denomination list, please enter a list of numbers inside quotes")
                        continue


                if get_type.lower() == "actual":
                    if denomination_list == "":
                        print(sample_cash_register.get_actual_money())
                    else:
                        print(sample_cash_register.get_actual_money(denomination_list))
                else:
                    if denomination_list == "":
                        print(sample_cash_register.get_percieved_money())
                    else:
                        print(sample_cash_register.get_percieved_money(denomination_list))
                sys.exit(0)        

            case "set": #gud and done and checked
                while True:
                    set_amount = input("Enter the amount of cash to have in the register")
                    try:
                        set_amount = ast.literal_eval(set_amount)
                        if isinstance(set_amount, (int, float)):
                            set_amount = float(set_amount)
                            if 0 < set_amount < float("inf"):
                                break
                            else:
                                print("Invalid amount, must be non-negative, non-infinite number")
                        else:
                            print("Invalid amount, must be a number")
                    except Exception as e:
                        print("Invalid input, must be a positive number that isn't infinite")
                set_amount = float(set_amount) # type: ignore
                for unit in sample_cash_register.bill_partitions + sample_cash_register.coin_partitions: 
                    formatted_unit = ("{:.2f}".format(unit)).replace('.', '_')
                    setattr(sample_cash_register, f"partition_{formatted_unit}_count", 0)
                    setattr(sample_cash_register, f"partition_{formatted_unit}_stack", [])
                for unit in sample_cash_register.bill_partitions + sample_cash_register.coin_partitions:
                    while set_amount - unit >= round(0.0, 2):
                        print(unit)
                        sample_cash_register.add_money(round(unit, 2))
                        set_amount -= round(unit, 2) # type: ignore
                print(f"Total set to {sample_cash_register.get_percieved_money()}")
                if round(set_amount, 2) > 0:
                    print(f"Warning: {set_amount} was left over after setting total, this may be due to rounding errors or insufficient denominations")
                    sys.exit(1)
                sys.exit(0)

            case "add": #gud and done and checked
                if adjust_skip == True:
                    add_amount = adjust_amount
                else:
                    while True:
                        try:
                            add_amount = input("Enter how much to add to the total")
                            add_amount = ast.literal_eval(add_amount)
                            if not isinstance(add_amount, (int, float)):
                                print("Invalid amount, must be a number")
                                continue
                            if 0 < add_amount < float("inf"):
                                break
                            else:
                                print("Invalid amount, must be non-negative, non-infinite number")
                                continue
                        except Exception as e:
                            print("Invalid input, must be a positive number that isn't infinite")
                            continue
                add_amount = float(add_amount) # type: ignore
                checklist_type = ""
                adder_count: float = round(0.0, 2)
                while True:
                    checklist = input("Enter a list or dictionary of denominations to add, empty will add from all denominations from highest to lowest")
                    if checklist == "":
                        checklist = sample_cash_register.bill_partitions + sample_cash_register.coin_partitions
                        checklist_type = "list"
                        break
                    elif checklist.startswith("[") and checklist.endswith("]"):
                        checklist = ast.literal_eval(checklist)
                        try:
                            if not isinstance(checklist, list):
                                print("Error: Denomination list must be a list")
                                continue
                        except Exception as e:
                            print("Error: Invalid List, watch that values are numbers")
                            continue
                        try:
                            for denomination in checklist:
                                if denomination not in sample_cash_register.bill_partitions + sample_cash_register.coin_partitions:
                                    print(f"Error: {denomination} not in list of denominations")
                                    super_go_horse_trigger = True
                                    break
                            if super_go_horse_trigger:
                                super_go_horse_trigger = False
                                continue
                            checklist_type = "list"
                            break
                        except Exception as e:
                            print("Error: Invalid List, watch that values are numbers")
                            continue
                    elif checklist.startswith("{") and checklist.endswith("}"):
                        try:
                            checklist = ast.literal_eval(checklist)
                            for key in checklist:
                                float(key)
                        except Exception:
                            print("Error: Invalid Dictionary, watch that keys are strings that can be converted to float, i.e. '1'")
                            continue   
                        for denomination in checklist:
                            if denomination not in sample_cash_register.bill_partitions + sample_cash_register.coin_partitions:
                                print(f"Error: {denomination} not in list of denominations")
                                super_go_horse_trigger = True
                                break
                        if super_go_horse_trigger:
                            super_go_horse_trigger = False
                            continue
                        checklist_type = "dict"
                        break    
                    else:
                        print("Invalid input, must be empty, list, or dictionary of denominations")
                        
                for unit in checklist:
                    unit_formatted = ("{:.2f}".format(unit)).replace('.', '_')
                    while round(add_amount, 2) - round(float(unit), 2) >= 0:
                        if checklist_type == "dict":
                            if checklist[unit] == 0: # type: ignore
                                break
                            else:
                                checklist[unit] -= 1 # type: ignore
                        sample_cash_register.add_money(unit) # type:ignore
                        adder_count += round(float(unit), 2)
                        add_amount -= round(float(unit), 2) # type: ignore
                print(f"Added {adder_count} to total, new total is {sample_cash_register.get_percieved_money()}")
                if add_amount > 0:
                    print(f"Warning: {add_amount} was left over after adding, this may be due to rounding errors or insufficient denominations")
                    sys.exit(1)
                sys.exit(0)

            case "remove": #gud and done and checked
                if adjust_skip == True:
                    remove_amount = adjust_amount
                else:
                    while True:
                        remove_amount = input("Enter how much to remove from the total")
                        remove_amount = ast.literal_eval(remove_amount)
                        if not isinstance(remove_amount, (int, float)):
                            print("Invalid amount, must be a number")
                        if 0 < remove_amount < float("inf"):
                            break
                        else:
                            print("Invalid amount, must be non-negative, non-infinite number")
                remove_amount = remaining_debt = float(remove_amount) # type: ignore
                current_denomination: int|float = 0
                while True:
                    checklist = input("Request specific denominations? If list will try to only use list denominations first, if dictionary will try to fulfill all values for each key from lowest key to highest key, empty will use all denominations from highest to lowest")
                    if checklist == "":
                        checklist = sample_cash_register.bill_partitions + sample_cash_register.coin_partitions
                        break
                    elif checklist.startswith("[") and checklist.endswith("]"):
                        print("A")
                        try:
                            checklist = ast.literal_eval(checklist)
                        except Exception:
                            print("Error: Invalid List, watch that values are numbers")
                            continue
                            
                        print("B")
                        for denomination in checklist:
                            print(f"C: {denomination}")
                            if denomination not in sample_cash_register.bill_partitions + sample_cash_register.coin_partitions:
                                print(f"D: {denomination}")
                                print(f"Error: {denomination} not in list of denominations")
                                print(f"E: {denomination}")
                                super_go_horse_trigger = True
                                break
                                print(f"F: {denomination}")
                        if super_go_horse_trigger:
                            super_go_horse_trigger = False
                            continue
                        break            
                    elif checklist.startswith("{") and checklist.endswith("}"):
                        try:
                            checklist = ast.literal_eval(checklist)
                        except Exception:
                            print("Error: Invalid Dictionary, watch that keys are strings")
                            continue
                        for denomination in checklist:
                            if denomination not in sample_cash_register.bill_partitions + sample_cash_register.coin_partitions:
                                print(f"Error: {denomination} not in list of denominations")
                                super_go_horse_trigger = True
                                break
                        if super_go_horse_trigger:
                            super_go_horse_trigger = False
                            continue
                        break        
                    else:
                        print("Invalid input, must be empty, list, or dictionary of denominations")
                        continue
                if checklist != sample_cash_register.bill_partitions + sample_cash_register.coin_partitions:
                    checklist = sorted(checklist, reverse=True)
                for current_denomination in checklist:
                    if isinstance(checklist, dict):
                        if checklist[current_denomination] == 0:
                            continue
                    curr_denom_formatted = ("{:.2f}".format(current_denomination)).replace('.', '_')
                    while (round(remaining_debt, 2) >= round(float(current_denomination), 2)) and getattr(sample_cash_register, f"partition_{curr_denom_formatted}_count") > 0:
                        sample_cash_register.remove_money(current_denomination)
                        remaining_debt -= round(current_denomination, 2)
                        setattr(sample_cash_register, 
                                f"partition_{curr_denom_formatted}_count", 
                                (getattr(sample_cash_register,
                                f"partition_{curr_denom_formatted}_count") - 1))
                        getattr(sample_cash_register, f"partition_{curr_denom_formatted}_stack").pop()
                        print(round(remaining_debt, 2))
    
                if round(remaining_debt, 2) > 0:
                    checklist = sample_cash_register.bill_partitions + sample_cash_register.coin_partitions
                    for current_denomination in checklist:
                        curr_denom_formatted = ("{:.2f}".format(current_denomination)).replace('.', '_')
                        while (round(remaining_debt, 2) >= round(float(current_denomination), 2)) and getattr(sample_cash_register, f"partition_{curr_denom_formatted}_count") > 0:
                            sample_cash_register.remove_money(current_denomination)
                            remaining_debt -= round(current_denomination, 2)
                            setattr(sample_cash_register, 
                                    f"partition_{curr_denom_formatted}_count", 
                                    (getattr(sample_cash_register,
                                    f"partition_{curr_denom_formatted}_count") - 1))
                            getattr(sample_cash_register, f"partition_{curr_denom_formatted}_stack").pop()
                if round(remaining_debt, 2) > 0:
                    print(f"Tried removing {remove_amount} from total, new total is {sample_cash_register.get_percieved_money()}, but {round(remaining_debt, 2):.2f} was left over")
                    sys.exit(1)
                else:
                    print(f"Removed {remove_amount} from total, new total is {sample_cash_register.get_percieved_money()}")
                sys.exit(0)

            case "adjust": #gud and done and checked
                while True:
                    adjust_amount = input ("Enter how much to adjust the total by, can be negative")
                    try:
                        adjust_amount = float(adjust_amount)
                    except Exception:
                        print("Invalid amount, must be a number")
                        continue
                    if not isinstance(adjust_amount, (int, float)):
                        print("Invalid amount, must be a number")
                    if float("-inf") < adjust_amount < float("inf"):
                        break
                    else:
                        print("Invalid amount, must be non-negative, non-infinite number")
                        continue
                adjust_amount = float(adjust_amount) # type: ignore
                if adjust_amount < 0: 
                    adjust_skip = "remove"
                    adjust_amount = abs(adjust_amount) # type: ignore
                elif adjust_amount > 0:
                    adjust_skip = "add"
                else:
                    print("No adjustment made, value is 0")
                    sys.exit(0)
                main(adjust_amount, adjust_skip) # type: ignore
            
            case _: #gud and done
                print("Usage: python main.py 'command_string'")
                print('"get": argv[2] should be "actual" or "percieved" based on if you want to have each bill or coin checked in their stack')
                print('"set": argv[2] should be a positive float to set actual total to')
                print('"add": argv[2] should be a positive float to add to the total')
                print('"remove": argv[2] should be a positive float to remove from the total')
                print('"adjust": argv[2] should be a float to adjust the total by, can be negative')
                sys.exit(0)
    except IndexError as e:
        print(e)
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