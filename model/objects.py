from data import ModelParameters
from collections import Counter
import random


class Crop:
    def __init__(self, type):
        self.type = type
        self.growing_season = None  # Rabi or Kharif
        # Sugercane takes both seasons, all others take one.


class Farmland:
    def __init__(self, size, district, n_parcels):
        self.size = size
        self.district = district
        self.n_parcels = n_parcels
        self.parcels = [Parcel(size / n_parcels) for _ in range(n_parcels)]
        self.crop_counter = Counter()

    def plant(self, new_crop, n_parcels=1, replace_pref=[]):
        # TODO: Simply by only updating one parcel, and one replace_pref value
        replace_pref = [crop_type for crop_type in replace_pref if crop_type in self.parcels]
        replace_pref_index = 0
        while n_parcels > 0:
            current_crops = set(parcel.crop for parcel in self.parcels)
            # Select the first crop out replace_pref that's already planted
            while replace_pref_index < len(replace_pref):
                if replace_pref[replace_pref_index] in current_crops:
                    replace_crop = replace_pref[replace_pref_index]
                    break
                replace_pref_index += 1
            else:
                replace_crop = random.choice(list(current_crops))
            # Select a random parcel with that crop
            parcel = random.choice([parcel for parcel in self.parcels if parcel.crop == replace_crop or parcel.crop == None])
            # Plant the crop
            parcel.crop = new_crop
            n_parcels -= 1
        self.crop_counter = Counter([parcel.crop for parcel in self.parcels])


    def harvest(self, year):
        income = 0
        district_df = ModelParameters.crop_prices_dict[self.district]
        for parcel in self.parcels:
            if parcel.crop is not None:
                # Lookup the crop price from the crop_df
                crop_price = district_df[parcel.crop][year]
                # TODO: Calculate crop yield for each parcel based on rain-yield regression (including rain lookup, and irrigation)
                crop_yield = ModelParameters.crop_df.loc[parcel.crop]["Yield (tons/ha)"]
                income += crop_price * 10 * crop_yield * parcel.size  # TODO: Here's some unit conversion, make it excplicit
        return income

class Parcel:
    def __init__(self, size):
        self.size = size
        self.crop = None

class Loan:
    def __init__(self, amount, interest_rate, duration, borrower, lender=None, interest_rate_after_duration=None, collateral_used=0):
        self.amount = amount
        self.interest_rate = interest_rate
        self.duration = duration
        self.years = 0
        self.borrower = borrower
        self.lender = lender
        self.interest_rate_after_duration = (
            interest_rate if interest_rate_after_duration is None else interest_rate_after_duration
        )
        self.current_interest_rate = interest_rate
        self.collateral_used = collateral_used

    def update(self):
        # TODO: Validate order of steps here, also considering year = 0
        self.years += 1
        if self.years > self.duration:
            self.current_interest_rate = self.interest_rate_after_duration
        self.amount *= 1 + self.current_interest_rate

    def pay_back(self, pay_amount):
        # TODO: Check how collateral should be reduced
        self.amount -= pay_amount
        if self.amount <= 0:
            if self.lender is not None:
                self.lender.money += self.amount
            self.amount = 0
            self.borrower.loans.remove(self)
            del self

class JGL:
    def __init__(self, max_size, type, district):
        self.members = []
        self.max_size = max_size
        self.type = type
        self.district = district
