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
import re
from collections import OrderedDict

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
    
    # Creata a tree structure instead:
    tree_writer(body=body, build_directory=build_directory)
    
def tree_writer(body:str, build_directory:str):
    """Splitting the generated LaTex document into sub files:
    
    * main.tex
        * section 1
        * section 2
        *...    

    Parameters
    ----------
    body : str
        LaTeX text

    build_directory : str
        Where should the tree be placed
    """

    body = latex_cleaner(body)

    pre, document, end = split_parts(body=body)
    sections = splitter_section(document=document)

    main = '%s\n\\begin{document}\n' % pre
    
    for section_name, section in sections.items():
        
        # Create the section file:
        section_file_name = '%s.tex' % section_name
        section_file_path = os.path.join(build_directory, section_file_name)
        with open(section_file_path, mode='w') as file:
            file.write(section)

        # Make a ref in the main file:
        ref = r'\input{%s}' % section_name
        ref+='\n'

        main+=ref
        
    main+='\n\\end{document}%s' % end

    main_file_name = 'main.tex'
    main_file_path = os.path.join(build_directory, main_file_name)
    with open(main_file_path, mode='w') as file:
        file.write(main)

def latex_cleaner(body):

    ## Clean equation:
    body = re.sub(r'\$\\displaystyle\W*\\begin{equation}',r'\\begin{equation}', body)
    body = re.sub(r'\\end{equation}\W*\$',r'\\end{equation}', body)
    
    return body


def split_parts(body):
    """Split into:
    * Pre
    * Document
    * End

    Parameters
    ----------
    body : [type]
        [description]
    """
    
    

    p = re.split(pattern= r'\\begin{document}', string=body)
    pre = p[0]
    rest = p[1]

    p2 = re.split(pattern= r'\\end{document}', string=rest)
    document = p2[0]
    end = p2[1]

    return pre, document, end


def splitter_section(document):

    
    parts = re.split(pattern= r'\\section', string=document)

    sections = OrderedDict()

    for part in parts[1:]:
        result = re.match(pattern=r'^\{([^}]+)', string=part)
        if not result:
            raise ValueError('Could not find the section name in:%s' % part)
        
        text = result.group(1)
        ps = re.findall(r'[\w]+', text)
        section_name = ps[0]
        if len(ps)>1:
            for p_ in ps[1:]:
                section_name+=' %s' % p_

        section_name = section_name.replace(' ','_')
        section_name = section_name.lower()


        section = '\\section%s' % part
        sections[section_name] = section

    return sections
