import joblib
from sklearn import tree
import matplotlib.pyplot as plt

import rolldecayestimators.ikeda_naked as ikeda_naked

from reports.examples import KVLCC2_section_table


def show():
    c_r_tree = joblib.load('../../models/C_r_tree.pkl')
    fig,ax = plt.subplots()
    fig.set_size_inches(15,8)
    #with plt.style.context('paper'):
    tree.plot_tree(c_r_tree, ax=ax, feature_names=[r'$\sigma$', r'$a_3$'], rounded=True);

def show_KVLCC2_C_r_prediction():


    df_kvlcc2 = KVLCC2_section_table.get()
    df_kvlcc2_ = df_kvlcc2.copy()
    OG = df_kvlcc2_['OG/d']*df_kvlcc2_['T']
    ra = 1000
    df_kvlcc2_['C_r'] = ikeda_naked.calculate_C_r(bwl=df_kvlcc2_.beam,
                          a_1=df_kvlcc2_.a_1, a_3=df_kvlcc2_.a_3, sigma=df_kvlcc2_.sigma, 
                                              H0=df_kvlcc2_.H0, d=df_kvlcc2_['T'], OG=OG, 
                          R=df_kvlcc2_.R, ra=ra)

    good_feature_names=['sigma', 'a_3']
    c_r_tree = joblib.load('../../models/C_r_tree.pkl')
    df_kvlcc2['C_r'] = c_r_tree.predict(X=df_kvlcc2[good_feature_names])

    fig,ax=plt.subplots()
    df_kvlcc2.plot(y='C_r', style='.-', label='decision tree', ax=ax)
    df_kvlcc2_.plot(y='C_r', style='.-', label='ikeda', ax=ax)
    ax.set_ylabel(r'$C_r$')
    ax.set_xlabel(r'station')
    ax.grid(True)