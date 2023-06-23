import random

from mesa import Agent
from objects import Crop, Farmland, Loan
from data import ModelParameters, get_weighted_crop_choice

class Farmer(Agent):
    def __init__(self, unique_id, model, type, district, farmland, initial_money, cost_of_living):
        super().__init__(unique_id, model)
        self.type = type
        self.district = district
        self.farmland = farmland
        self.land_value = random.uniform(ModelParameters.land_value_df.loc[district]["land_min_value"], ModelParameters.land_value_df.loc[district]["land_max_value"])
        self.money = initial_money
        self.income = 0
        self.value = self.money
        self.cost_of_living = cost_of_living
        self.neighbours = []
        self.loans = []
        self.will_lend: bool
        self.years_in_debt = 0
        self.years_in_increasing_debt = 0
        self.jgl = None  # JGL reference

    def step(self):
        value_last_year = self.value
        self.will_lend = self.random.random() < self.model.lend_probability
        self.money -= self.cost_of_living

        self.harvest_crops()
        # Select one random crop to plant. TODO: Make this neighbour dependent.
        crop = get_weighted_crop_choice()
        self.plant_crops()

        if self.money < 0:
            self.borrow_money(amount_to_borrow=-self.money)
        self.pay_back_loans()

        # Update value by subtracting loans from money, and debt status
        self.value = self.money - sum([loan.amount for loan in self.loans])
        if self.value < 0:
            self.years_in_debt += 1
            if self.value < value_last_year:
                self.years_in_increasing_debt += 1
            else:
                self.years_in_increasing_debt = 0
        else:
            self.years_in_debt = 0

    def harvest_crops(self):
        income = self.farmland.harvest(year=self.model.year)
        self.income = income
        self.money += income
        print(f"Farmer {self.unique_id} earned {income:.0f}, now has {self.money:.0f}")

    def plant_crops(self):
        # TODO: Improve crop selection
        crop = get_weighted_crop_choice()
        self.farmland.plant(crop)

    def borrow_money(self, amount_to_borrow, max_interest_rate=2.0):
        borrowed = 0
        # First, check neighbours:
        interest_rate = 0
        duration = 1
        # Create list of neighbours sorted by money (ask richest first)
        for neighbour in self.neighbours:
            if neighbour.will_lend and neighbour.money > 0:
                # TODO: Incorporate trust or reputation of neighbour
                max_willing_to_borrow = max(0, (neighbour.money - neighbour.cost_of_living * 1.5))
                amount_to_borrow_now = min(amount_to_borrow, max_willing_to_borrow)

                loan = Loan(amount_to_borrow_now, interest_rate, duration, self, neighbour)
                neighbour.money -= amount_to_borrow_now
                self.money += amount_to_borrow_now
                self.loans.append(loan)
                borrowed += amount_to_borrow_now
                print(f"Farmer {self.unique_id} borrowed {amount_to_borrow_now:.0f} from farmer {neighbour.unique_id}")
                if borrowed >= amount_to_borrow:
                    return

        # Second, check Nationalized banks. Lowest rate of interest (10-14%), show collatoral (60%) or income.
        # Calculate max loan amount from income
        # TODO: First take land as collatoral, then income (for slightly lower interest rate)
        income_financing = (self.income - self.cost_of_living)  # TODO: Take average income over 3 years

        max_collateral = self.farmland.size * self.model.land_value * 0.6
        collateral_in_loans = sum([loan.collateral_used for loan in self.loans])
        available_collateral = max(0, (max_collateral - collateral_in_loans))

        amount_to_borrow_now = min(amount_to_borrow, (income_financing + available_collateral))
        collateral_used = max(0, (amount_to_borrow_now - income_financing))

        interest_rate = random.uniform(0.10, 0.14)
        interest_rate_after_duration = interest_rate * 1.5
        duration = random.randint(1, 3)

        loan = Loan(amount_to_borrow_now, interest_rate, duration, self, interest_rate_after_duration=interest_rate_after_duration, collateral_used=collateral_used)
        self.money += amount_to_borrow_now
        self.loans.append(loan)
        borrowed += amount_to_borrow_now
        print(f"Farmer {self.unique_id} borrowed {amount_to_borrow_now:.0f} for {duration} years at {interest_rate:.2%} from bank based on proven income and {collateral_used:.0f} collateral")

        if borrowed >= amount_to_borrow:
            return

        # Third, check microfinance institution. TODO
        # Payed of loans by another member of the JLG, are converted to neighbour loans
        # Who pays back first?

        print(f"Farmer {self.unique_id} hasn't borrowed enough money, still needs {amount_to_borrow - borrowed:.0f}")

    # Pay back as much open loans, until either all loans are paid back, all money is used or the interest rate to lend
    def pay_back_loans(self):
        # Pay back loans with the highest interest rate first (if interest rate is the same, pay back the smallest loan first)
        loans_to_pay_back = sorted(self.loans, key=lambda x: (-x.current_interest_rate, x.amount))
        while self.money > 0 and len(loans_to_pay_back) > 0:
            loan = loans_to_pay_back.pop(0)
            amount_to_pay_back = min(self.money, loan.amount)
            loan.pay_back(amount_to_pay_back)
            self.money -= amount_to_pay_back
            lender_name = f"farmer {loan.lender.unique_id}" if loan.lender is not None else "bank"
            print(f"Farmer {self.unique_id} paid back {amount_to_pay_back:.0f} to {lender_name}, {self.money:.0f} left, {len(self.loans)} loans left (total {sum([loan.amount for loan in self.loans]):.0f})")

# Loading agents:
# - Nationalized banks. Lowest rate of interest (10-14%), show collatoral or income.
# - Microfinance institutions. Higher rate of interest (22% to 27%), network based collatoral (joint liability groups). 40% have access.
# - Neighbors. No rate of interest, no collatoral.
