
import pandas as pd

import shipflowmotionshelpers.shipflowmotionshelpers as helpers

def show():

    file_paths = [
    '../../data/external/kvlcc2_rolldecay_0kn',
    '../../data/external/kvlcc2_rolldecay_15-5kn',
    ]
    df_parameters = pd.DataFrame()
    df_parameters =  helpers.load_parameters(file_path=file_paths)
    parameters = df_parameters.iloc[-1]

    interesting = [
    'title',
    'LPP',
    'B',
    'ZCG',
    'KXX',
    'S',
    'V',
    'dens',
    'ta',
    'tf',
    ]
    table_parameters = pd.DataFrame(parameters[interesting]).transpose()
    return table_parameters