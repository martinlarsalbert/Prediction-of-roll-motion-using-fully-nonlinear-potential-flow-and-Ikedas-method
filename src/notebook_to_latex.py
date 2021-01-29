"""Convert notebook to LaTeX
"""

import nbformat

# 1. Import the exporter
from nbconvert import LatexExporter
from nbconvert.writers import FilesWriter
import nbconvert.preprocessors.extractoutput
from nbconvert.preprocessors import TagRemovePreprocessor
import src.bibpreprocessor
from traitlets.config import Config
import os
import shutil
import src

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

    # Configure our tag removal
    c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell",)
    c.TagRemovePreprocessor.remove_all_outputs_tags = ('remove_output',)
    c.TagRemovePreprocessor.remove_input_tags = ('remove_input',)
    #c.LatexExporter.preprocessors = [TagRemovePreprocessor,'src.bibpreprocessor.BibTexPreprocessor']
    c.LatexExporter.preprocessors = [TagRemovePreprocessor]

    # 2. Instantiate the exporter. We use the `basic` template for now; we'll get into more details
    # later about how to customize the exporter further.
    latex_exporter = LatexExporter(config = c)
    latex_exporter.template_file = os.path.join(src.path,'mytemplate.tplx')
    latex_exporter.exclude_input=True  # No input cells.
    latex_exporter.exclude_input_prompt=True  # No cell numbering
    latex_exporter.exclude_output_prompt=True  # No cell numbering
    
    # 3. Process the notebook we loaded earlier
    (body, resources) = latex_exporter.from_notebook_node(nb)

    FilesWriter(body=body,resources=resources)
       
    fw = FilesWriter(config=c, input=False)
    fw.write(body, resources, notebook_name=notebook_name)

    #with open(latex_path,'w') as file:
    #    file.write(body)