from rolldecayestimators.direct_estimator_cubic import EstimatorCubic,EstimatorQuadraticB,EstimatorLinear
from sklearn.pipeline import Pipeline
from rolldecayestimators.transformers import CutTransformer, LowpassFilterDerivatorTransformer, ScaleFactorTransformer, OffsetTransformer
from rolldecayestimators.direct_estimator_cubic import EstimatorQuadraticB, EstimatorCubic, EstimatorQuadratic

from sklearn.base import clone
from copy import deepcopy
from numpy.random import normal
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import reports.examples.analytical_numerical


def show(omega0_lambda, accelaration_lambda, plot=True, dt=0.01):
    
    np.random.seed(42)

    ## Simulate:
    df = reports.examples.analytical_numerical.show(omega0_lambda=omega0_lambda, 
                                                    accelaration_lambda=accelaration_lambda, plot=False, dt=dt)
    df_true = df.drop(columns=['phi1d'])

    ## Add noise:
    df_measure = df_true.copy()
    df_measure['noise'] = normal(loc=0, scale=np.deg2rad(0.2), size=len(df_measure))
    df_measure['noise']-=df_measure['noise'].mean()

    df_measure['phi']+=df_measure['noise']

    ## Analyze the damping:
    lowpass_filter = LowpassFilterDerivatorTransformer(cutoff=1.0, minimum_score=0.0)
    cutter = CutTransformer(phi_max=np.deg2rad(15), phi_min=np.deg2rad(0), phi1d_start_tolerance=0.015)
    offset_transformer = OffsetTransformer()

    ## Differentiation
    estimator_diff = EstimatorQuadratic(fit_method='derivation', maxfev=100000)
    steps = [
        ('filter',lowpass_filter),
        #('cutter', cutter), 
        ('estimator', estimator_diff)
    ]

    pipline_estimator_diff = Pipeline(steps=steps)
    pipline_estimator_diff.fit(X=df_measure[['phi']])
    df_diff = pipline_estimator_diff.predict(df_true)

    ## Integration
    estimator_int= EstimatorQuadratic(fit_method='integration', maxfev=100000, p0=estimator_diff.parameters)
    steps = [
        ('filter',lowpass_filter),
        #('cutter', cutter), 
        ('estimator', estimator_int)
    ]

    pipline_estimator_int = Pipeline(steps=steps)
    pipline_estimator_int.fit(X=df_measure[['phi']])
    df_int = pipline_estimator_int.predict(df_true)
    pipline_estimator_int.score(df_true)

    if plot:
        fig,ax=plt.subplots()

        df_measure.plot(y='phi',style='-', color='grey', label='measurement', ax=ax, alpha=0.5)
        df_diff.plot(y='phi',style='r-', label='differentiation', ax=ax)
        df_int.plot(y='phi',style='g-', label='integration', ax=ax)
        df_true.plot(y='phi',style='k:', label='true', ax=ax)
        ax.set_ylabel(r'$\phi$ $[rad]$')
        ax.set_xlabel(r'time $[s]$')
        ax.grid(True)
        ax.legend()

    return df_measure,df_true

def _vary_cutoff(cutoff:float, fit_method:str, df_measure): 
    
    lowpass_filter = LowpassFilterDerivatorTransformer(cutoff=cutoff, minimum_score=0.0)
      
    estimator = EstimatorLinear(fit_method='derivation', maxfev=100000)
    steps = [
        ('filter',lowpass_filter),
        ('estimator', estimator)
    ]
    
    pipeline = Pipeline(steps=steps)
    pipeline.fit(X=df_measure[['phi']])
    
    if fit_method is 'integration':
        #estimator = EstimatorLinear(fit_method='integration', maxfev=100000, 
        #                                 p0=estimator.parameters)
        
        estimator = EstimatorLinear(fit_method='integration', maxfev=100000, 
                                         p0=estimator.parameters)
        
        steps = [
            #('filter',lowpass_filter),
#            ('cutter', cutter), 
            ('estimator', estimator)
        ]
        pipeline = Pipeline(steps=steps)
        pipeline.fit(X=df_measure[['phi']])
    
    return pipeline['estimator'].parameters

def vary_cutoff(df_measure, df_true):

    N = 10
    np.random.seed(42)

    cutoffs = np.linspace(0.7,15,N)
    df_vary = pd.DataFrame()
    for cutoff in cutoffs:

        for method in ['differentiation','integration']:
            s = pd.Series(_vary_cutoff(cutoff=cutoff, fit_method=method, df_measure=df_measure))
            s['method'] = method
            s['cutoff'] = cutoff
            df_vary = df_vary.append(s, ignore_index=True)

    s_true = pd.Series()
    A_44 = 1.0
    B_1 = 0.3
    C_1 = 5.0
    s_true['B_1A'] = B_1/A_44
    s_true['B_2A'] = 0

    s_true['C_1A'] = C_1/A_44
    s_true['C_3A'] = 0
    s_true['C_5A'] = 0

    fig,ax=plt.subplots()
    for method, df_ in df_vary.groupby(by='method'):
        df_.plot(x='cutoff', y='B_1A', style='.-', ax=ax, label=method)

    ax.set_ylabel(r'$B_1$ $[Nm \cdot s]$')
    ax.set_xlabel(r'Low pass filter cutoff frequency [1/s]')
    ax.grid(True)