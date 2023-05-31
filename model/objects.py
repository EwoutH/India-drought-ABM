from data import ModelParameters

class Crop:
    def __init__(self, type):
        self.type = type

class Farmland:
    def __init__(self, size):
        self.crop = None
        self.size = size

    def plant(self, crop):
        self.crop = crop

    def harvest(self):
        if self.crop is not None:
            # Lookup the crop price from the crop_df
            crop_price = ModelParameters.crop_df.loc[self.crop.type]["Price (Rs/quintal)"]
            crop_yield = ModelParameters.crop_df.loc[self.crop.type]["Yield (tons/ha)"]
            income = crop_price * 10 * crop_yield * self.size
            self.crop = None
            return income
        return 0
