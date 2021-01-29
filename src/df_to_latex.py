from src.PrettyTable import PrettyTable
import pandas as pd

class LateXTable(PrettyTable):

    def __init__(self, df:pd.DataFrame):
        super().__init__(df.values, df.columns)
