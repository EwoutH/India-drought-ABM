from data import ModelParameters

class Crop:
    def __init__(self, type):
        self.type = type
        self.growing_season = None  # Rabi or Kharif
        # Sugercane takes both seasons, all others take one.

class Farmland:
    def __init__(self, size, district):
        self.crop = None
        self.size = size
        self.district = district

    def plant(self, crop):
        self.crop = crop

    def harvest(self, year):
        if self.crop is not None:
            # Lookup the crop price from the crop_df
            district_df = ModelParameters.crop_prices_dict[self.district]
            try:
                crop_price = district_df[self.crop.type][year]
            except KeyError:
                print(f"District {self.district} does not grow {self.crop.type}")
            print(crop_price)
            crop_yield = ModelParameters.crop_df.loc[self.crop.type]["Yield (tons/ha)"]
            income = crop_price * 10 * crop_yield * self.size
            self.crop = None
            return income
        return 0

class Loan:
    def __init__(self, amount, interest_rate, duration, lender):
        self.amount = amount
        self.interest_rate = interest_rate
        self.duration = duration
        self.years = 0
        self.lender = lender
        self.final_amount = amount * (1 + interest_rate) ** duration
