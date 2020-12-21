"""helper methods
"""
import pandas as pd
import numpy as np

from pyscores2.output import OutputFile
from rolldecayestimators.ikeda import Ikeda, IkedaR
from pyscores2.runScores2 import Calculation
from pyscores2.indata import Indata
import rolldecayestimators
from rolldecayestimators import lambdas as lambdas

def get_ikeda(indata_file_path:str, output_file_path:str, mdl_meta_data:pd.Series, omega0:float, phi_a:float)->rolldecayestimators.ikeda.Ikeda:
    """setup an Ikeda class object

    Parameters
    ----------
    indata_file_path : str
        scores indata file path
    output_file_path : str
        scores outdata file path
    mdl_meta_data : pd.Series
        meta data from mdl db 
    omega0 : float or ndarray
        frequancies (usually natural frequency)
    phi_a : float or ndarray
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
        
    ## Run Ikeda
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
       
    BKL_ = BKL*np.ones(len(phi_a))
    BKB_ = BKB*np.ones(len(phi_a))
    
    ikeda = Ikeda.load_scoresII(V=V, w=w, fi_a=phi_a, indata=indata, output_file=output_file, 
                                scale_factor=scale_factor, BKL=BKL_, BKB=BKB_)
    
    R = mdl_meta_data.R/scale_factor  
    ikeda.R = R
    
    #ikeda = IkedaR.load_scoresII(V=V, w=w, fi_a=phi_a, indata=indata, output_file=output_file, 
    #                            scale_factor=scale_factor, BKL=BKL_, BKB=BKB_)
        
    return ikeda

def calculate_ikeda(ikeda):

    output = pd.DataFrame()
    output['B_44_hat']   = ikeda.calculate_B44()
    output['B_W0_hat']   = float(ikeda.calculate_B_W0())
    output['B_W_hat']    = float(ikeda.calculate_B_W())
    output['B_F_hat']    = ikeda.calculate_B_F()
    output['B_E_hat']    = ikeda.calculate_B_E()
    output['B_BK_hat']   = ikeda.calculate_B_BK()
    output['B_L_hat']    = float(ikeda.calculate_B_L())
    output['Bw_div_Bw0'] = float(ikeda.calculate_Bw_div_Bw0())
    return output

def get_estimator_variation(estimator, results, meta_data):

    if not hasattr(estimator,'X_pred_amplitudes'):
        estimator.calculate_amplitudes_and_damping()

    X_amplitudes=estimator.X_pred_amplitudes.copy()
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
    X_amplitudes['B']=X_amplitudes['B_n']*2*omega0*A_44/2
    X_amplitudes['B_hat'] = lambdas.B_hat_lambda(B=X_amplitudes['B'], Disp=meta_data['Volume'], beam=meta_data['beam'], g=meta_data['g'], rho=meta_data['rho'])
    return X_amplitudes