import joblib
from sklearn import tree
import matplotlib.pyplot as plt
import pandas as pd

import rolldecayestimators.ikeda_naked as ikeda_naked

from reports.examples import KVLCC2_section_table

c_r_tree = joblib.load('../../models/C_r_tree.pkl')

def show():
    
    fig,ax = plt.subplots()
    fig.set_size_inches(8,8)
    #with plt.style.context('paper'):
    tree.plot_tree(c_r_tree, ax=ax, feature_names=[r'$\sigma$', r'$a_1$', r'$a_3$'], rounded=True, fontsize=15);
    

def show_regression():

    ikeda_sections_path = r'../../data/processed/ikeda_sections_R.csv'
    df_ikeda_sections = pd.read_csv(ikeda_sections_path, index_col=0)

    df_ikeda_sections.rename(columns= {
        'B_e_star_hat':'B_E_star_hat',
        'd':'T',
        'w_hat':'omega_hat', 
        'L':'L_pp', 
        'B':'beam', 
        'volume':'Disp', 
    }, inplace=True)

    df_ikeda_sections.rename(columns={
        'T':'T_s',
    }, inplace=True)

    
    ## Pred tree:
    X = df_ikeda_sections[['sigma','a_1','a_3']].copy()
    y_pred = c_r_tree.predict(X)
    data_pred = df_ikeda_sections.copy()
    data_pred['C_r'] = y_pred

    ## Pred Ikeda:
    data2 = df_ikeda_sections.copy()
    ra = 1000
    data2['C_r'] = ikeda_naked.calculate_C_r(bwl=data2.beam,
                          a_1=data2.a_1, a_3=data2.a_3, sigma=data2.sigma, 
                                              H0=data2.H0, d=data2['T_s'], OG=0, 
                          R=data2.R, ra=ra)

    ## plot:
    fig,ax=plt.subplots()
    
    for df in [data2,data_pred,df_ikeda_sections]:
        df[r'$a_3$'] = df['a_3'] 

    key = r'$a_3$'
    
    df_ikeda_sections.sort_values(by=key).plot(x=key, y='C_r', style='x', label='experiment', ax=ax)
    data_pred.sort_values(by=key).plot(x=key, y='C_r', style='-', label='decision tree', ax=ax)
    data2.sort_values(by=key).plot(x=key, y='C_r', style='-', label='ikeda', ax=ax)

    ax.grid(True)
    ax.set_ylabel(r'$C_r$')

    for _,row in df_ikeda_sections.iterrows():
        ax.annotate(row['model'], xy=(row[key],row['C_r']))


def show_KVLCC2_C_r_prediction(include_Rb=True):


    df_kvlcc2 = KVLCC2_section_table.get()
    df_kvlcc2_ = df_kvlcc2.copy()
    OG = df_kvlcc2_['OG/d']*df_kvlcc2_['T']
    ra = 1000
    df_kvlcc2_['C_r'] = ikeda_naked.calculate_C_r(bwl=df_kvlcc2_.beam,
                          a_1=df_kvlcc2_.a_1, a_3=df_kvlcc2_.a_3, sigma=df_kvlcc2_.sigma, 
                                              H0=df_kvlcc2_.H0, d=df_kvlcc2_['T'], OG=OG, 
                          R=df_kvlcc2_.R, ra=ra)

    good_feature_names=['sigma', 'a_1', 'a_3']
    c_r_tree = joblib.load('../../models/C_r_tree.pkl')
    df_kvlcc2['C_r'] = c_r_tree.predict(X=df_kvlcc2[good_feature_names])

    fig,ax=plt.subplots()
    df_kvlcc2.plot(y='C_r', style='g.-', label='decision tree', ax=ax)
    df_kvlcc2_.plot(y='C_r', style='r.-', label='ikeda', ax=ax)
    ax.set_ylabel(r'$C_r$')
    ax.set_xlabel(r'station')
    ax.grid(True)
    ax.legend(loc='upper left')

    if include_Rb:
        df_kvlcc2['R/b'] = df_kvlcc2['R']/df_kvlcc2['beam']
        ax_R_b = ax.twinx()
        ax_R_b.tick_params(axis='y', labelcolor='blue')
        df_kvlcc2.plot(y='R/b', ax=ax_R_b, style='--', label=r'$\frac{R_b}{b}$ $[-]$', color='blue')
        ax_R_b.set_ylim(0,0.3)
        ax_R_b.set_ylabel(r'$\frac{R_b}{b}$ $[-]$', color='blue')
        ax_R_b.legend(loc='upper right')

def show_regression2(include_decision_tree=True):

    ikeda_sections_path = r'../../data/processed/ikeda_sections_R.csv'
    df_ikeda_sections = pd.read_csv(ikeda_sections_path, index_col=0)

    df_ikeda_sections.rename(columns= {
        'B_e_star_hat':'B_E_star_hat',
        'd':'T',
        'w_hat':'omega_hat', 
        'L':'L_pp', 
        'B':'beam', 
        'volume':'Disp', 
    }, inplace=True)

    df_ikeda_sections.rename(columns={
        'T':'T_s',
    }, inplace=True)

    
    ## Pred tree:
    X = df_ikeda_sections[['sigma','a_1','a_3']].copy()
    y_pred = c_r_tree.predict(X)
    data_pred = df_ikeda_sections.copy()
    data_pred['C_r'] = y_pred

    ## Pred Ikeda:
    data2 = df_ikeda_sections.copy()
    ra = 1000
    data2['C_r'] = ikeda_naked.calculate_C_r(bwl=data2.beam,
                          a_1=data2.a_1, a_3=data2.a_3, sigma=data2.sigma, 
                                              H0=data2.H0, d=data2['T_s'], OG=0, 
                          R=data2.R, ra=ra)

    ## plot:
    fig,ax=plt.subplots()
    
    for df in [data2,data_pred,df_ikeda_sections]:
        df[r'$a_3$'] = df['a_3'] 

    
    
    
    #df_ikeda_sections.sort_values(by=key).plot(x=key, y='C_r', style='x', label='experiment', ax=ax)
    if include_decision_tree:
        ax.plot(df_ikeda_sections['C_r'], data_pred['C_r'], 'o', label='decision tree')
    
    ax.plot(df_ikeda_sections['C_r'], data2['C_r'], 'x', label='ikeda')
    ax.plot([df_ikeda_sections['C_r'].min(),df_ikeda_sections['C_r'].max()], [df_ikeda_sections['C_r'].min(),df_ikeda_sections['C_r'].max()],'r-')
    ax.grid(True)
    ax.set_xlabel(r'$C_r $ (experiment)')
    ax.set_ylabel(r'$C_r $ (prediction)')
    ax.legend()

    #for _,row in data_pred.iterrows():
    #    ax.annotate(row['model'], xy=(row['C_r'],0))