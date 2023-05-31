from mesa import Model
from mesa.time import BaseScheduler

from agents import Farmer
from objects import Farmland, Crop

class FarmingModel(Model):
    def __init__(self, N, crop_price):
        self.num_farmers = N
        self.crop_price = crop_price
        self.year = 0
        self.schedule = BaseScheduler(self)
        self.current_id = 0
        for i in range(self.num_farmers):
            farmland = Farmland()
            farmer = Farmer(self.next_id(), self, farmland, self.crop_price)
            self.schedule.add(farmer)

    def step(self):
        self.year += 1
        self.schedule.step()

# Usage
model = FarmingModel(10, 100)
for i in range(10):
    model.step()
