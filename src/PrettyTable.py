# class PrettyTable

class PrettyTable(list):
    """ Overridden list class which takes a 2-dimensional list of 
        the form [[1,2,3],[4,5,6]], and renders HTML and LaTeX Table in 
        IPython Notebook. For LaTeX export two styles can be chosen."""
    def __init__(self, initlist=[], extra_header=None, print_latex_longtable=True, caption='Caption', label='label', fontsize=r'\scriptsize', hline=1):
        self.print_latex_longtable = print_latex_longtable
        self.caption=caption
        self.label=label
        self.fontsize=fontsize
        self.hline = hline
        
        if extra_header is not None:
            if len(initlist[0]) != len(extra_header):
                raise ValueError("Header list must have same length as data has columns.")
            initlist = [extra_header]+list(initlist)
        super(PrettyTable, self).__init__(initlist)
    
    def latex_table_tabular(self):

        """Produces something like:

        \begin{table}[H]
        \small
        \center
        \caption{KVLCC2 sections}
        \label{tab:kvlcc2_sections}
            \begin{tabular}{llllllll}
        \toprule\addlinespace
        $x$ & $beam$ & $T_s$ & $\sigma$ & $\frac{OG}{d}$ & $R_b$ & $a_1$ & $a_3$\\
        \midrule
        -0.0808 & 0.1712 & 0.0294 & 0.594 & 1.1 & 0.0976 & 0.5341 & 0.0935\\
        4.7901 & 0.084 & 0.2379 & 0.4708 & 0.136 & 0.222 & -0.7722 & 0.103\\
        \bottomrule
        \end{tabular}
        \end{table}

        Returns
        -------
        LaTeX
        """

        latex = ["""
\\begin{table}[H]
%s
\\center
\\caption{%s}
\\label{tab:%s}
\\begin{tabular}""" % (self.fontsize, self.caption, self.label)]
     
        latex.append("{|"+"".join((["l|"]*len(self[0])))+"}\n")
        
        latex.append("\\hline\\addlinespace\n")
        for i,row in enumerate(self):
            latex.append(" & ".join(map(format, row)))
            latex.append("\\\\ \n")
            if i==self.hline:
                latex.append("\\hline")
        
        
        latex.append("""
\\hline
\\end{tabular}
\\end{table}""")

        return ''.join(latex)
    
    
    def latex_longtable(self):
        latex = ["\\begin{longtable}[c]{@{}"]
        latex.append("".join((["l"]*len(self[0]))))
        latex.append("@{}}\n")
        latex.append("\\toprule\\addlinespace\n")
        first = True
        for row in self:
            latex.append(" & ".join(map(format, row)))
            latex.append("\\\\\\addlinespace \n")
            if first:
                latex.append("\\midrule\\endhead\n")
                first = False
        latex.append("\\bottomrule \n \\end{longtable}")
        return ''.join(latex)
        
    
    def _repr_html_(self):
        html = ["<table>"]
        for row in self:
            html.append("<tr>")
            for col in row:
                html.append("<td>{0}</td>".format(col))
            html.append("</tr>")
        html.append("</table>")
        return ''.join(html)
    def _repr_latex_(self):
        if self.print_latex_longtable: 
            return self.latex_longtable()
        else: 
            return self.latex_table_tabular()
