import os
import pandas as pd
from collections import OrderedDict


def load_time_series_fnpf(names):
    
    time_series = OrderedDict()
    for name in names:
        file_path = os.path.join('../../data/processed/roll decay KVLCC2','fnpf_%s.csv' % name)
        df = pd.read_csv(file_path, index_col=0)
        time_series[name] = df
        
    return time_series