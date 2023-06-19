from dataclasses import dataclass
import pandas as pd
import numpy as np
from random import gauss
from scipy.stats import lognorm
from collections import Counter

crop_df_local = pd.read_csv('../analysis/crops/agg_data.csv', index_col=0)
farm_df_local = pd.read_csv('../Data/Farmland/farmland_clean.csv', index_col=0)
land_value_df_local = pd.read_csv('../Data/csv_data/land_value.csv', index_col=0)

p = crop_df_local["Area (1000 ha)"]
p = p.fillna(0)
p = p.sort_values(ascending=False)[:7]  # Keep the 7 highest area crops
crop_probabilities = p / p.sum()

@dataclass
class ModelParameters:
    num_farmers: int = 10
    initial_year: int = 2017
    run_length: int = 30
    crop_list = p.index.tolist()
    crop_df = crop_df_local
    farm_df = farm_df_local
    land_value_df = land_value_df_local
    districts = ["Chitradurga", "Bellary", "Davanagere", "Haveri", "Gadag"]

    # Calculate crop prices
    crop_mean = {}
    crop_volatility = {}
    crop_prices_dict = {}

    for district in districts:
        crop_prices = pd.read_csv(f'../Data/crops/district_wise_prices/{district}_inflation_adjusted_prices.csv', index_col=1)
        crop_prices.columns = [col.capitalize() for col in crop_prices.columns]
        crop_prices = crop_prices.drop(["Dist code", "State code", "State name", "Dist name", "Inflation index"], axis=1)
        crop_prices = crop_prices.rename(columns={"Paddy": "Rice"})

        # Calculate the mean and volatility of each crop. Each column is a crop. Save as a dictionary.
        crop_mean[district] = crop_prices.mean()
        crop_volatility[district] = crop_prices.std()

        # Predict the next years: price = mean + volatility * gauss(0, 1). Extend the crop_prices dataframe.
        for i in range(run_length+1):
            gauss_for_each_crop = [gauss(0, 1) for i in range(len(crop_prices.columns))]
            crop_prices.loc[initial_year + i] = crop_mean[district] + crop_volatility[district] * gauss_for_each_crop

        # Save the crop prices dictionary.
        crop_prices_dict[district] = crop_prices

# Set all crop probabilities to 0, if the crop is not grown at all


def get_weighted_crop_choice():
    # Create a list of crop percentages, to draw from. Do this based on the Area (1000 ha) column, which contains absolute numbers.
    # Generate a weighted random choice:
    random_crop = np.random.choice(crop_probabilities.index, p=crop_probabilities)
    return random_crop

def get_crop_dict(n_crops, n_parcels):
    # Create a dictionary of crops, with the number of parcels of land for each crop.
    crops = np.random.choice(crop_probabilities.index, size=n_crops, replace=False)
    crop_dict = {}
    # Select crops from crop_probabilities, and normalize the probabilities to 1.
    new_crop_probabilities = crop_probabilities[crops] / crop_probabilities[crops].sum()

    for _ in range(n_parcels):
        crop = np.random.choice(crops, p=new_crop_probabilities.values)
        if crop in crop_dict:
            crop_dict[crop] += 1
        else:
            crop_dict[crop] = 1
    return crop_dict

def get_farm_size(shape=0.92, loc=0, scale=1.25):
    # Drawing the number from lognormal distribution, capping at 1000, and classifying it.
    farm_size = min(lognorm.rvs(shape, loc, scale), 1000)
    farm_class = classify_size(farm_size)
    return farm_size, farm_class

def classify_size(size):
    # Define the boundaries and the labels
    boundaries = [0, 1, 2, 4, 10, np.inf]
    labels = ['Marginal', 'Small', 'Semi-medium', 'Medium', 'Large']

    # Get the index of the bin that the farm size falls into
    bin_index = np.digitize(size, boundaries) - 1

    # Return the appropriate label
    return labels[bin_index]


def predict_crop_prices(model):
    # For each district, predict next years crop prices for farmers using the mean of the previous 5 years.
    for district in ModelParameters.districts:
        # Get the last 5 years of crop prices. The current year is model.year.
        crop_prices = ModelParameters.crop_prices_dict[district].loc[model.year - 5:model.year - 1]
        # Calculate the mean of the last 5 years, and save it as a dictionary.
        model.predicted_crop_prices[district] = crop_prices.mean().to_dict()


def calculate_gini(model):
    agent_value = [agent.value for agent in model.schedule.agents]
    x = sorted(agent_value)
    N = model.num_farmers
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B

def calculate_number_of_crops(model):
    # Create a Counter with the number of farmers that have a certain number of crops.
    number_of_crops = [len(farmer.farmland.crop_counter) for farmer in model.schedule.agents]
    return Counter(number_of_crops)
