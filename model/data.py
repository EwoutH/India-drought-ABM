from dataclasses import dataclass
import pandas as pd
import numpy as np
from random import gauss

crop_df_local = pd.read_csv('../analysis/crops/agg_data.csv', index_col=0)
farm_df_local = pd.read_csv('../Data/Farmland/farmland_clean.csv', index_col=0)
land_value_df_local = pd.read_csv('../Data/csv_data/land_value.csv', index_col=0)

p = crop_df_local["Area (1000 ha)"]
p = p.fillna(0)
p = p.sort_values(ascending=False)[:7]  # Keep the 7 highest area crops
crop_probabilities = p / p.sum()

@dataclass
class ModelParameters:
    num_farmers: int = 25
    initial_year: int = 2017
    run_length: int = 30
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
        for i in range(run_length):
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


def calculate_gini(model):
    agent_money = [agent.money for agent in model.schedule.agents]
    x = sorted(agent_money)
    N = model.num_farmers
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B
