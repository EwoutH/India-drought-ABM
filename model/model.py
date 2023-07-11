import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools
import math

from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid

from agents import Farmer
from objects import Farmland, Crop, JGL
from data import ModelParameters, calculate_gini, calculate_number_of_crops, get_farm_size, get_crop_dict, predict_crop_prices, predicted_yield


class FarmingModel(Model):
    def __init__(self, N=ModelParameters.num_farmers):
        self.num_farmers: int = N
        self.avg_neighbours = 4  # Max 8
        self.year: int = ModelParameters.initial_year
        self.run_length: int = ModelParameters.run_length
        self.schedule = BaseScheduler(self)  # Use stage scheduler
        self.current_id: int = 0
        self.rainfall = None
        self.predicted_crop_prices = {}
        self.minimum_cropable_area = 0.4    # in ha (this is 1 Acre)
        self.lend_probability = 0.3
        self.crops_per_farmer_coefficient = 3  # Does not actually represent the average, since many farmers have not enough parcels of land to plant 3 crops.
        self.rainfall_range = (500, 1500)  # TODO: Base on data
        self.land_value = 20000000  # in Rs per ha (TODO)
        self.districts = ModelParameters.districts
        self.jgls = []  # Changed to a list
        self.max_additional_income = 80 * 450   # 80 days of work, 450 Rs per day
        # TODO: Add policy option of 24000 Rs per year per farmer, as UBI

        initial_money_range = (100000, 200000)  # in Rs             TODO: Base on data
        cost_of_living_range = (25000, 100000)  # in Rs per year    TODO: Let depend on income

        # Calculate total grid size
        grid_size = self.num_farmers * 8 // self.avg_neighbours
        # Calculate district size
        district_size = int((grid_size - 4) // 5)  # Size of a district
        district_dim = int(district_size**0.5)  # Dimensions of a district
        self.height = 5 * district_dim + 4  # Total height of the grid
        self.width = district_dim  # Total width of the grid
        while (self.height-4) * self.width < self.num_farmers:
            self.width += 1

        self.grid = SingleGrid(self.width, self.height, torus=False)
        print(f"Created a grid of size {self.width}x{self.height} with {self.num_farmers} farmers")

        for i in range(self.num_farmers):
            farm_size, farmer_type = get_farm_size()
            district = i // (self.num_farmers // 5)

            farmland = Farmland(size=farm_size, district=self.districts[district], n_parcels=max(int(farm_size / self.minimum_cropable_area), 1))
            farmer = Farmer(
                unique_id=self.next_id(),
                model=self,
                type=farmer_type,
                district=self.districts[district],  # Maybe make weighted choice
                farmland=farmland,
                initial_money=self.random.randrange(*initial_money_range),   # TODO: Improve with data
                cost_of_living=self.random.randrange(*cost_of_living_range),  # Will depend on expenditure
            )
            self.schedule.add(farmer)

            # Compute district to place the agent
            min_row = district_dim * district + district    # Min row for this district
            max_row = min_row + district_dim - 1            # Max row for this district
            empty = self.grid.empties
            # Choose an empty cell within the district
            viable_positions = [pos for pos in empty if min_row <= pos[1] <= max_row]
            pos = self.random.choice(viable_positions)
            self.grid.place_agent(farmer, pos)

            self.assign_to_jgl(farmer)

        total_neighbours = 0
        for farmer in self.schedule.agents:
            farmer.neighbours = self.grid.get_neighbors(farmer.pos, moore=True)
            total_neighbours += len(farmer.neighbours)
        print(f"Average number of neighbours: {total_neighbours / self.num_farmers}")

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
        # Update yearly parameters
        self.random.randrange(*self.rainfall_range)
        self.calculate_fraction_borrowers()
        self.lend_probability = 0.3 * self.fraction_borrowers / (1 - self.fraction_borrowers)
        print(f"Fraction of borrowers: {self.fraction_borrowers:.3f}, lending probability: {self.lend_probability:.3f}")
        predict_crop_prices(self)

        self.schedule.step()
        self.year += 1
        self.datacollector.collect(self)  # TODO: Only collect data after certain year (warmup)

    def rabi(self):
        # Grows with irrigation
        pass

    def karif(self):
        # Grows without irrigation
        pass

    def calculate_fraction_borrowers(self):
        # Calculate fraction of farmers who have one or more open loans.
        self.fraction_borrowers = len([farmer for farmer in self.schedule.agents if len(farmer.loans) > 0]) / self.num_farmers

    def assign_to_jgl(self, farmer):
        # TODO: Improve selection of joining JGL. Base one if collateral is maxed out
        if self.random.random() < ModelParameters.jgl_membership[farmer.type]:
            # Filter JGLs by district and type
            district_type_jgls = [jgl for jgl in self.jgls if jgl.district == farmer.district and jgl.type == farmer.type]
            if not district_type_jgls or len(district_type_jgls[-1].members) >= district_type_jgls[-1].max_size:
                # Create new JGL if none exist or the last one is full
                jgl = JGL(max_size=self.random.randint(4, 10), type=farmer.type, district=farmer.district)
                self.jgls.append(jgl)
            else:
                # Add to the last JGL
                jgl = district_type_jgls[-1]
            jgl.members.append(farmer)
            farmer.jgl = jgl


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
