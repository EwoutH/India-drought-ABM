from mesa import Agent
from objects import Crop, Farmland, Loan
from data import get_weighted_crop_choice

class Farmer(Agent):
    def __init__(self, unique_id, model, farmland, initial_money, cost_of_living):
        super().__init__(unique_id, model)
        self.farmland = farmland
        self.money = initial_money
        self.cost_of_living = cost_of_living
        self.loans = []

    def step(self):
        self.money -= self.cost_of_living
        if self.farmland.crop is not None:
            self.harvest_crop()
        if self.farmland.crop is None:
            self.plant_crop()
        if self.money < 0:
            self.borrow_money()
        self.pay_back_money()

    def harvest_crop(self):
        income = self.farmland.harvest()
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
            if neighbor.money > 0:
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
