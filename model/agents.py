from mesa import Agent
from objects import Crop, Farmland
from data import get_weighted_crop_choice

class Farmer(Agent):
    def __init__(self, unique_id, model, farmland, initial_money, cost_of_living):
        super().__init__(unique_id, model)
        self.farmland = farmland
        self.money = initial_money
        self.cost_of_living = cost_of_living

    def step(self):
        self.money -= self.cost_of_living
        if self.farmland.crop is not None:
            self.harvest_crop()
        if self.farmland.crop is None:
            self.plant_crop()

    def harvest_crop(self):
        income = self.farmland.harvest()
        self.money += income
        print(f"Farmer {self.unique_id} earned {income:.0f}, now has {self.money:.0f}")

    def plant_crop(self):
        crop = Crop(get_weighted_crop_choice())
        self.farmland.plant(crop)


