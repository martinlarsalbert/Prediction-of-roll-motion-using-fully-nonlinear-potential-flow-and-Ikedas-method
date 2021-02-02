"""Convert notebook to LaTeX
"""

import nbformat

# 1. Import the exporter
from nbconvert import LatexExporter
from nbconvert.writers import FilesWriter
import nbconvert.preprocessors.extractoutput
from nbconvert.preprocessors import TagRemovePreprocessor, Preprocessor
import src.bibpreprocessor
from src.itemize_preprocessor import ItemizePreprocessor
from traitlets.config import Config
import os
import shutil
import src
import re
from collections import OrderedDict
from IPython.display import Math
from sympy.physics.vector.printing import vpprint, vlatex
import sympy as sp

# Import the RST exproter
from nbconvert import RSTExporter

class FigureRenameError(Exception): pass

def convert_notebook_to_latex(notebook_path:str, build_directory:str, save_main=True, skip_figures=False):

    _,notebook_file_name = os.path.split(notebook_path)
    notebook_name,_ = os.path.splitext(notebook_file_name)

    notebook_filename = notebook_path
    with open(notebook_filename,encoding="utf8") as f:
        nb = nbformat.read(f, as_version=4)

    #path = os.path.split(os.path.abspath(__file__))[0]
    c = Config()
    # Employ nbconvert.writers.FilesWriter to write the markdown file 
    
    if not os.path.exists(build_directory):
        os.mkdir(build_directory)

    figure_directory = os.path.join(build_directory,'figures')
    if not os.path.exists(figure_directory):
        os.mkdir(figure_directory)

    c.FilesWriter.build_directory = figure_directory  # Only figures!!

    # Configure our tag removal
    c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell",)
    c.TagRemovePreprocessor.remove_all_outputs_tags = ('remove_output',)
    c.TagRemovePreprocessor.remove_input_tags = ('remove_input',)
    #c.LatexExporter.preprocessors = [TagRemovePreprocessor,'src.bibpreprocessor.BibTexPreprocessor']
    c.LatexExporter.preprocessors = [TagRemovePreprocessor, FigureName, src.bibpreprocessor.BibTexPreprocessor, ItemizePreprocessor]

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
    
    if not skip_figures:
        fw.write(body, resources, notebook_name=notebook_name)
    else:
        fw.write(body, {}, notebook_name=notebook_name)

    # Creata a tree structure instead:
    tree_writer(body=body, build_directory=build_directory, save_main=save_main)


class FigureName(Preprocessor):
    """Give names to figures"""

    def preprocess(self, nb, resources):
        #self.log.info("I'll keep only cells from %d to %d", self.start, self.end)
        #nb.cells = nb.cells[self.start:self.end]
        
        for cell_id, cell in enumerate(nb['cells']):

            meta_data = cell['metadata']
            if 'name' in meta_data:

                if 'outputs' in cell:
                    outputs = cell['outputs']
                    output_id = 0
                    for output_id, output in enumerate(outputs):                    
                        output = outputs[output_id]
                        output_meta_data = output.get('metadata',None)
                        if output_meta_data is None:
                            continue

                        filenames = output_meta_data['filenames']

                        output_name = 'output_%i_%i' % (cell_id, output_id)
                        for key, value in filenames.items():
                            if output_name in value:

                                # Rename to "figure":
                                new_figure_name = value.replace(output_name, meta_data['name'])

                                # Meta data:
                                nb['cells'][cell_id]['outputs'][output_id]['metadata']['filenames'][key] = new_figure_name       

                                # resources:
                                resources['outputs'][new_figure_name] = resources['outputs'].pop(value)


        
        return nb, resources


def tree_writer(body:str, build_directory:str, save_main=True):
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

    save_main : bool
        generate a main.tex with all subsections.
    """

    body = latex_cleaner(body)
    body = change_figure_paths(body=body, build_directory=build_directory)

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
    if save_main:
        with open(main_file_path, mode='w') as file:
            file.write(main)

def latex_cleaner(body:str):

    ## Clean equation:
    body = re.sub(r'\$\\displaystyle\W*\\begin{equation}',r'\\begin{equation}', body)
    body = re.sub(r'\\end{equation}\W*\$',r'\\end{equation}', body)

    ## Clean links:
    body = clean_links(body=body)
    
    return body

def clean_links(body:str):
    
    """Cleaning something like:
    \href{../../notebooks/01.3_select_suitable_MDL_test_KLVCC2_speed.ipynb\#yawrate}{yawrate}

    Returns
    -------
    [type]
        [description]
    """
    
    return re.sub(r"\\href\{.*.ipynb[^}]*}{[^}]+}",'',body)



def change_figure_paths(body:str, build_directory:str, figure_directory_name='figures'):
    """The figures are now in a subfolder, 
    so the paths need to be changed.

    Parameters
    ----------
    body : str
    """
    figure_directory = os.path.join(build_directory,figure_directory_name)
    for file in os.listdir(figure_directory):
        _,ext = os.path.splitext(file)
        if ext=='.pdf' or ext=='.png':
            new_path =r'%s/%s' % (figure_directory_name,file)
            body = body.replace(file, new_path)

    return body




def split_parts(body:str):
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

class Equation(Math):
    
    def __init__(self,data=None, label='eq:equation', url=None, filename=None, metadata=None, max_length=150):
        self.label = label
        
        data_text = vlatex(data)
        if len(data_text) > max_length:
            expanded = vlatex(sp.expand(data))
            parts = expanded.split('+')
            data_text = parts[0]
            row_length = len(data_text)
            if len(parts) > 1:
                for part in parts[1:]:
                    if (row_length + len(part)) < max_length:
                        data_text+='+%s' % part
                        row_length+=len(part)
                    else:
                        data_text+='\\\\ +%s' % part
                        row_length = len(part)

            data_text_ = '\\begin{aligned}\n%s\n\\end{aligned}' % data_text
        else:
            data_text_ = data_text

        super().__init__(data=data_text_, url=url, filename=filename, metadata=metadata)
    
    def _repr_latex_(self):
              
        label='eq:one'
        v2 = r"""
\begin{equation}
%s
\label{%s}
\end{equation}
""" % (self.data,self.label)
        
        return Math(v2)._repr_latex_()
