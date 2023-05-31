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

        money_range = (100, 200)

        for i in range(self.num_farmers):
            farmland = Farmland()
            farmer = Farmer(
                unique_id=self.next_id(),
                model=self,
                farmland=farmland,
                crop_price=self.crop_price,
                initial_money=self.random.randrange(*money_range)
            )
            self.schedule.add(farmer)

    def step(self):
        self.year += 1
        self.schedule.step()

# Usage
model = FarmingModel(10, 100)
for i in range(10):
    model.step()
