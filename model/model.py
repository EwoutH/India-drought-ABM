from agents import Farmer, MoneyLender

from mesa import Model
from mesa.time import StagedActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
import networkx as nx

from agents import Farmer
from objects import FarmLand, Crop

crop_types = ['Maize', 'Pigeonpea', 'Sorghum', 'Chickpea', 'Groundnut', 'Finger millet']

soil_types_distribution = {
    "Shallow black soils": 1.3,
    "Medium black soils": 20.34,
    "Deep black soils": 10.25,
    "Red sandy soils": 29.27,
    "Mixed red and black soils": 11.82,
    "Red loamy soils": 15.14,
    "Laterite soils and laterite gravely soils": 9.3,
    "Coastal alluvial soils": 2.58
}


def compute_gini(model):
    # Define a function to compute GINI coefficient
    pass


def compute_poverty(model):
    # Define a function to compute no. of farmers below the poverty threshold
    pass


def compute_debt_wealth_ratio(model):
    # Define a function to compute Debt/wealth ratio, per farmer
    pass


def compute_no_of_farmers(model):
    # Define a function to compute No. of farmers
    pass


def compute_drought_risk(model):
    # Define a function to compute Presence/absence of drought risk
    pass


class AgriModel(Model):
    def __init__(self, N, avg_farm_size, avg_farm_lands=1.5, avg_crops, avg_consumption, avg_expenses):
        # create a graph for farmers and their social network
        G = nx.erdos_renyi_graph(n=N, p=0.1)
        self.grid = NetworkGrid(G)

        self.initial_money_range = (500, 2000)
        self.yearly_expenses_range = (avg_expenses - 1000, avg_expenses + 1000)
        self.yearly_consumption_range = (avg_consumption - 1000, avg_consumption + 1000)

        self.avg_farm_lands = avg_farm_lands
        self.farm_land_value_per_acre = 10000

        # List of farming seasons in India
        self.seasons = ["Kharif", "Rabi", "Zaid"]
        self.schedule = StagedActivation(self, stage_list=self.seasons, shuffle=True, shuffle_between_stages=True)

        # Create agents (Farmers)
        for i in range(N):
            a = Farmer(unique_id=i, model=self)

            # Assign initial money and expenses to farmers
            a.money = self.random.randrange(*self.initial_money_range)
            a.yearly_living_expenses = self.random.randrange(*self.yearly_expenses_range)

            # Assign initial farm lands to farmers (poisson distribution)
            for j in range(self.random.poisson(avg_farm_lands)):
                a.lands.append(self.create_farmland())

            self.schedule.add(a)
            self.grid.place_agent(a, i)

        # Get neighbours of each farmer
        for farmer in self.schedule.agents:
            farmer.neighbours = self.grid.get_neighbors(farmer.pos)


        # self.datacollector = DataCollector(
        #     model_reporters={
        #         "Inequality (GINI)": compute_gini,
        #         "No. of farmers below the poverty threshold": compute_poverty,
        #         "Debt/wealth ratio, per farmer": compute_debt_wealth_ratio,
        #         "No. of farmers": compute_no_of_farmers,
        #         "Presence/absence of drought risk": compute_drought_risk,
        #     }
        # )

    # Helper functions
    def create_farmland(self):
        size = self.random.randrange(1, 10)
        farmland = FarmLand(
            size=size,
            monetary_value=self.farm_land_value_per_acre * size,
            irrigation_systems=None
        )
        return farmland

    # Step/stage functions
    def step(self):
        #self.datacollector.collect(self)
        self.schedule.step()

    def kharif(self):
        pass

    def rabi(self):
        pass

    def zaid(self):
        pass


if __name__ == "__main__":
    model = AgriModel(10, 5, 3, 100, 50)
    for i in range(100):
        model.step()
