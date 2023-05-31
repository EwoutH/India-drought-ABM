class Crop:
    def __init__(self, price):
        self.price = price


class Farmland:
    def __init__(self):
        self.crop = None

    def plant(self, crop):
        self.crop = crop

    def harvest(self):
        if self.crop is not None:
            income = self.crop.price
            self.crop = None
            return income
        return 0
