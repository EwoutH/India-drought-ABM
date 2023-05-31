from dataclasses import dataclass
import pandas as pd
import numpy as np

crop_df_local = pd.read_csv('../analysis/crops/agg_data.csv', index_col=0)

@dataclass
class ModelParameters:
    num_farmers: int = 10
    crop_df = crop_df_local


def get_weighted_crop_choice():
    # Create a list of crop percentages, to draw from. Do this based on the Area (1000 ha) column, which contains absolute numbers.
    p = crop_df_local["Area (1000 ha)"]
    p = p.fillna(0)
    crop_probabilities = p / p.sum()
    # Generate a weighted random choice:
    random_crop = np.random.choice(p.index, p=crop_probabilities)
    return random_crop


def calculate_gini(model):
    agent_money = [agent.money for agent in model.schedule.agents]
    x = sorted(agent_money)
    N = model.num_farmers
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B
