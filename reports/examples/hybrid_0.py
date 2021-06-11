import matplotlib.pyplot as plt
import numpy as np
import joblib
from copy import deepcopy
from collections import OrderedDict
import pandas as pd

from reports.examples.mdl import plot_amplitudes
import src.visualization.visualize as visualize 
import reports.mdl_results as mdl_results
import src.helpers
from reports.examples.ikeda import plot_ikeda
import shipflowmotionshelpers.shipflowmotionshelpers as helpers

id = 21338
key = 'kvlcc2_rolldecay_0kn'
invicid_motions = key

file_paths = [
    '../../data/external/kvlcc2_rolldecay_0kn',
]
df_parameters = pd.DataFrame()
df_parameters = pd.read_csv('../../data/processed/roll decay KVLCC2/fnpf_parameters.csv', index_col=0)

def get_models_and_results():
    
    parameters = df_parameters.loc[key]
    row = mdl_results.df_rolldecays.loc[id]
    models_motions = OrderedDict()
    df_results = pd.DataFrame()
    
    ikeda_name = 'ikeda_C_r'
    file_name = '%s_%s_%s.pkl' % (id,key,ikeda_name)
    model = joblib.load('../../models/%s' % file_name)['estimator']
    
    results = pd.Series(model.results, name=key)
    results['paper_name'] = row.paper_name
    results['id'] = row.name
        
    df_results = df_results.append(results)
    
    df_results = df_results.astype(float)
    df_results['id'] = df_results['id'].astype(int)
    df_results['paper_name'] = df_results['paper_name'].astype(int)

    df_results['method'] = 'hybrid'
    
    return models_motions,df_results


def show(amplitudes, amplitudes_motions, models_mdl, ylim=None, show_FNPF=False):

    
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
    results['B_W'] = df_amplitudes_motions['B_model'].values
    results_ = results.copy()
    results_['phi_a_deg'] = np.rad2deg(results_.index)
    results_.set_index('phi_a_deg', inplace=True)
    fig,ax=plt.subplots()
    plot_ikeda(df_amplitudes=amplitudes[id], results=results_, paper_name=row.paper_name, ax=ax)
    
    if show_FNPF:
        plot_amplitudes(df_amplitudes=df_amplitudes_motions, source='FNPF', paper_name=row.paper_name,
                        ax=ax, color='red')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[0:1], labels=labels[0:1], loc='upper left')
    
    if not ylim is None:
        ax.set_ylim(ylim)

    ax.set_ylabel(r'$B$ $[Nm \cdot s]$')
    ax.set_xlabel(r'$\phi_a$ $[deg]$')

def show_time(models_mdl, models_motions, show_hybrid=True, show_model_test=True):

    model_mdl = models_mdl[id]
    row = mdl_results.df_rolldecays.loc[id]
    
    ikeda_name = 'ikeda_C_r'
    file_name = '%s_%s_%s.pkl' % (id,key,ikeda_name)
    model_hybrid = joblib.load('../../models/%s' % file_name)['estimator']

    model_invicid = deepcopy(models_motions[invicid_motions])
    
    X = model_mdl.X.copy()
    X_pred = model_hybrid.predict(X)
    X_pred_inviscid = model_invicid.predict(X)

    fig,ax=plt.subplots()
    X['phi_deg'] = np.rad2deg(X['phi'])
    X_pred['phi_deg'] = np.rad2deg(X_pred['phi'])
    X_pred_inviscid['phi_deg'] = np.rad2deg(X_pred_inviscid['phi'])

    X_pred_inviscid.plot(y='phi_deg', style='-', label='Run %i: FNPF' % row.paper_name, alpha=0.5, ax=ax)
    
    if show_model_test:
        X.plot(y='phi_deg', label='Run %i: model test' % row.paper_name, ax=ax)
    
    if show_hybrid:
        X_pred.plot(y='phi_deg', style='--', label='Run %i: hybrid' % row.paper_name, ax=ax)
        
    ax.grid(True)
    ax.set_xlabel(r'Time [s]')
    ax.set_ylabel(r'$\phi$ $[deg]$');
    return ax


#key = 'kvlcc2_rolldecay_0kn'
#df_amplitudes_motions = amplitudes_motions[key].copy()
#row = mdl_results.df_rolldecays.loc[id]

#ikeda_name = 'ikeda_C_r'
#file_name = '%s_%s_%s.pkl' % (id,key,ikeda_name)
#model_hybrid = joblib.load('../../models/%s' % file_name)['estimator']
#model_mdl = models_mdl[id]

#X = model_mdl.X.copy()
#X_pred = model_hybrid.predict(X)
#X['phi_deg'] = np.rad2deg(X['phi'])
#X_pred['phi_deg'] = np.rad2deg(X_pred['phi'])
#
#
#fig,ax=plt.subplots()
#X.plot(y='phi_deg', label='Model test', ax=ax)
#X_pred.plot(y='phi_deg', label='Hybrid', ax=ax)
#ax.set_ylabel(r'$\phi$ $[deg]$')
#ax.set_xlabel(r'Time $[s]$')
#ax.grid(True)

