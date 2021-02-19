
import pandas as pd

import shipflowmotionshelpers.shipflowmotionshelpers as helpers
from src.df_to_latex import LateXTable

def show():

    file_paths = [
    '../../data/external/kvlcc2_rolldecay_0kn',
    '../../data/external/kvlcc2_rolldecay_15-5kn',
    ]
    df_parameters = pd.DataFrame()
    df_parameters = pd.read_csv('../../data/processed/roll decay KVLCC2/fnpf_parameters.csv', index_col=0)
    parameters = df_parameters.iloc[[-1]]

    parameters['draught'] = (parameters['ta'] + parameters['tf'])/2

    interesting = [
    'LPP',
    'B',
    'ZCG',
    'KXX',
    'S',
    'V',
    'dens',
    'draught',
    ]

    table_parameters = parameters[interesting]

    rename = {
        'LPP' : r'$L_{pp}$',
        'B' : r'$beam$',
        'ZCG' : r'$v_{cg}$',
        'KXX' : r'$k_{xx}$',
        'S' : r'$S$',
        'V' : r'$V$',
        'dens' : r'$rho$',
        'draught' : r'$T$',
        
    }
    
    units = {
        'LPP' : r'$[m]$',
        'B' : r'$[m]$',
        'ZCG' : r'$[m]$',
        'KXX' : r'$[m]$',
        'S' : r'$[m^2]$',
        'V' : r'$\left[\frac{m}{s}\right]$',
        'dens' : r'$\left[\frac{kg}{m^3}\right]$',
        'draught' : r'$[m]$',        
    }

    table_parameters = table_parameters.round(decimals=3)
    lt = LateXTable(table_parameters, units=units, rename=rename, caption='KVLCC2 model data', label='kvlcc2_model_data')
    return lt