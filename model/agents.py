from mesa import Agent
from objects import FarmLand, Crop, IrrigationSystem

# Define a Farmer agent
class Farmer(Agent):


    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.name = f"Farmer_{unique_id}"

        self.money: float
        self.yearly_living_expenses: float
        self.lands: list[FarmLand] = []
        self.neighbors = None

    def select_and_sow_crops(self):
        pass

    def invest(self, type, item):
        pass

    def harvest_crops(self):
        pass

    def borrow_money(self, lender, amount):
        pass

    def lend_money_out(self, borrower, amount):
        pass

    def spread_information_to_network(self, information):
        pass

    def step(self):
        # Define farmer's behaviours and actions here
        pass


# Define a Money Lender agent
class MoneyLender(Agent):
    def __init__(self, unique_id, model, liquidity, total, current_customers):
        super().__init__(unique_id, model)
        self.name = f"MoneyLender_{unique_id}"
        self.offering = {'interest_rate': None, 'duration': None, 'maximum_amount': None}
        self.liquidity = liquidity
        self.total = total
        self.current_customers = current_customers

    def update_strategy(self):
        pass

    def accept_decline_request(self, borrower, amount):
        pass

    def revise_offers(self):
        pass

    def step(self):
        # Define money lender's behaviours and actions here
        pass
