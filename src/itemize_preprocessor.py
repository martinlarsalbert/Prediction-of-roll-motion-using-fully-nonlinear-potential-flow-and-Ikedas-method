import re
from nbconvert.preprocessors import Preprocessor

class ItemizePreprocessor(Preprocessor):

    def preprocess_cell(self, cell, resources, index):


        if cell.cell_type != "markdown":
            return cell, resources

        cell.source = self.itemize(body=cell.source)

        return cell, resources


    def itemize(self,body:str):

        """Making itemize of a bullet list ex:

        * $B_W$ does not change with amplitude, implying that they only contribute to the linear part ($B_1$) of the damping. (The $B_W$ was calculated with strip theory here)
        * $B_F$ has a small amplitude dependancy but the linear part is dominating.
        * $B_E$ has a large amplitude depandancy and only contributes to the quadratic damping ($B_2$)<cite data-cite="7505983/4AFVVGNT"></cite>.
        """

        for result in re.finditer(r'(\* .+\W)+', body):
        
            items = re.findall(r'\* (.+)', result.group(0))

            if len(items)==0:
                continue
            s='\\begin{itemize}\n'

            for i,item in enumerate(items):
            
                s+='\\item %s\n' % item

            s+='\\end{itemize}\n'

            body = body.replace(result.group(0),s)

        return body
