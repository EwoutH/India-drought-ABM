# Define a FarmLand object
class FarmLand:
    def __init__(self, size, monetary_value, irrigation_systems):
        self.owner: Farmer = None
        self.size: float = size                                  # In acres
        self.monetary_value: int = monetary_value                # In Rupees
        self.irrigation_systems: list[str] = irrigation_systems
        self.current_crop: Crop = None

    def grow_crop(self, crop):
        # Code to simulate crop growth
        pass


# Define a Crop object
class Crop:
    def __init__(self, price_per_quintal, sowing_density, required_irrigation_type, water_req_func, yield_func):
        self.price_per_quintal = price_per_quintal
        self.growth_state: str | None = None
        self.planted: bool = False
        self.grown: bool = False
        self.farm_land_planted: FarmLand
        self.years_old: int = 0
        self.sowing_density: float = sowing_density # In kg/acre
        self.allowed_irrigation_types: list[str]
        self.water_req_func = water_req_func
        self.yield_func = yield_func

    def grow(self, rainfall, time):
        # Code to simulate crop growth
        pass

class IrrigationSystem:
    def __init__(self, type, cost, max_water_supply_rate):
        self.type: str = type
        self.cost: float = cost
        self.max_water_supply_rate: float = max_water_supply_rate
        self.farm_land: FarmLand

