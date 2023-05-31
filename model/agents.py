from mesa import Agent
from objects import Crop, Farmland
class Farmer(Agent):
    def __init__(self, unique_id, model, farmland, crop_price, initial_money, cost_of_living):
        super().__init__(unique_id, model)
        self.farmland = farmland
        self.crop_price = crop_price
        self.money = initial_money
        self.cost_of_living = cost_of_living

    def step(self):
        self.money -= self.cost_of_living
        if self.model.year % 2 == 0:  # plant a crop every 2 years
            crop = Crop(self.crop_price)
            self.farmland.plant(crop)
        else:  # harvest the crop in other years
            income = self.farmland.harvest()
            self.money += income
            print(f"Farmer {self.unique_id} earned {income}, now has {self.money}")