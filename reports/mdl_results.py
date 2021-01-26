import pandas as pd
from src.data import database
import numpy as np

def load():
    db = database.get_db()

    sql = """
    SELECT * from run
    INNER JOIN loading_conditions
    ON (run.loading_condition_id = loading_conditions.id)
    INNER JOIN models
    ON (run.model_number = models.model_number)
    INNER JOIN ships
    ON (run.ship_name = ships.name)
    WHERE run.model_number='M5057-01-A' and run.test_type='roll decay' and run.project_number=40178362;
    """
    df_rolldecays = pd.read_sql(sql=sql, con=db.engine)
    df_rolldecays['rho']=1000
    df_rolldecays['g']=9.81
    df_rolldecays=df_rolldecays.loc[:,~df_rolldecays.columns.duplicated()]
    df_rolldecays.set_index('id', inplace=True)

    df_rolldecays['ship_speed'].fillna(0, inplace=True)
    
    df_rolldecays=df_rolldecays.loc[[21337,21338,21340,]].copy()
    df_rolldecays['paper_name'] = np.arange(len(df_rolldecays)) + 1

    return df_rolldecays

df_rolldecays = load()