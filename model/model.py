import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector

from agents import Farmer
from objects import Farmland, Crop
from data import ModelParameters, calculate_gini, get_farm_size


class FarmingModel(Model):
    def __init__(self, N=ModelParameters.num_farmers):
        self.num_farmers: int = N
        self.year: int = ModelParameters.initial_year
        self.run_length: int = ModelParameters.run_length
        self.schedule = BaseScheduler(self)  # Use stage scheduler
        self.current_id: int = 0
        self.rainfall = None

        self.rainfall_range = (500, 1500)
        self.fraction_borrowers: float

        initial_money_range = (100000, 200000)  # in Rs
        cost_of_living_range = (25000, 100000)  # in Rs per year

        # Create a dataframe with the chance of each type of farmer.
        p = ModelParameters.farm_df["Number"]
        p = p.drop("Total", axis="index")
        farmer_probabilities = p / p.sum()

        for i in range(self.num_farmers):
            district = np.random.choice(ModelParameters.districts)
            farm_size, farmer_type = get_farm_size()

            farmland = Farmland(size=farm_size, district=district)
            farmer = Farmer(
                unique_id=self.next_id(),
                model=self,
                type=farmer_type,
                district=np.random.choice(ModelParameters.districts),
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
        self.calculate_fraction_borrowers()
        self.year += 1
        self.datacollector.collect(self)
        self.schedule.step()

    def rabi(self):
        # Grows with irrigation
        pass

    def karif(self):
        # Grows without irrigation
        pass

    def calculate_fraction_borrowers(self):
        # Calculate fraction of farmers who have one or more open loans.
        self.fraction_borrowers = len([farmer for farmer in self.schedule.agents if len(farmer.loans) > 0]) / self.num_farmers



# Usage
model = FarmingModel()
for i in range(ModelParameters.run_length):
    model.step()
    print(f"Year {model.year}: Gini = {calculate_gini(model)}")

gini = model.datacollector.get_model_vars_dataframe()
gini.plot()
plt.show()

# Plot the wealth of all farmers
agent_wealth = model.datacollector.get_agent_vars_dataframe()
agent_wealth.reset_index().pivot(index='Step', columns='AgentID', values='Money').plot()
plt.show()
