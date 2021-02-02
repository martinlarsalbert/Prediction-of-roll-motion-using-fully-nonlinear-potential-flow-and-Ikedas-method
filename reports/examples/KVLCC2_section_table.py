import pandas as pd
from src.helpers import calculate_lewis
from rolldecayestimators import ikeda_naked
from reports import mdl_results    
from src.df_to_latex import LateXTable

def get():

    df_kvlcc2 = pd.read_csv('../../data/interim/kvlcc_areas.csv', sep=';', index_col=0)

    df_kvlcc2.rename(columns={
        'b':'beam',
        't':'T',
        'r_b':'R',
    }, inplace=True)
    df_kvlcc2['sigma']=df_kvlcc2.area/(df_kvlcc2.beam*df_kvlcc2['T'])
    meta_data = mdl_results.df_rolldecays.iloc[0]
    OG = meta_data.TA-meta_data.kg
    df_kvlcc2['OG/d']=OG/df_kvlcc2['T']
    scale_factor = meta_data.scale_factor

    df_kvlcc2['area']/=(scale_factor**2)
    df_kvlcc2['x']/=scale_factor
    df_kvlcc2['T']/=scale_factor
    df_kvlcc2['beam']/=scale_factor
    df_kvlcc2['R']/=scale_factor

    df_ = df_kvlcc2.copy()
    df_.rename(columns={
        'beam':'B',
        'T':'d',
    }, inplace=True)

    a, a_1, a_3, sigma_s, H = calculate_lewis(df_)
    df_kvlcc2['a_1'] = a_1
    df_kvlcc2['a_3'] = a_3
    df_kvlcc2['H0'] = H

    return df_kvlcc2

def show():

    df_kvlcc2 = get()

    interesting = [
    'x',
    'beam',
    'T',
    'sigma',
    'OG/d',
    'R',
    'a_1',
    'a_3']

    section_table = df_kvlcc2[interesting].copy()
    rename = {
        'x':r'$x$',
        'beam':r'$beam$',
        'T':r'$T_s$',
        'sigma':r'$\sigma$',
        'OG/d':r'$\frac{OG}{d}$',
        'R':r'$R_b$',
        'a_1':r'$a_1$',
        'a_3':r'$a_3$',

    }
    section_table.rename(columns=rename, inplace=True)
    lt = LateXTable(section_table.round(decimals=4))
    return lt

