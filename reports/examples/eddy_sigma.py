import matplotlib.patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.helpers import estimate_sigma,calculate_B_star_hat

def plot_simplified_section(fig, model, xy=(.25, .70)):
    
    ax = fig.add_axes([xy[0], xy[1], .10, .10], zorder=1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    B2 = model.B/2    
    x1 = B2-model.R
    rectangle_1 = matplotlib.patches.Rectangle((0,0), x1, model.d, angle=0.0)
    
    y1 = model.R
    h1 = model.d - model.R
    rectangle_2 = matplotlib.patches.Rectangle((0,y1), B2, h1, angle=0.0)
    
    bilge = matplotlib.patches.Wedge((x1,y1), r=model.R, theta1=270, theta2=360)
    
    ax.add_patch(rectangle_1)
    ax.add_patch(rectangle_2)
    ax.add_patch(bilge)
    
    ax.set_xlim(0,B2)
    ax.set_ylim(0,model.d)
    ax.axis('equal')

def show():

    model = pd.Series()
    model['B'] = 0.280
    model['d'] = 0.112
    model['w_hat'] = 0.751
    model['phi_a'] = 0.31
    model['OG/d'] = 0
    model['L'] = 0.8

    N=100
    data = np.tile(model,(N,1))
    df_ = pd.DataFrame(data=data, columns=model.index)
    df_['R/B'] = np.linspace(0,1/2,N)
    df_['R'] = model.B*df_['R/B']
    df_['sigma'] = estimate_sigma(b=df_['B'],t=df_['d'],R=df_['R'])
    df_['volume'] = df_['sigma']*df_['B']*df_['d']*df_['L']
    df_.set_index('R/B', inplace=True)

    fig,ax=plt.subplots()
    plot_simplified_section(fig=fig, model=df_.iloc[0], xy=(0.15,0.73))
    plot_simplified_section(fig=fig, model=df_.iloc[50], xy=(0.5,0.55))
    plot_simplified_section(fig=fig, model=df_.iloc[99], xy=(0.8,0.15))

    label=r'$\hat{B_e*}$'
    ax.set_ylabel(label)
    ax.tick_params(axis='y', colors='b')
    df_['B_e_star_hat_pred'] = calculate_B_star_hat(df_)
    df_.plot(y='B_e_star_hat_pred', label=label, ax=ax, zorder=10)
    ax.legend(loc='lower left')

    ax_sigma = ax.twinx()
    ax_sigma.tick_params(axis='y', colors='r')
    label=r'$\sigma$'
    df_.plot(y='sigma', style='r-', label=label, ax=ax_sigma, zorder=20)
    ax_sigma.plot(df_.index,df_['sigma'], 'r-', label=label, zorder=20)
    ax_sigma.set_ylabel(label)
    