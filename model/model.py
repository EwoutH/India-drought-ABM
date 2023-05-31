import matplotlib.pyplot as plt

from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector

from agents import Farmer
from objects import Farmland, Crop

def calculate_gini(model):
    agent_money = [agent.money for agent in model.schedule.agents]
    x = sorted(agent_money)
    N = model.num_farmers
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B


class FarmingModel(Model):
    def __init__(self, N, crop_price):
        self.num_farmers = N
        self.crop_price = crop_price
        self.year = 0
        self.schedule = BaseScheduler(self)
        self.current_id = 0

        money_range = (100, 200)
        cost_of_living_range = (10, 20)

        for i in range(self.num_farmers):
            farmland = Farmland()
            farmer = Farmer(
                unique_id=self.next_id(),
                model=self,
                farmland=farmland,
                crop_price=self.crop_price,
                initial_money=self.random.randrange(*money_range),
                cost_of_living=self.random.randrange(*cost_of_living_range)
            )
            self.schedule.add(farmer)

        # Add data collector.
        self.datacollector = DataCollector(
            model_reporters={"Gini": calculate_gini},
            agent_reporters={"Money": "money"}
        )

    def step(self):
        self.year += 1
        self.datacollector.collect(self)
        self.schedule.step()

# Usage
model = FarmingModel(10, 100)
for i in range(10):
    model.step()
    print(f"Year {model.year}: Gini = {calculate_gini(model)}")

gini = model.datacollector.get_model_vars_dataframe()
gini.plot()
plt.show()
