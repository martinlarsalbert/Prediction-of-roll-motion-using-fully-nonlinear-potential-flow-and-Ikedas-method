import numpy as np
import matplotlib.pyplot as plt


def plot_area(results,interesting_ = ['B_W_hat','B_F_hat','B_E_hat','B_L_hat'], ax=None):
    """Plot area with annotations

    Parameters
    ----------
    results : [type]
        [description]
    interesting_ : list, optional
        [description], by default ['B_W_hat','B_F_hat','B_E_hat','B_L_hat']
    ax : [type], optional
        [description], by default None

    Returns
    -------
    [type]
        axes
    """
    
    if ax is None:
        fig,ax=plt.subplots()
    
    results.plot.area(y=interesting_, ax=ax)
    
    ## Fancy annotation:
    xs = []
    for component_ in interesting_:
        values=results[component_]
        
        A =  np.trapz(values, x=results.index)
        xA = np.trapz(values*results.index, x=results.index)
            
        x = xA/A
        xs.append(x)
    
    ys = []
    y=0
    
    for x,component_ in zip(xs,interesting_):
        values=results[component_]
        
        dy = np.interp(x, values.index, values)/2
        y+=dy
        ys.append(y)
        y+=dy
        
    
    for x,y,component_ in zip(xs,ys,interesting_):
        values=results[component_]
        
        ax.annotate('%s' % component_, xy=(x,y))
        
        values_old = values
        
    return ax