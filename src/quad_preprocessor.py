from nbconvert.preprocessors import Preprocessor
import re

class QuadPreprocessor(Preprocessor):

    def preprocess_cell(self, cell, resources, index):


        if cell.cell_type != "markdown":
            return cell, resources

        cell.source = add_quad(body=cell.source)

        return cell, resources


def add_quad(body:str):
    """[summary]

    Change:
    blablalbab.
    sddfdf
    To:
    blablalbab.
        sddfdf
    Adding \quad
    """
    body = re.sub(r'\n\n','\n\n\\quad ', body)
    return body