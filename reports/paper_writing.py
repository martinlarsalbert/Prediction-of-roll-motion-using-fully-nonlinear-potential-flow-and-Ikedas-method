import os
import matplotlib.pyplot as plt
import matplotlib
import re
import sympy as sp
import rolldecayestimators.equations
from rolldecayestimators import equations
import rolldecayestimators.special_symbol as ss

def setup(rcParams):
    # Change to paper custom style:
    matplotlibrc_path = os.path.join(os.path.dirname(__file__),'matplotlibrc')
    #rcParams.update(matplotlib.rc_params_from_file(matplotlibrc_path))

# \label{eq:roll_decay_equation_cubic}
regexp_label = re.compile(pattern=r'\\label{eq\:([^}]+)', flags=re.MULTILINE)

# \input{equations/roll_decay_equation_himeno_linear}
regexp_input = re.compile(pattern=r'\\input{([^}]+)', flags=re.MULTILINE)

paper_figures_path = os.path.join(os.path.dirname(__file__),'figures')

def save_fig(fig, name, full_page=False, width_cm=15):
    """
    Save a figure to the paper
    :param fig: figure handle
    :param name: figure name (without extension)
    :param full_page: default None
    :width_cm width in cm
    :return: None
    """

    fnames = [
        os.path.join(paper_figures_path, '%s.eps' % name),
        os.path.join(paper_figures_path, '%s.pdf' % name),
        os.path.join(paper_figures_path, '%s.png' % name),
    ]

    fig.tight_layout()

    size = fig.get_size_inches()

    cm_to_inches = 0.393700787
    width = cm_to_inches*width_cm

    #if full_page:
    #    height = width*1.618
    #
    #else:
    #    height = width / 1.618

    #fig.set_dpi(300)
    #fig.set_size_inches(width, height)
    #plt.tight_layout()

    for fname in fnames:
        fig.savefig(fname=fname,dpi=300)

def generate_nomenclature(paper_path=None,exclude_dirs=['equations']):
    """
    Generate a nomenclature based on the equation labels in the tex files under paper_path folder
    :param paper_path: None->Default is present paper
    :return:
    """
    eq_labels=[]

    if paper_path is None:
        paper_path=rolldecay.paper_path

    file_paths = _find_tex_files(paper_path=paper_path, exclude_dirs=exclude_dirs)

    for file_path in file_paths:
        with open(file_path, mode='r') as file:
            s = file.read()

        eq_labels+=_find_eq_labels(s=s)

    input_paths = _find_inputs_in_files(file_paths)
    for file_path in input_paths:

        if not os.path.exists(file_path):
            file_path=os.path.join(paper_path,file_path)
            _,ext = os.path.splitext(file_path)
            if ext=='':
                file_path+='.tex'

        with open(file_path, mode='r') as file:
            s = file.read()


        eq_labels+=_find_eq_labels(s=s)

    equation_dict = _match_sympy_equations(eq_labels=eq_labels)
    symbols = _get_symbols(equation_dict=equation_dict)

    latex_nomenclature = _generate_latex_nomenclature(symbols=symbols)

    return latex_nomenclature

def _find_tex_files(paper_path, exclude_dirs=['equations']):

    file_paths = []
    for root, dirs, files in os.walk(paper_path, topdown=False):

        # Could this directory be excluded?
        exclude=False
        for exclude_dir in exclude_dirs:
            if exclude_dir in root:
                exclude=True
                break
        if exclude:
            continue

        for name in files:
            if os.path.splitext(name)[-1]=='.tex':
                path = os.path.join(root, name)
                file_paths.append(path)

    return file_paths

def _find_eq_labels(s:str):
    return regexp_label.findall(string=s)

def _find_inputs_in_files(file_paths:list):

    input_paths = []
    for file_path in file_paths:
        with open(file_path, mode='r') as file:
            s = file.read()

        input_paths+=_find_inputs(s=s)

    input_paths=list(set(input_paths))  # Remove possible duplicates

    return input_paths

def _find_inputs(s:str):
    return regexp_input.findall(string=s)


def _match_sympy_equations(eq_labels):
    avaliable_equation_dict = {key: value for key, value in rolldecayestimators.equations.__dict__.items() if isinstance(value, sp.Eq)}
    equation_dict = {}

    for eq_label in eq_labels:
        if eq_label in avaliable_equation_dict:
            equation_dict[eq_label] = avaliable_equation_dict[eq_label]

    return equation_dict

def _get_symbols(equation_dict:dict):

    symbols = {}
    for name,eq in equation_dict.items():
        if isinstance(eq,str):
            continue
        
        free_symbols = {symbol.name:symbol for symbol in eq.free_symbols}
        symbols.update(free_symbols)
    
    return symbols

def _latex_unit(unit:str):
    latex_unit = unit.replace('**', r'^')
    latex_unit=latex_unit.replace('*',r'\cdot ')
    latex_unit='%s'%latex_unit
    return latex_unit


def _generate_latex_nomenclature(symbols, subs=True, join_description=True, additional_descriptions={}, additions_units={}):
    """
    The method should create something like this:

    \mbox{}
    \nomenclature{$c$}{Speed of light in a vacuum inertial frame \nomunit{$m/s$}}
    \nomenclature{$h$}{Planck constant}
    \printnomenclature
    
    Parameters
    ----------
    subs : bool
        Make substitutions of hat symbols etc.
        (The substitutions are taken from equations.nicer_LaTeX)
    join_description : bool
        Symbols with the same description will get the same row in nomenclature.
    additional_descriptions : dict
        additional desctiption can be added
    additions_units : dict
        additional units can be added
    """

    symbols_ = dict(symbols)  # making a copy

    ## Divide the symbols in rows:
    description_rows = {}
    if join_description:
        descriptions = {}
        for name,symbol in sorted(symbols.items()):
            
            if hasattr(symbol,'description'):
                description = symbol.description
            elif symbol in additional_descriptions:
                description = additional_descriptions[symbol]
            else:
                continue
            
            
            if not description in descriptions:
                descriptions[description] = []
            
            descriptions[description].append(symbol)
            symbols_.pop(symbol.name)

        # Inversing this dict:
        description_rows = {items[0].name:items for description,items in descriptions.items()}
    
    for name,symbol in symbols_.items():
        if not name in description_rows:
            description_rows[name] = [symbol]

    content = ''
    for name,row in sorted(description_rows.items()):
        
        latex=''
        first = True
        for symbol in row:
            assert isinstance(symbol,sp.Symbol)

            latex_,description,unit = _symbol_to_latex(symbol=symbol, name=name, subs=subs, additional_descriptions=additional_descriptions, 
                                                        additions_units=additions_units)
            
            if first:
                first=False
            else:
                latex+=','

            latex+='%s' % latex_
            
        row = r'\nomenclature{'+latex+'}{'+description+ r'\nomunit{' + unit + '}}\n'
        
        content+=row

    latex_nomenclature = r"\mbox{}" + '\n' + content + '\n' + r"\printnomenclature"
    return latex_nomenclature

def _symbol_to_latex(symbol:ss.Symbol, name:str, subs=True, additional_descriptions={}, additions_units={}):
    
    description = ''
    unit=''
    if hasattr(symbol,'description'):
        description=symbol.description
    
    if symbol in additional_descriptions:
        description = additional_descriptions[symbol]            
        
    if len(description) == 0:
        if name == 't':
            description='time'
            unit='s'
    
    if len(description) > 1:
        description=description[0].lower() + description[1:]
    
    if hasattr(symbol, 'unit'):
        unit=unit=symbol.unit

    if symbol in additions_units:
        unit = additions_units[symbol]

    if subs:
        symbol = symbol.subs(equations.nicer_LaTeX)
    latex = symbol._repr_latex_()

    if unit=='':
        unit = ' '

    unit = _latex_unit(unit)

    return latex,description,unit

def save_table(file_path, tabular_tex:str, label:str, caption:str):

    tabular_tex=tabular_tex.replace('\$','$')
    tabular_tex=tabular_tex.replace(r'\textasciicircum ','^')

    latex="""
\\begin{table}[H]
    \centering
    \caption{%s}
   %s
    \label{%s}
\end{table}
    """ % (caption,tabular_tex,label)

    container = GeneralContainer()
    container.append(latex)

    container.generate_tex(file_path)
