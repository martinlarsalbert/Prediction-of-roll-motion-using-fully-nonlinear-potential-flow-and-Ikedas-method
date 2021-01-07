"""helper methods
"""
import pandas as pd
import numpy as np
from collections import OrderedDict

from pyscores2.output import OutputFile
from rolldecayestimators.ikeda import Ikeda, IkedaR
from pyscores2.runScores2 import Calculation
from pyscores2.indata import Indata
import rolldecayestimators
from rolldecayestimators import lambdas as lambdas

def get_ikeda(indata_file_path:str, output_file_path:str, mdl_meta_data:pd.Series,IkedaClass=rolldecayestimators.ikeda.Ikeda, omega0=None, phi_a=None)->rolldecayestimators.ikeda.Ikeda:
    """setup an Ikeda class object

    Parameters
    ----------
    indata_file_path : str
        scores indata file path
    output_file_path : str
        scores outdata file path
    mdl_meta_data : pd.Series
        meta data from mdl db 
    omega0 : float or ndarray or None (Then it should be specified in the calculation step)
        frequancies (usually natural frequency)
    phi_a : float or ndarray or None (Then it should be specified in the calculation step)
        roll amplitude [rad]

    Returns
    -------
    rolldecayestimators.ikeda.Ikeda
        ikeda class object
    """

    scale_factor = mdl_meta_data.scale_factor
    
    ## Load ScoresII results
    indata = Indata()
    indata.open(indataPath=indata_file_path)
    output_file = OutputFile(filePath=output_file_path)
        
    w = omega0
    V = mdl_meta_data.ship_speed*1.852/3.6/np.sqrt(scale_factor)
    
    if not mdl_meta_data.BKL:
        BKL=0
    else:
        BKL=mdl_meta_data.BKL/scale_factor
    
    if not mdl_meta_data.BKB:
        BKB = 0
    else:
        BKB=mdl_meta_data.BKB/scale_factor
    
    
    kg=mdl_meta_data.kg/scale_factor
    #S_f=mdl_meta_data.S/(scale_factor**2)

    ikeda = IkedaClass.load_scoresII(V=V, w=w, fi_a=phi_a, indata=indata, output_file=output_file, 
                                scale_factor=scale_factor, BKL=BKL, BKB=BKB, kg=kg)

    if not isinstance(ikeda, rolldecayestimators.ikeda.IkedaR):
        R = mdl_meta_data.R/scale_factor  
        ikeda.R = R
        
    return ikeda

def calculate_ikeda(ikeda:rolldecayestimators.ikeda.Ikeda, omega0=None, phi_a=None)->pd.DataFrame:
    """
    Parameters
    ----------
    ikeda : rolldecayestimators.ikeda.Ikeda
        [description]
    omega0 : float or ndarray or None (if it has already been defined)
        frequancies (usually natural frequency)
    phi_a : float or ndarray or None (if it has already been defined)
        roll amplitude [rad]

    Returns
    -------
    pd.DataFrame
        DataFrame with ikeda damping
    """
    raise ValueError('This method has been depricated')
    

def get_estimator_variation(estimator, results, meta_data):

    if not hasattr(estimator,'X_pred_amplitudes'):
        estimator.calculate_amplitudes_and_damping()

    X_amplitudes=estimator.X_pred_amplitudes.copy()
    return get_variation(X_amplitudes=X_amplitudes, results=results, meta_data=meta_data)
    
def get_variation(X_amplitudes, results, meta_data):
    
    phi_a=X_amplitudes['phi_a']
    B_e = lambdas.B_e_lambda_cubic(B_1=results['B_1'], B_2=results['B_2'], B_3=results['B_3'], 
                                   omega0=results['omega0'], phi_a=phi_a)
    B_e_hat = lambdas.B_hat_lambda(B=B_e, Disp=meta_data['Volume'], beam=meta_data['beam'], g=meta_data['g'], rho=meta_data['rho'])
    X_amplitudes['B_e'] = B_e
    X_amplitudes['B_e_hat'] = B_e_hat
    X_amplitudes['B_e'] = X_amplitudes['B_e'].astype(float)
    X_amplitudes['B_e_hat'] = X_amplitudes['B_e_hat'].astype(float)   
    
    return X_amplitudes

def get_data_variation(estimator, results, meta_data):
    
    if not hasattr(estimator,'X_amplitudes'):
        estimator.calculate_amplitudes_and_damping()

    X_amplitudes=estimator.X_amplitudes
    omega0=estimator.omega0
    A_44=results['A_44']
    zeta = X_amplitudes['zeta_n']
    X_amplitudes['B']=2*A_44*omega0*zeta
        
    X_amplitudes['B_hat'] = lambdas.B_hat_lambda(B=X_amplitudes['B'], Disp=meta_data['Volume'], beam=meta_data['beam'], g=meta_data['g'], rho=meta_data['rho'])
    return X_amplitudes

def unhat(df:pd.DataFrame, Disp:float, beam:float, g:float, rho:float, hat_suffix = '_hat')-> pd.DataFrame:
    """Create a new dataframe with damping without hat

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with nondimensional damping (having the hat_suffix)
    Disp : float, ndarray
        Ship volume [m3]
    beam : float, ndarray
        Ship beam [m]
    g : float, ndarray
        gravity
    rho : float, ndarray
        water density
    hat_suffix : str, optional
        columns containing this suffix will be unormalized, by default '_hat'

    Returns
    -------
    pd.DataFrame
        New dataframe with "unhatted" dimensional damping
    """

    new_df = pd.DataFrame(index=df.index)

    hat_keys = [key for key in df.keys() if hat_suffix in key]
    unhat_keys = [key.replace(hat_suffix,'') for key in hat_keys]
    for hat_key, unhat_key in zip(hat_keys,unhat_keys):

        new_df[unhat_key] = lambdas.B_from_hat_lambda(B_44_hat=df[hat_key], Disp=Disp, beam=beam, g=g, rho=rho)

    return new_df

def hatify(df:pd.DataFrame, Disp:float, beam:float, g:float, rho:float)-> pd.DataFrame:

    new_df = pd.DataFrame(index=df.index)

    for key in df:
        
        hat_key = '%s_hat' % key
        new_df[hat_key] = lambdas.B_to_hat_lambda(B=df[key], Disp=Disp, beam=beam, g=g, rho=rho)

    return new_df
