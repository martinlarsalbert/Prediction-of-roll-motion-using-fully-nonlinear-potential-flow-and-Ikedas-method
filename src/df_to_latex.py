from src.PrettyTable import PrettyTable
import pandas as pd

class LateXTable(PrettyTable):

    def __init__(self, df:pd.DataFrame, units={}, rename={}, caption='Caption', label='label', print_latex_longtable=False, fontsize=r'\scriptsize'):
        """Create a LaTeX table object that works in both LaTeX and HTML

        Parameters
        ----------
        df : pd.DataFrame
            The data that should be in the table
        units : dict, optional
            You can speficy the units here, by original column name, by default {}
        rename : dict, optional
            You can rename the columns before printout, by default {}
        caption : str, optional
            This will be the caption in LaTeX, by default 'Caption'
        label : str, optional
            This will be the label: tab:label, by default 'label'
        print_latex_longtable : bool, optional
            A switch to instead get a longtable in LaTeX, by default False
        fontsize : str, optional
            What is the fontsize of this table?, by default r'\scriptsize'
        """
        
        df2 = pd.DataFrame(columns=df.columns)
        if len(units) > 0:
            df2.loc[-1] = pd.Series(units)
        
        df2 = df2.append(df, ignore_index=True)
        
        df2.rename(columns=rename, inplace=True)
        
        columns = df2.columns
        df2.fillna('', inplace=True)
        data = df2.values
                
        super().__init__(data, columns, print_latex_longtable=print_latex_longtable, caption=caption, label=label, fontsize=fontsize)
