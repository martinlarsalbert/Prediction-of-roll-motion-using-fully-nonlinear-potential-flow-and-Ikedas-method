import os.path

from src.notebook_to_latex import convert_notebook_to_latex
import reports


notebook_path = os.path.join(reports.path,'ISOPE_outline','01.1.outline.ipynb')
build_directory = os.path.join(reports.path,'ISOPE')

if not os.path.exists(build_directory):
    os.mkdir(build_directory)

skip_figures=True
convert_notebook_to_latex(notebook_path=notebook_path, build_directory=build_directory, save_main=False, skip_figures=skip_figures)

if not skip_figures:
    ## Special treatment
    import joblib
    import graphviz 
    from sklearn import tree
    clf = joblib.load('models/C_r_tree.pkl')
    dot_data = tree.export_graphviz(clf, out_file=None, 
                                    feature_names=[r'sigma', r'a_1', r'a_3'], rounded=True, 
                                    special_characters=True) 
    graph = graphviz.Source(dot_data) 
    graph.render("reports/ISOPE/figures/decision_tree") 

