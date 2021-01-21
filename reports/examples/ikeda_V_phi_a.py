import numpy as np
import joblib
import matplotlib.pyplot as plt

from reports import mdl_results
import rolldecayestimators.ikeda as ikeda_classes
from pyscores2.indata import Indata
from pyscores2.output import OutputFile
import src.visualization.visualize as visualize

def show():

    mdl_meta_data = mdl_results.df_rolldecays.iloc[0]
    scale_factor = mdl_meta_data.scale_factor
    N = 200
    V = np.linspace(0,15.5,N)*1.852/3.6/np.sqrt(scale_factor)
    kg=mdl_meta_data.kg/scale_factor

    ## Load ScoresII results
    indata = Indata()
    indata.open(indataPath='../../models/KVLCC2_speed.IN')
    output_file = OutputFile(filePath='../../data/interim/KVLCC2_speed.out')
    phi_a_deg = 10
    phi_a = np.deg2rad(phi_a_deg)

    model_mdl = joblib.load('../../models/KVLCC2_speed.pkl')

    ## Amplitude variation 1
    phi_as = np.deg2rad(np.linspace(0,phi_a_deg,N))
    ikeda_estimator0 = ikeda_classes.Ikeda.load_scoresII(V=np.min(V), 
                                                        w=model_mdl['estimator'].omega0, 
                                                        fi_a=phi_as, 
                                                        indata=indata, 
                                                        output_file=output_file, 
                                    scale_factor=scale_factor, BKL=0, BKB=0, kg=kg)

    results0 = ikeda_estimator0.calculate()
    results0['phi_a'] = phi_as
    results0.set_index('phi_a', inplace=True)

    ## Speed variation
    ikeda_estimator = ikeda_classes.Ikeda.load_scoresII(V=V, 
                                                        w=model_mdl['estimator'].omega0, 
                                                        fi_a=phi_a, 
                                                        indata=indata, 
                                                        output_file=output_file, 
                                    scale_factor=scale_factor, BKL=0, BKB=0, kg=kg)

    results = ikeda_estimator.calculate()
    results['V'] = V
    results['fn'] = fn = V/np.sqrt(ikeda_estimator.lpp*ikeda_estimator.g)
    results.set_index('fn', inplace=True)

    ## Amplitude variation 2
    phi_as = np.deg2rad(np.linspace(0,phi_a_deg,N))
    ikeda_estimator2 = ikeda_classes.Ikeda.load_scoresII(V=np.max(V), 
                                                        w=model_mdl['estimator'].omega0, 
                                                        fi_a=phi_as, 
                                                        indata=indata, 
                                                        output_file=output_file, 
                                    scale_factor=scale_factor, BKL=0, BKB=0, kg=kg)

    results2 = ikeda_estimator2.calculate()
    results2['phi_a'] = phi_as
    results2.set_index('phi_a', inplace=True)

    
    fig,axes=plt.subplots(ncols=3)
    fig.set_size_inches(10, 6)
    rename = {
        'B_W_hat':r'$\hat{B_W}$',
        'B_F_hat':r'$\hat{B_F}$',
        'B_E_hat':r'$\hat{B_E}$',
        'B_L_hat':r'$\hat{B_L}$',
    }

    interesting_=['B_W_hat', 'B_F_hat', 'B_E_hat', 'B_L_hat']
    interesting2 = [rename[key] for key in interesting_]

    ymax=np.max([results0['B_44_hat'].max(),results['B_44_hat'].max(),results2['B_44_hat'].max()])

    ax=axes[0]
    results_ = results0.rename(columns=rename)
    visualize.plot_area(results_, ax=ax, interesting_=interesting2)
    ax.set_xlabel(r'$\phi_a$ $[deg]$');
    ax.set_title(r'$F_n$:%0.2f $[-]$' % np.min(fn))
    ax.set_ylim((0,ymax))
    ax.set_yticks([])  # Removing the ticks this is just an illustration

    ax=axes[1]
    results_ = results.rename(columns=rename)
    visualize.plot_area(results_, ax=ax, interesting_=interesting2)
    ax.set_xlabel(r'$F_n$ $[-]$');
    ax.set_title(r'$\phi_a$:%0.0f $[deg]$' % phi_a_deg)
    ax.set_yticks([])  # Removing the ticks this is just an illustration
    ax.set_ylim((0,ymax))
    ax.get_legend().set_visible(False)

    ax=axes[2]
    results_ = results2.rename(columns=rename)
    visualize.plot_area(results_, ax=ax, interesting_=interesting2)
    ax.set_xlabel(r'$\phi_a$ $[deg]$');
    ax.set_title(r'$F_n$:%0.2f $[-]$' % np.max(fn))
    ax.get_legend().set_visible(False)
    ax.set_ylim((0,ymax))
    xlim = ax.get_xlim()
    ax.set_xlim(xlim[1], xlim[0])  # reversing
    ax.set_yticks([])  # Removing the ticks this is just an illustration
