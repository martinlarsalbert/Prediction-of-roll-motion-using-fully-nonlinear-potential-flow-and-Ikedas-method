from src.PrettyTable import PrettyTable
import pandas as pd

class LateXTable(PrettyTable):

    def __init__(self, df:pd.DataFrame, units={}, rename={}, caption='Caption', label='label', print_latex_longtable=False, fontsize=r'\scriptsize'):
        
        df2 = pd.DataFrame(columns=df.columns)
        if len(units) > 0:
            df2.loc[-1] = pd.Series(units)
        
        df2 = df2.append(df, ignore_index=True)
        
        df2.rename(columns=rename, inplace=True)
        
        columns = df2.columns
        df2.fillna('', inplace=True)
        data = df2.values
                
        super().__init__(data, columns, print_latex_longtable=print_latex_longtable, caption=caption, label=label, fontsize=fontsize)
