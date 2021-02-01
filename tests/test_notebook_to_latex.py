import pytest
import os.path

from src import notebook_to_latex
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



def test_tree_writer(body, tmpdir):

    notebook_to_latex.tree_writer(body=body, build_directory=str(tmpdir))