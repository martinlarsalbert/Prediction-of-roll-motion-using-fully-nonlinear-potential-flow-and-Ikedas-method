"""Various methods to simplify the run of scoresII
"""

from scipy.integrate import simps
import numpy as np
import pandas as pd

from pyscores2.indata import Indata
from pyscores2.runScores2 import Calculation
from pyscores2.output import OutputFile
from pyscores2 import TDPError

class DraughtError(ValueError): pass

def add_cScores(sections):
    sections=sections.copy()
    sections['cScores']=sections['area']/(sections['b']*sections['t'])
    mask=sections['cScores']>1
    sections.loc[mask,'cScores']=1
    return sections

def cut_sections(sections, draught):
    sections=sections.copy()
    mask = sections['t']>draught
    sections.loc[mask,'t']=draught
    sections.loc[mask,'area']-=draught*sections['b'].max()  # Assuming rectangular shape
    return sections

def remove_duplicate_sections(sections):
    sections=sections.copy()
    mask=~sections['x'].duplicated()
    sections=sections.loc[mask]
    assert sections['x'].is_unique
    return sections

def too_small_sections(sections):
    sections=sections.copy()
    small = 0.1
    mask=sections['b']==0
    sections.loc[mask,'b']=small
    mask=sections['t']==0
    sections.loc[mask,'t']=small
    mask=sections['area']==0
    sections.loc[mask,'area']=small
    return sections

def calculate_lcb(x, area, lcb_correction=1,**kwargs):
    """
    Calculate lcb from AP
    """
    return lcb_correction*simps(y=area*x,x=x)/np.trapz(y=area,x=x)

def calculate_dispacement(x, area, displacement_correction=1,**kwargs):
    """
    Calculate displacement
    """
    return displacement_correction*np.trapz(y=area,x=x)



def define_indata(row, sections, rho=1000,  g=9.81, displacement_correction=1, lcb_correction=1):
    
    indata = Indata()
    
    draught=(row.TA+row.TF)/2
    indata.draught=draught
    if draught<=sections['t'].max():
        sections = cut_sections(sections, draught)
    else:
        raise DraughtError('Draught is too large for sections')
    
    sections=add_cScores(sections)
    
    indata.cScores=np.array(sections['cScores'])
    indata.ts=np.array(sections['t'])
    indata.bs=np.array(sections['b'])
    indata.zbars=np.zeros_like(sections['b'])  # Guessing...
        
    beam=sections['b'].max()
    indata.lpp=sections['x'].max()-sections['x'].min()
    #indata.displacement=row.Volume
    indata.displacement=calculate_dispacement(displacement_correction=displacement_correction, **sections)
    
    indata.g=g
    indata.kxx=row.KXX
    indata.kyy=row.lpp*0.4
    lcb=calculate_lcb(x=sections['x'], area=sections['area'], lcb_correction=lcb_correction)
    indata.lcb=lcb-row.lpp/2
    indata.lpp=row.lpp
    indata.projectName='loading_condition_id_%i' % row.loading_condition_id
    
    indata.rho=rho
    indata.zcg=row.kg-draught
    #indata.waveFrequenciesMin=0.2
    #indata.waveFrequenciesMax=0.5
    #indata.waveFrequenciesIncrement=0.006
    w=row.omega0/np.sqrt(row.scale_factor)
    indata.waveFrequenciesMin=w*0.5
    indata.waveFrequenciesMax=w*2.0
    N=40
    indata.waveFrequenciesIncrement=(indata.waveFrequenciesMax-indata.waveFrequenciesMin)/N
    indata.runOptions["IE"].set_value(1)
    
    return indata,sections