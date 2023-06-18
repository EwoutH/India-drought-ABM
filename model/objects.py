from data import ModelParameters


class Crop:
    def __init__(self, type):
        self.type = type
        self.growing_season = None  # Rabi or Kharif
        # Sugercane takes both seasons, all others take one.


class Farmland:
    def __init__(self, size, district, pieces):
        self.crop = None
        self.size = size
        self.district = district
        self.pieces = pieces

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
    def __init__(self, amount, interest_rate, duration, lender, interest_rate_after_duration=None):
        self.amount = amount
        self.interest_rate = interest_rate
        self.duration = duration
        self.years = 0
        self.lender = lender
        self.interest_rate_after_duration = (
            interest_rate if interest_rate_after_duration is None else interest_rate_after_duration
        )
        self.current_interest_rate = interest_rate

    def update(self):
        # TODO: Validate order of steps here, also considering year = 0
        self.years += 1
        if self.years > self.duration:
            self.current_interest_rate = self.interest_rate_after_duration
        self.amount *= 1 + self.current_interest_rate

    def pay_off(self, amount):
        self.amount -= amount
        if self.amount <= 0:
            self.lender.money += self.amount
            self.amount = 0
            self.lender.loans.remove(self)
            del self
