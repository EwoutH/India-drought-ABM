import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools

from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector

from agents import Farmer
from objects import Farmland, Crop
from data import ModelParameters, calculate_gini, calculate_number_of_crops, get_farm_size, get_crop_dict


class FarmingModel(Model):
    def __init__(self, N=ModelParameters.num_farmers):
        self.num_farmers: int = N
        self.year: int = ModelParameters.initial_year
        self.run_length: int = ModelParameters.run_length
        self.schedule = BaseScheduler(self)  # Use stage scheduler
        self.current_id: int = 0
        self.rainfall = None
        self.minimum_cropable_area = 0.4    # in ha (this is 1 Acre)
        self.lend_probability = 0.3
        self.crops_per_farmer_coefficient = 3  # Does not actually represent the average, since many farmers have not enough parcels of land to plant 3 crops.


        self.rainfall_range = (500, 1500)

        initial_money_range = (100000, 200000)  # in Rs
        cost_of_living_range = (25000, 100000)  # in Rs per year

        for i in range(self.num_farmers):
            district = np.random.choice(ModelParameters.districts)
            farm_size, farmer_type = get_farm_size()

            farmland = Farmland(size=farm_size, district=district, n_parcels=max(int(farm_size / self.minimum_cropable_area), 1))
            farmer = Farmer(
                unique_id=self.next_id(),
                model=self,
                type=farmer_type,
                district=np.random.choice(ModelParameters.districts),  # Maybe make weighted choice
                farmland=farmland,
                initial_money=self.random.randrange(*initial_money_range),   # TODO: Improve with data
                cost_of_living=self.random.randrange(*cost_of_living_range)  # Will depend on expenditure
            )
            self.schedule.add(farmer)

        average_number_of_farmland_parcels = np.mean([farmer.farmland.n_parcels for farmer in self.schedule.agents])
        for farmer in self.schedule.agents:
            # Determine the number of crops and how many of each crop
            farmland = farmer.farmland
            max_crops = min(7, farmland.n_parcels)
            n_crops = min(max_crops, 1 + np.random.poisson(self.crops_per_farmer_coefficient * farmland.n_parcels / average_number_of_farmland_parcels))
            crop_dict = get_crop_dict(n_crops=n_crops, n_parcels=farmland.n_parcels)
            # Assign crops to parcels
            flat_crops = itertools.chain.from_iterable([crop] * n for crop, n in crop_dict.items())
            for parcel, crop in zip(farmland.parcels, flat_crops):
                parcel.crop = crop

        # Add data collector.
        self.datacollector = DataCollector(
            model_reporters={"Gini": calculate_gini,
                             "Number of crops": calculate_number_of_crops},
            agent_reporters={"Money": "money",
                             "Years in debt": "years_in_debt",
                             "Years in increasing debt": "years_in_increasing_debt"}
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

agent_wealth.reset_index().pivot(index='Step', columns='AgentID', values='Years in increasing debt').plot()
plt.show()
