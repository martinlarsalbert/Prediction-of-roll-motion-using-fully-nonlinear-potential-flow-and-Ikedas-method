import matplotlib.pyplot as plt
import numpy as np
import joblib
from copy import deepcopy

from reports.examples.mdl import plot_amplitudes
import src.visualization.visualize as visualize 
import reports.mdl_results as mdl_results
import src.helpers
from reports.examples.ikeda import plot_ikeda

best_motions_ikeda = 'kvlcc2_rolldecay_15-5kn_ikeda_dev'
invicid_motions = 'kvlcc2_rolldecay_15-5kn_const_large2'


def show(amplitudes, amplitudes_motions, models_mdl, ylim=None, show_FNPF=False):

    id = 21340
    key = best_motions_ikeda
    df_amplitudes_motions = amplitudes_motions[key].copy()

    row = mdl_results.df_rolldecays.loc[id]
    ikeda_name = 'ikeda_C_r'
    file_name = '%s_%s.pkl' % (id,ikeda_name)
    ikeda = joblib.load('../../models/%s' % file_name)
    model = models_mdl[id]
    df_amplitudes = amplitudes[id]
    phi_as = df_amplitudes_motions['phi_a']

    df = ikeda.calculate(w=model.results['omega0'], fi_a=phi_as)
    df['phi_a'] = phi_as
    df.set_index('phi_a', inplace=True)

    results = src.helpers.unhat(df=df, 
                                Disp=ikeda.volume, 
                                beam=ikeda.beam, 
                                g=ikeda.g, 
                                rho=ikeda.rho)

    ## Replacing the wave damping from motions
    results['B_W'] = df_amplitudes_motions['B_W_model'].values
    results_ = results.copy()
    results_['phi_a_deg'] = np.rad2deg(results_.index)
    results_.set_index('phi_a_deg', inplace=True)
    fig,ax=plt.subplots()
    plot_ikeda(df_amplitudes=amplitudes[id], results=results_, paper_name=row.paper_name, ax=ax)
    
    if show_FNPF:
        plot_amplitudes(df_amplitudes=df_amplitudes_motions, source='FNPF', paper_name=row.paper_name,
                        ax=ax, color='red')

    ax.legend()
    if not ylim is None:
        ax.set_ylim(ylim)

    ax.set_ylabel(r'$B$ $[Nm \cdot s]$')
    ax.set_xlabel(r'$\phi_a$ $[deg]$')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[0:1], labels=labels[0:1], loc='upper left')

def show_frequency(df_results, amplitudes, amplitudes_motions, ylim=None):
    

    fig,ax=plt.subplots()

    
    df_motions_ikeda = df_results.loc[[best_motions_ikeda]]
    
    for id,row in df_motions_ikeda.iterrows(): 
        df_amplitudes = amplitudes_motions[id].copy()

        df_amplitudes.sort_values(by='phi_a', inplace=True)
        df_amplitudes['phi_a_deg'] = np.rad2deg(df_amplitudes['phi_a'])
        plot_amplitudes(df_amplitudes=df_amplitudes, source='hybrid', paper_name=row.paper_name,ax=ax)

    id = 21340
    row = mdl_results.df_rolldecays.loc[id]
    plot_amplitudes(df_amplitudes=amplitudes[id], source='model test', paper_name=row.paper_name, ax=ax)

    if not ylim is None:
        ax.set_ylim(ylim)

    ax.set_ylabel(r'$B$ $[Nm \cdot s]$')
    ax.set_xlabel(r'$\phi_a$ $[deg]$')
    
def show_time(models_mdl, models_motions):
    
    id = 21340
    model_mdl = models_mdl[id]
    row = mdl_results.df_rolldecays.loc[id]
    model_hybrid = deepcopy(models_motions[best_motions_ikeda])
    model_invicid = deepcopy(models_motions[invicid_motions])
    
    steals = ['C_1A']
    for steal in steals:
        model_hybrid.parameters[steal] = model_mdl.parameters[steal]

    X = model_mdl.X.copy()
    X_pred = model_hybrid.predict(X)
    X_pred_inviscid = model_invicid.predict(X)

    fig,ax=plt.subplots()
    X['phi_deg'] = np.rad2deg(X['phi'])
    X_pred['phi_deg'] = np.rad2deg(X_pred['phi'])
    X_pred_inviscid['phi_deg'] = np.rad2deg(X_pred_inviscid['phi'])

    X_pred_inviscid.plot(y='phi_deg', style='-', label='Run %i: FNPF' % row.paper_name, alpha=0.5, ax=ax)
    X.plot(y='phi_deg', label='Run %i: model test' % row.paper_name, ax=ax)
    X_pred.plot(y='phi_deg', style='--', label='Run %i: hybrid' % row.paper_name, ax=ax)
        
    ax.grid(True)
    ax.set_xlabel(r'Time [s]')
    ax.set_ylabel(r'$\phi$ $[deg]$');

    return ax
    