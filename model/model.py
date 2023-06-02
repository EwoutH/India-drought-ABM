import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector

from agents import Farmer
from objects import Farmland, Crop
from data import ModelParameters, calculate_gini


class FarmingModel(Model):
    def __init__(self, N=ModelParameters.num_farmers):
        # TODO: Consider adding different districts, Niteesh checks data.
        self.num_farmers = N
        self.year = 0
        self.schedule = BaseScheduler(self)  # Use stage scheduler
        self.current_id = 0
        self.rainfall = None

        self.rainfall_range = (500, 1500)
        self.fraction_borrowers = None  # TODO: Calculate this every step.

        initial_money_range = (100000, 200000)  # in Rs
        cost_of_living_range = (25000, 100000)  # in Rs per year
        # TODO: Use data for farmland sizes https://github.com/EwoutH/India-drought-ABM/blob/main/Data/Farmland/farmland.csv
        farm_size_range = (1, 4)                # in hectares

        for i in range(self.num_farmers):
            farmland = Farmland(size=self.random.uniform(*farm_size_range))
            farmer = Farmer(
                unique_id=self.next_id(),
                model=self,
                farmland=farmland,
                initial_money=self.random.randrange(*initial_money_range),
                cost_of_living=self.random.randrange(*cost_of_living_range)
            )
            self.schedule.add(farmer)

        # Add data collector.
        self.datacollector = DataCollector(
            model_reporters={"Gini": calculate_gini},
            agent_reporters={"Money": "money"}
        )

    def step(self):
        self.random.randrange(*self.rainfall_range)
        self.year += 1
        self.datacollector.collect(self)
        self.schedule.step()

    def rabi(self):
        # Grows with irrigation
        pass

    def karif(self):
        # Grows without irrigation
        pass

# Usage
model = FarmingModel()
for i in range(20):
    model.step()
    print(f"Year {model.year}: Gini = {calculate_gini(model)}")

gini = model.datacollector.get_model_vars_dataframe()
gini.plot()
plt.show()

# Plot the wealth of all farmers
agent_wealth = model.datacollector.get_agent_vars_dataframe()
agent_wealth.reset_index().pivot(index='Step', columns='AgentID', values='Money').plot()
plt.show()
