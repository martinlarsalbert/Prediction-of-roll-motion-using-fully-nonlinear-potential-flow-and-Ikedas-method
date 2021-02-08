import os.path

from src.notebook_to_latex import convert_notebook_to_latex
import reports


notebook_path = os.path.join(reports.path,'ISOPE_outline','01.1.outline.ipynb')
build_directory = os.path.join(reports.path,'ISOPE')

if not os.path.exists(build_directory):
    os.mkdir(build_directory)

convert_notebook_to_latex(notebook_path=notebook_path, build_directory=build_directory, save_main=False, skip_figures=True)

