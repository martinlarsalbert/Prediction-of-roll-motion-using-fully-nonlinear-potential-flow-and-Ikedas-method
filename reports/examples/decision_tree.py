import joblib
from sklearn import tree
import matplotlib.pyplot as plt


def show():
    c_r_tree = joblib.load('../../models/C_r_tree.pkl')
    fig,ax = plt.subplots()
    fig.set_size_inches(15,8)
    #with plt.style.context('paper'):
    tree.plot_tree(c_r_tree, ax=ax, feature_names=[r'$\sigma$', r'$a_3$'], rounded=True);