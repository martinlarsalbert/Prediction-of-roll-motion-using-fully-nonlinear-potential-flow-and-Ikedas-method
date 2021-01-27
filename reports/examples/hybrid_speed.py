import matplotlib.pyplot as plt
import numpy as np
import joblib
from copy import deepcopy

from reports.examples.mdl import plot_amplitudes
import src.visualization.visualize as visualize 
import reports.mdl_results as mdl_results
import src.helpers

best_motions_ikeda = 'kvlcc2_rolldecay_15-5kn_ikeda_dev'

def show_frequency(df_results, amplitudes, amplitudes_motions, ylim=None):
    

    fig,ax=plt.subplots()

    
    df_motions_ikeda = df_results.loc[[best_motions_ikeda]]
    
    for id,row in df_motions_ikeda.iterrows(): 
        df_amplitudes = amplitudes_motions[id].copy()

        df_amplitudes.sort_values(by='phi_a', inplace=True)
        df_amplitudes['phi_a_deg'] = np.rad2deg(df_amplitudes['phi_a'])
        plot_amplitudes(df_amplitudes=df_amplitudes, source='Hybrid', paper_name=row.paper_name,ax=ax)

    id = 21340
    row = mdl_results.df_rolldecays.loc[id]
    plot_amplitudes(df_amplitudes=amplitudes[id], source='model test', paper_name=row.paper_name, ax=ax)

    if not ylim is None:
        ax.set_ylim(ylim)
    
def show_time(models_mdl, models_motions):
    
    id = 21340
    model_mdl = models_mdl[id]
    row = mdl_results.df_rolldecays.loc[id]
    model_hybrid = deepcopy(models_motions[best_motions_ikeda])
    steals = ['C_1A']
    for steal in steals:
        model_hybrid.parameters[steal] = model_mdl.parameters[steal]

    X = model_mdl.X.copy()
    X_pred = model_hybrid.predict(X)

    fig,ax=plt.subplots()
    X['phi_deg'] = np.rad2deg(X['phi'])
    X_pred['phi_deg'] = np.rad2deg(X_pred['phi'])

    X.plot(y='phi_deg', label='Run %i: model test' % row.paper_name, ax=ax)
    X_pred.plot(y='phi_deg', style='--', label='Run %i: Hybrid' % row.paper_name, ax=ax)
    ax.grid(True)
    ax.set_xlabel(r'Time [s]')
    ax.set_ylabel(r'$\phi$ $[deg]$');
    