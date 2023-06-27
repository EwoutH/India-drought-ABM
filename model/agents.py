import random

from mesa import Agent
from collections import Counter
import pandas as pd
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
        for loan in self.loans:
            loan.update()

        self.harvest_crops()
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
        # print(f"Farmer {self.unique_id} earned {income:.0f}, now has {self.money:.0f}")

    def plant_crops(self):
        current_crops = list(Counter([parcel.crop for parcel in self.farmland.parcels]).keys())

        # Calculate the count of each crop among all neighbours
        crop_counts = {crop: 0 for crop in ModelParameters.crop_list}
        for neighbour in self.neighbours:
            for parcel in neighbour.farmland.parcels:
                crop_counts[parcel.crop] += 1
        crop_counts = {crop: count for crop, count in crop_counts.items() if count > 0}

        # print(crop_counts)

        # Get crops that at least 1/3rd of the neighbours have planted
        potential_crops = [crop for crop, count in crop_counts.items() if count > len(self.neighbours) / 3]
        # print(f"Farmer {self.unique_id} has {len(potential_crops)} potential crops to choose from: {potential_crops}")

        # Select the crop with the highest price per hectare
        c_p = pd.Series(self.model.predicted_crop_prices[self.district])
        c_y = pd.Series(ModelParameters.crop_df["Yield (tons/ha)"])

        # TODO: Calculate globally to increase performance
        # Calculate price per hectare
        price_density = c_p * c_y

        if len(potential_crops) > 0:
            price_density_pot = price_density[price_density.index.isin(potential_crops)]
            best_crop = price_density_pot.idxmax()
        else:
            best_crop = random.choice(current_crops)

        worst_crop = price_density[price_density.index.isin(current_crops)].idxmin()

        self.farmland.plant(best_crop, replace_pref=[worst_crop])
        # print(f"Farmer {self.unique_id} planted {best_crop} (replacing {worst_crop})")

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
                # print(f"Farmer {self.unique_id} borrowed {amount_to_borrow_now:.0f} from farmer {neighbour.unique_id}")
                if borrowed >= amount_to_borrow:
                    return

        # Second, check Nationalized banks. Lowest rate of interest (10-14%), show collatoral (60%).
        # Calculate max loan amount from income

        max_collateral = self.farmland.size * self.model.land_value * 0.6
        collateral_in_loans = sum([loan.collateral_used for loan in self.loans])
        available_collateral = max_collateral - collateral_in_loans

        if available_collateral > 0:
            amount_to_borrow_now = min(amount_to_borrow, available_collateral)

            interest_rate = random.uniform(0.10, 0.14)
            interest_rate_after_duration = interest_rate * 1.5
            duration = random.randint(1, 3)

            loan = Loan(amount_to_borrow_now, interest_rate, duration, self, interest_rate_after_duration=interest_rate_after_duration, collateral_used=amount_to_borrow_now)
            self.money += amount_to_borrow_now
            self.loans.append(loan)
            borrowed += amount_to_borrow_now
            # print(f"Farmer {self.unique_id} borrowed {amount_to_borrow_now:.0f} for {duration} years at {interest_rate:.2%} from bank based on collateral")
            if borrowed >= amount_to_borrow:
                return

        # Third, check Nationalized banks. Rate of interest (16-18%), show income.
        income_financing = (self.income - self.cost_of_living) * 0.6
        if income_financing > 0:
            amount_to_borrow_now = min(amount_to_borrow, income_financing)

            interest_rate = random.uniform(0.16, 0.18)
            interest_rate_after_duration = interest_rate * 1.5
            duration = random.randint(1, 3)

            loan = Loan(amount_to_borrow_now, interest_rate, duration, self, interest_rate_after_duration=interest_rate_after_duration)
            self.money += amount_to_borrow_now
            self.loans.append(loan)
            borrowed += amount_to_borrow_now
            print(f"Farmer {self.unique_id} borrowed {amount_to_borrow_now:.0f} for {duration} years at {interest_rate:.2%} from bank based on income")
            if borrowed >= amount_to_borrow:
                print(f"Farmer {self.unique_id} borrowed enough money: {borrowed:.0f}")
                return

        print(f"Farmer {self.unique_id} borrowed {borrowed:.0f} from neighbours and banks, still needs {amount_to_borrow - borrowed:.0f}")

        # Third, check microfinance institution. TODO
        # Payed of loans by another member of the JLG, are converted to neighbour loans
        # Who pays back first? = spread equally among all members
        # TODO: Join JLG when collateral is maxed out
        # TODO: How much can be borrowed by a JLG?
        # Tag as "bankrupt"

        # print(f"Farmer {self.unique_id} hasn't borrowed enough money, still needs {amount_to_borrow - borrowed:.0f}")

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
            # print(f"Farmer {self.unique_id} paid back {amount_to_pay_back:.0f} to {lender_name}, {self.money:.0f} left, {len(self.loans)} loans left (total {sum([loan.amount for loan in self.loans]):.0f})")

# Loading agents:
# - Nationalized banks. Lowest rate of interest (10-14%), show collatoral or income.
# - Microfinance institutions. Higher rate of interest (22% to 27%), network based collatoral (joint liability groups). 40% have access.
# - Neighbors. No rate of interest, no collatoral.
