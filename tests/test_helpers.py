import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

import src.helpers as helpers
from rolldecayestimators import lambdas

def test_unhat():

    df_hat = pd.DataFrame()
    N = 10
    df_hat['B_hat'] = B_hat = np.linspace(0,1,N)
    df_hat['other'] = other = 123
    
    Disp = 123
    beam = 10
    g = 9.82
    rho = 679

    df = helpers.unhat(df=df_hat, Disp=Disp, beam=beam, g=g, rho=rho, hat_suffix='_hat')

    df_expected = pd.DataFrame()
    df_expected['other'] = other
    df_expected['B'] = lambdas.B_from_hat_lambda(B_44_hat=B_hat, Disp=Disp, beam=beam, g=g, rho=rho)

    assert_frame_equal(df_expected,df)