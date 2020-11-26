"""
This module contains some covenient methods to get manoeuvring results from the DB
"""
import pandas as pd

from sqlalchemy import create_engine
from mdldb.mdl_db import MDLDataBase
import mdldb.run
import signal_lab.mdl_to_evaluation
import os
from dotenv import load_dotenv
dirname = os.path.dirname(__file__)
base_path = os.path.split(os.path.split(dirname)[0])[0]
dotenv_path = os.path.join(base_path, '.env')
assert os.path.exists(dotenv_path)
load_dotenv(dotenv_path)  # Loading environment variables (where the password is one of them)


sql_template = """
SELECT * from
%s
INNER JOIN run
ON %s.run_id = run.id
    INNER JOIN projects
    ON run.project_number=projects.project_number
        INNER JOIN loading_conditions
        ON (run.loading_condition_id = loading_conditions.id)
            INNER JOIN models
            ON run.model_number = models.model_number
                INNER JOIN ships
                ON models.ship_name = ships.name
        
"""

# Password is retrieved from the environment variable "password"
pw = os.environ.get('password')
if not pw:
    raise ValueError('You need to define environment variable "password" with the password to the mdl database.\n The easiest way is to add a file ".env" in the root of this repo containing: password="..."')

engine = create_engine(r'postgresql://sspauser:' + pw + r'@ais01:5432/mdl')

def load(rolldecay_table_name='rolldecay_quadratic_b',sql=None,only_latest_runs=True, limit_score=0.96,
         include_softmooring=False, exclude_table_name=None):


    db = get_db()

    if sql is None:
        sql = sql_template % (rolldecay_table_name, rolldecay_table_name)

    df_rolldecay = pd.read_sql(sql, con=engine, index_col='run_id', )
    df_rolldecay = df_rolldecay.loc[:, ~df_rolldecay.columns.duplicated()]

    mask = df_rolldecay['score'] > limit_score
    df_rolldecay = df_rolldecay.loc[mask]

    if not include_softmooring:
        mask = df_rolldecay['Körfallstyp']!='Rak bana'
        df_rolldecay = df_rolldecay.loc[mask]

    if only_latest_runs:
        by = ['model_number', 'loading_condition_id', 'ship_speed']
        df_rolldecay = df_rolldecay.groupby(by=by).apply(func=get_latest)
        df_rolldecay.drop(columns = by, inplace=True)
        df_rolldecay.reset_index(inplace=True)
        df_rolldecay.set_index('run_id', inplace=True)

    if not exclude_table_name is None:
        df_exclude = pd.read_sql_table(table_name=exclude_table_name,con=engine, index_col='run_id',)
        common_index = list(set(df_rolldecay.index) - set(df_exclude.index))
        df_rolldecay=df_rolldecay.loc[common_index].copy()

    return df_rolldecay

def get_db():
    db = MDLDataBase(engine=engine)
    return db

def get_latest(group):
    """
    Get the latest run in this group:
    """
    s = group.sort_values(by=['date','run_number'], ascending=False).iloc[0]
    s['run_id'] = s.name
    return s

def load_run(db_run:mdldb.run.Run, load_temp=True, save_temp=True, save_as_example=False, prefer_hdf5=True)->pd.DataFrame:
    """[summary]

    Parameters
    ----------
    db_run : mdldb.run.Run
        Run database object
    load_temp : bool, optional
        should run be loaded from local copy if it exists?, by default True
    save_temp : bool, optional
        should run be saved locally in a temp folder?, by default True
    save_as_example : bool, optional
        The run can be saved in an example folder (not so usefull feature), by default False
    prefer_hdf5 : bool, optinal
        If a hdf5 file exist use it (instead of ascii-file which may also be presen),by default True

    Returns
    -------
    pd.DataFrame
        The time series is returned ad Pandas DataFrame
    """

    if save_as_example:
        other_save_directory = os.path.join(rolldecay.data_path,'example_data')
    else:
        other_save_directory = None

    db_run.load(load_temp=load_temp, save_temp=save_temp, other_save_directory=other_save_directory, prefer_hdf5=prefer_hdf5)

    df = signal_lab.mdl_to_evaluation.do_transforms(df=db_run.df)
    df.rename(columns={'MA/Roll': 'phi'}, inplace=True)
    df.rename(columns={'MA/Pitch': 'theta'}, inplace=True)
    df.rename(columns={'ma/roll': 'phi'}, inplace=True)
    df.rename(columns={'ma/pitch': 'theta'}, inplace=True)
    db_run.df = df
    
    db_run.units['phi']='rad'
    db_run.units['theta']='rad'

    return db_run
