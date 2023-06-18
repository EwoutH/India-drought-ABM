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
        self.cost_of_living = cost_of_living
        self.loans = []
        self.will_lend: bool

    def step(self):
        self.will_lend = self.random.random() < self.model.lend_probability
        self.money -= self.cost_of_living
        if self.farmland.crop is not None:
            self.harvest_crop()
        if self.farmland.crop is None:
            self.plant_crop()
        if self.money < 0:
            self.borrow_money()
        self.pay_back_money()

    def harvest_crop(self):
        income = self.farmland.harvest(year=self.model.year)
        self.money += income
        print(f"Farmer {self.unique_id} earned {income:.0f}, now has {self.money:.0f}")

    def plant_crop(self):
        crop = Crop(get_weighted_crop_choice())
        self.farmland.plant(crop)

    def borrow_money(self):
        amount_to_borrow = -self.money
        interest_rate = self.random.uniform(0.05, 0.15)
        duration = self.random.randrange(1, 5)
        for neighbor in self.model.schedule.agents:
            if neighbor.money > 0 and neighbor.will_lend:
                loan = Loan(amount_to_borrow, interest_rate, duration, neighbor)
                neighbor.money -= amount_to_borrow
                self.money += amount_to_borrow
                self.loans.append(loan)
                print(f"Farmer {self.unique_id} borrowed {amount_to_borrow:.0f} from farmer {neighbor.unique_id}")
                break

    def pay_back_money(self):
        for loan in self.loans:
            if loan.years == loan.duration:
                self.money -= loan.final_amount
                loan.lender.money += loan.final_amount
                self.loans.remove(loan)
                print(f"Farmer {self.unique_id} paid back {loan.final_amount:.0f} to farmer {loan.lender.unique_id}")
            else:
                loan.years += 1



# Loading agents:
# - Nationalized banks. Lowest rate of interest (10-14%), show collatoral or income.
# - Microfinance institutions. Higher rate of interest (22% to 27%), network based collatoral (joint liability groups). 40% have access.
# - Neighbors. No rate of interest, no collatoral.
