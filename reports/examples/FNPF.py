import pandas as pd
import joblib
from collections import OrderedDict

import shipflowmotionshelpers.shipflowmotionshelpers as helpers
import reports.mdl_results as mdl_results
import reports.examples.mdl

file_paths = [
    '../../data/external/kvlcc2_rolldecay_0kn',
    '../../data/external/kvlcc2_rolldecay_15-5kn_const_large',
    '../../data/external/kvlcc2_rolldecay_15-5kn_const_large2',
    '../../data/external/kvlcc2_rolldecay_15-5kn_const_large_5deg',
    '../../data/external/kvlcc2_rolldecay_15-5kn_const_large_ikeda',
    '../../data/external/kvlcc2_rolldecay_15-5kn_ikeda_dev',
]
df_parameters = pd.DataFrame()
df_parameters =  helpers.load_parameters(file_path=file_paths)

mask_0 = (df_parameters['vm_s'].round(5) == 0)
df_parameters.loc[mask_0,'id'] = 21338  # MDL DB run id
df_parameters.loc[~mask_0,'id'] = 21340
mask_visc = (df_parameters[['b4l','b4q']] > 0).any(axis=1)

def get_models_and_results():
    models_motions = OrderedDict()
    df_results = pd.DataFrame()
    for key,parameters in df_parameters.iterrows():

        row = mdl_results.df_rolldecays.loc[parameters.id]
        model_motions = joblib.load('../../models/%s.pkl' % key)
        model = model_motions['estimator']
        models_motions[key] = model

        results = pd.Series(model.results, name=key)
        results['paper_name'] = row.paper_name
        results['id'] = row.name
        
        df_results = df_results.append(results)
    
    df_results = df_results.astype(float)
    df_results['id'] = df_results['id'].astype(int)
    df_results['paper_name'] = df_results['paper_name'].astype(int)
    

    return models_motions,df_results

def show(amplitudes, df_results, ylim=None):

    index = df_parameters.loc[~mask_visc].index
    reports.examples.mdl.show(amplitudes=amplitudes, df_results=df_results.loc[index], ylim=ylim)