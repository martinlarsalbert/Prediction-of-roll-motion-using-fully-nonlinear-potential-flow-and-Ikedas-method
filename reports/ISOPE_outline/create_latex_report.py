import os.path

from src.notebook_to_latex import convert_notebook_to_latex
import reports


notebook_path = os.path.join(reports.path,'ISOPE_outline','01.1.outline.ipynb')
latex_path = os.path.join(reports.path,'ISOPE_outline','01.1.outline.tex')

convert_notebook_to_latex(notebook_path=notebook_path, latex_path=latex_path)
