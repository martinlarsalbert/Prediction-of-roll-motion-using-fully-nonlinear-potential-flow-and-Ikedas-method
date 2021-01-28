"""Convert notebook to LaTeX
"""

import nbformat

# 1. Import the exporter
from nbconvert import LatexExporter
from nbconvert.writers import FilesWriter
import nbconvert.preprocessors.extractoutput
from traitlets.config import Config
import os
import shutil

# Import the RST exproter
from nbconvert import RSTExporter

def convert_notebook_to_latex(notebook_path:str, build_directory:str):

    _,notebook_file_name = os.path.split(notebook_path)
    notebook_name,_ = os.path.splitext(notebook_file_name)

    notebook_filename = notebook_path
    with open(notebook_filename,encoding="utf8") as f:
        nb = nbformat.read(f, as_version=4)

    #path = os.path.split(os.path.abspath(__file__))[0]
    c = Config()
    # Employ nbconvert.writers.FilesWriter to write the markdown file 
    c.FilesWriter.build_directory = build_directory

    # 2. Instantiate the exporter. We use the `basic` template for now; we'll get into more details
    # later about how to customize the exporter further.
    latex_exporter = LatexExporter(config = c)
    latex_exporter.exclude_input=True  # No input cells.

    # 3. Process the notebook we loaded earlier
    (body, resources) = latex_exporter.from_notebook_node(nb)
    output = body

    FilesWriter(body=body,resources=resources)
       
    fw = FilesWriter(config=c, input=False)
    fw.write(output, resources, notebook_name=notebook_name)

    #with open(latex_path,'w') as file:
    #    file.write(body)