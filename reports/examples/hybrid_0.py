import matplotlib.pyplot as plt
import numpy as np
import joblib

from reports.examples.mdl import plot_amplitudes
import src.visualization.visualize as visualize 
import reports.mdl_results as mdl_results
import src.helpers
from reports.examples.ikeda import plot_ikeda


def show(amplitudes, amplitudes_motions, models_mdl, ylim=None):
    id = 21338
    key = 'kvlcc2_rolldecay_0kn'
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
    plot_amplitudes(df_amplitudes=df_amplitudes_motions, source='FNPF', paper_name=row.paper_name,
                        ax=ax, color='red')
    ax.set_title('Hybrid method')
    ax.legend()
    if not ylim is None:
        ax.set_ylim(ylim)