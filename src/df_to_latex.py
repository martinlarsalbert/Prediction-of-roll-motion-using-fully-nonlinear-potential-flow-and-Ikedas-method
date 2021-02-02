from src.PrettyTable import PrettyTable
import pandas as pd

class LateXTable(PrettyTable):

    def __init__(self, df:pd.DataFrame, caption='Caption', label='label', print_latex_longtable=False):
        super().__init__(df.values, df.columns, print_latex_longtable=print_latex_longtable, caption=caption, label=label)
