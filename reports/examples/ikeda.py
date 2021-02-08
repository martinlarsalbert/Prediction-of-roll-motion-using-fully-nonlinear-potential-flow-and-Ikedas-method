import matplotlib.pyplot as plt
import numpy as np
import joblib

from reports.examples.mdl import plot_amplitudes
import src.visualization.visualize as visualize 
import reports.mdl_results as mdl_results
import src.helpers

def plot_ikeda(df_amplitudes,results, paper_name, ax=None):
    
    if ax is None:   
        fig,ax=plt.subplots()
    rename = {
        'B_W':r'$B_W$',
        'B_F':r'$B_F$',
        'B_E':r'$B_E$',
        'B_L':r'$B_L$',
    }
    
    interesting_=['B_W', 'B_F', 'B_E', 'B_L']
    interesting2 = [rename[key] for key in interesting_]
    results_ = results.rename(columns=rename)
    
    visualize.plot_area(results_, ax=ax, interesting_=interesting2)
    plot_amplitudes(df_amplitudes=df_amplitudes, source='model test', paper_name=paper_name,
                    ax=ax, color='black')
    ax.set_xlabel(r'$\phi_a$ $[deg]$')
    #ax.set_ylim(y_lim_motions)
    ax.legend()


def get_estimator(id,ikeda_name):
    file_name = '%s_%s.pkl' % (id,ikeda_name)
    ikeda = joblib.load('../../models/%s' % file_name)
    return ikeda

def show(amplitudes, amplitudes_motions, models_mdl, ylim=None):
    id = 21338
    ikeda_names = ['ikeda_r_s','ikeda_C_r',]
    paper_ikeda_names = {
        'ikeda_C_r' : r'Decision tree $C_r$',
        'ikeda_r_s' : r'Regular implementation',
    }
    fig,axes = plt.subplots(ncols=len(ikeda_names))
    for ax,ikeda_name in zip(axes,ikeda_names):

        row = mdl_results.df_rolldecays.loc[id]
        ikeda = get_estimator(id=id, ikeda_name=ikeda_name)
        model = models_mdl[id]
        df_amplitudes = amplitudes[id]
        #phi_as = np.linspace(df_amplitudes['phi_a'].min(), df_amplitudes['phi_a'].max(), 100)
        phi_as = df_amplitudes['phi_a']

        df = ikeda.calculate(w=model.results['omega0'], fi_a=phi_as)
        df['phi_a_deg'] = np.rad2deg(phi_as)
        df.set_index('phi_a_deg', inplace=True)

        results = src.helpers.unhat(df=df, 
                                    Disp=ikeda.volume, 
                                    beam=ikeda.beam, 
                                    g=ikeda.g, 
                                    rho=ikeda.rho)

        plot_ikeda(df_amplitudes=amplitudes[id], results=results, paper_name=row.paper_name, ax=ax)
    
        ax.set_title(paper_ikeda_names[ikeda_name])
        ax.legend(loc='upper left')
        
        if not ylim is None:
            ax.set_ylim(ylim)
    
    axes[0].get_legend().set_visible(False)
    