from agents import Farmer, MoneyLender

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
import networkx as nx

from agents import Farmer
from objects import FarmLand, Crop


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
    def __init__(self, N, avg_farm_size, avg_crops, avg_consumption, avg_expenses):
        # create a graph for farmers and their social network
        G = nx.erdos_renyi_graph(n=N, p=0.1)
        self.grid = NetworkGrid(G)

        self.schedule = RandomActivation(self)

        # Create agents (Farmers)
        for i in range(N):
            a = Farmer(i, self, money=0, land=FarmLand(avg_farm_size, "location", "soil_type", 0, 0, "drip"),
                       network=list(self.grid.get_neighbors(i)), education_level=0, risk_awareness=0, risk_aversion=0)
            self.schedule.add(a)
            self.grid.place_agent(a, i)

            # Assign initial crops to farmers
            for j in range(avg_crops):
                crop = Crop(price_per_quintal=0, sowing_density=0, required_irrigation_type="drip",
                            water_req_func=None, yield_func=None)
                a.crops.append(crop)

        self.datacollector = DataCollector(
            model_reporters={
                "Inequality (GINI)": compute_gini,
                "No. of farmers below the poverty threshold": compute_poverty,
                "Debt/wealth ratio, per farmer": compute_debt_wealth_ratio,
                "No. of farmers": compute_no_of_farmers,
                "Presence/absence of drought risk": compute_drought_risk,
            }
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()


if __name__ == "__main__":
    model = AgriModel(10, 5, 3, 100, 50)
    for i in range(100):
        model.step()
