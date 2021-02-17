Prediction-of-roll-motion-using-fully-nonlinear-potential-flow-and-Ikedas-method
==============================
The repository was used for the work conducted for the paper: "Prediction of roll motion using fully nonlinear potential flow and Ikeda's method". The LaTeX for the actual paper is however [here](https://github.com/martinlarsalbert/inviscid_CFD_-roll_decay)



[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/martinlarsalbert/Prediction-of-roll-motion-using-fully-nonlinear-potential-flow-and-Ikedas-method/HEAD)

## Note!
Some of the dependencies and the data used in this repo are unfortunatelly not open source.

# Setup
## .env
place a file called *.env* in the root of this repo containing the environmental variable for the database password. Simply add: password="..."

## nbstripout
Use a pre-commit filter called [nbstripout](https://github.com/kynan/nbstripout) to clean the output from the notebooks, if they contain sensitive information.

Project Organization
------------

    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. This is where the actual research has been conducted, data exploration, experiments etc.  
    │                                These notebooks are referred to in the [loogbook](notebooks/logbook.ipynb)
    │                                Naming convention is a number (for ordering).
    │                         
    │
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
