"""This preprocessor replaces bibliography code in markdowncell
"""

#-----------------------------------------------------------------------------
# Copyright (c) 2015, Julius Schulz
#
# Distributed under the terms of the Modified BSD License.
#
#-----------------------------------------------------------------------------

from nbconvert.preprocessors import *
import re
import os
import sys
from copy import deepcopy

class NoAuthorError(Exception): pass


def get_path(d:dict, path:list, default=None):
    value = d
    
    for sub_path in path:
        if sub_path in value:
            value=value[sub_path]
        else:
            return default

    return value


class BibTexPreprocessor(Preprocessor):

    def create_bibentry(self, refkey, reference, doi_title=True):
        
        reference = deepcopy(reference)
        
        entry = "\n"
        entry += "@article{" + refkey + ",\n"

        if not 'author' in reference:
            raise NoAuthorError('No author for reference:%s' % reference)


        entry += "  author = {"
        entry += " and ".join([a["family"] + ", " + a["given"] for a in reference["author"]])
        entry += "}, \n"
        
        items = {
            'title' : ['title'],
            'year' : ['issued','year'],
            'journal':["container-title"],
            'pages':["page"],
            'volume':["volume"],
            'issue':["issue"],
            'doi':["DOI"],
            'url':["URL"],
            'publisher' : ['publisher'],

        }

        if not "container-title" in reference:
            if "publisher" in reference:
                reference["container-title"]=reference["publisher"]  # dirty fix


        if doi_title:
            if 'DOI' in reference:
                reference['title'] = '%s (doi:%s)' % (reference['title'],reference['DOI'])
        
        first = True
        for item, path in items.items():
            
            value = get_path(d=reference, path=path)
            if value is None:
                continue
            else:
                if first:
                    first=False
                else:
                    entry+=', \n'

                row = "  %s = {%s}" % (item,value)
                
                entry+=row  

        
        """
        if ("title" in reference):
            entry += "  title = \{%s\} \n" % reference["title"]
        
        if ("issued" in reference):
            if 'year' in  reference["issued"]:
                entry += "  year = \{%s\}" % reference["issued"]["year"]
        
        if ("container-title" in reference):
            entry += "  journal = {" + reference["container-title"] + "}, \n"
        if ("page" in reference):
            entry += "  pages = {" + re.sub("-", "--", str(reference["page"])) + "}, \n"
        if ("volume" in reference):
            entry += "  volume = {" + reference["volume"] + "}, \n"
        if ("issue" in reference):
            entry += "  issue = {" + reference["issue"] + "}, \n"
        if ("DOI" in reference):
            entry += "  doi = {" + reference["DOI"] + "}, \n"
        if ("URL" in reference):
            entry += "  url = {" + reference["URL"] + "}, \n"

        
        """
        entry += "\n}\n"
        
        
        return entry

    def fix_non_ansii_characters(self):

        for key, reference in self.references.items():
            
            if not 'author' in reference:
                raise NoAuthorError('No author for reference:%s' % reference)
            
            authors = reference['author']
            for n,author in enumerate(authors):
                
                self.references[key]['author'][n]['family'] = self.replace_non_ascii(author['family'])
                self.references[key]['author'][n]['given'] = self.replace_non_ascii(author['given'])

    @staticmethod
    def replace_non_ascii(s:str):

        replacements = {
            'å' : r'{\aa}',
            'ä' : r'{\"a}',
            'ö' : r'{\"o}',
            'Å' : r'{\AA}',
            'Ä' : r'{\"A}',
            'Ö' : r'{\"O}',
            'é': r"\'e",
        }

        for old,new in replacements.items():
            s = s.replace(old, new)

        return s

    def create_bibfile(self, filename):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, "w", encoding='utf8') as f:
            for r in self.references:
                
                reference = self.references[r]
                
                bibentry = self.create_bibentry(r, reference)
                
                if (sys.version_info > (3, 0)):
                    f.write(bibentry)
                else:
                    f.write(bibentry).encode('utf-8')
        
    def preprocess(self, nb, resources):
        try:
          self.references = nb["metadata"]["cite2c"]["citations"]
        except:
          print("Did not find cite2c")

        self.fix_non_ansii_characters()

        figure_directory = self.config['FilesWriter']['build_directory']
        building_directory,_ = os.path.split(figure_directory)
        #bibfile_name = resources["unique_key"]+".bib"
        bibfile_name = "references.bib"
                
        bibfile_path = os.path.join(building_directory, bibfile_name)
        self.create_bibfile(bibfile_path)

        for index, cell in enumerate(nb.cells):
            nb.cells[index], resources = self.preprocess_cell(cell, resources, index)
        return nb, resources

    def preprocess_cell(self, cell, resources, index):
        """
        Preprocess cell

        Parameters
        ----------
        cell : NotebookNode cell
            Notebook cell being processed
        resources : dictionary
            Additional resources used in the conversion process.  Allows
            preprocessors to pass variables into the Jinja engine.
        cell_index : int
            Index of the cell being processed (see base.py)
        """
        if cell.cell_type == "markdown":
            if "<div class=\"cite2c-biblio\"></div>" in cell.source:
                replaced = re.sub("<div class=\"cite2c-biblio\"></div>", r"\\bibliography{"+resources["output_files_dir"]+"/"+resources["unique_key"]+r"} \n ", cell.source)
                cell.source = replaced
        return cell, resources
