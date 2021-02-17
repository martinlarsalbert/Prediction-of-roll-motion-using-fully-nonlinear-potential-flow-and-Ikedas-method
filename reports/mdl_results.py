import pandas as pd
import numpy as np

def load():
    
    df_rolldecays = pd.read_csv('../../data/processed/roll decay KVLCC2/model_test_parameters.csv', index_col=0)

    return df_rolldecays

df_rolldecays = load()