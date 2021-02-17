import pandas as pd
from src.df_to_latex import LateXTable


def show():
    
    df_ikeda_sections = pd.read_csv('../../data/processed/ikeda_sections_R.csv', index_col=0)

    interesting = ['model',
                   'omega_hat',
                   'phi_a',
                   'B_E_star_hat',
                   'B_W+B_F',
                   'L_pp',
                   'beam',
                   'T',
                   'sigma',
    #               'OG/d',
                   'R',
                   'a_1',
                   'a_3', 
                   'C_r']

    section_table = df_ikeda_sections[interesting].copy()
    rename = {
        'omega_hat':r'$\hat{\omega}$',
        'phi_a':r'$\phi_a$',
        'B_E_star_hat':r'$\hat{B_E}^*$',
        'L_pp':r'$L_{pp}$',
        'beam':r'$beam$',
        'T_s':r'$T_s$',
        'sigma':r'$\sigma$',
    #    'OG/d':r'$\frac{OG}{d}$',
        'R':r'$R_b$',
        'a_1':r'$a_1$',
        'a_3':r'$a_3$',
        'C_r':r'$C_r$',

    }
    section_table.rename(columns=rename, inplace=True)

    lt = LateXTable(section_table, print_latex_longtable=False)

    return lt