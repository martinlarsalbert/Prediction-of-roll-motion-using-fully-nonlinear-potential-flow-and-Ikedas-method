import pytest
import os.path

from src import notebook_to_latex
from src.itemize_preprocessor import ItemizePreprocessor
import tests

@pytest.fixture
def body():
    body_path = os.path.join(tests.path,'body.tex')
    
    with open(body_path, mode='r') as file:
        yield file.read()


def test_splitter_parts(body):
    pre, document, end = notebook_to_latex.split_parts(body=body)

def test_splitter_section(body):

    pre, document, end = notebook_to_latex.split_parts(body=body)
    parts = notebook_to_latex.splitter_section(document=document)

def test_splitter_section_linefeed(body):

    parts = notebook_to_latex.splitter_section(document='dfdfdf \section{first \n second}')
    assert 'first_second' in parts

def test_latex_cleaner():

    assert notebook_to_latex.latex_cleaner(r"""$\displaystyle
\begin{equation}""") == r"""\begin{equation}"""

def test_clean_links():
    assert notebook_to_latex.clean_links(body='asss [dfdf](dfdfd) asss') == 'asss  asss'

def test_itemize():
    body = "Looking at the roll amplitude variation (right):\n* (Please note that this x-axis is revered in this graph)\n* $B_L$ does not change with amplitude, implying that they only contribute to the linear part ($B_1$) of the damping.\n* $B_F$ has a small amplitude dependancy but the linear part is dominating."

    i = ItemizePreprocessor()
    new_body = i.itemize(body=body)
    a = 1

def test_equation_link():

    body = r'model (see Section \ref{eq_linear}).'
    new_body = notebook_to_latex.equation_links(body=body)

    a = 1


def test_tree_writer(body, tmpdir):

    notebook_to_latex.tree_writer(body=body, build_directory=str(tmpdir))