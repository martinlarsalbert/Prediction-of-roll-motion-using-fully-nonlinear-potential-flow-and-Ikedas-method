"""Convert notebook to LaTeX
"""

import nbformat

# 1. Import the exporter
from nbconvert import LatexExporter
import nbconvert.preprocessors
from traitlets.config import Config
import os
import shutil

def convert_notebook_to_latex(notebook_path:str, latex_path:str):

    notebook_filename = notebook_path
    with open(notebook_filename,encoding="utf8") as f:
        nb = nbformat.read(f, as_version=4)

    #path = os.path.split(os.path.abspath(__file__))[0]
    c = Config()
    #c.HTMLExporter.preprocessors = [ChangeIbynbLink]

    # 2. Instantiate the exporter. We use the `basic` template for now; we'll get into more details
    # later about how to customize the exporter further.
    latex_exporter = LatexExporter(config = c)
    #latex_exporter.template_file = os.path.join(path,'hidecode.tplx')

    # 3. Process the notebook we loaded earlier
    (body, resources) = latex_exporter.from_notebook_node(nb)

    with open(latex_path,'w') as file:
        file.write(body)