import warnings
warnings.filterwarnings('ignore')

import numpy as np
import matplotlib.pyplot as plt
plt.style.use('paper')
import sympy as sp
from scipy.integrate import solve_ivp
import pandas as pd

from rolldecayestimators import equations
from rolldecayestimators import symbols
from rolldecayestimators import lambdas
from rolldecayestimators.substitute_dynamic_symbols import lambdify

eqs = [
    equations.B_1_zeta_eq,    
    equations.analytical_solution,
      ]

analytical_solution_B_1 = sp.Eq(symbols.phi,
                                sp.simplify(sp.solve(eqs,symbols.zeta,symbols.phi)[0][1]))
analytical_lambda = lambdify(sp.solve(analytical_solution_B_1,symbols.phi)[0])

def show(omega0_lambda, accelaration_lambda):
    

    class RollDecayStateSpace():
    
        def __init__(self,B_1A, C_1A, B_2A=0, B_3A=0, C_3A=0, C_5A=0):
            self.parameters = {
                'B_1A':B_1A, 
                'B_2A':B_2A, 
                'B_3A':B_3A, 
                'C_1A':C_1A, 
                'C_3A':C_3A, 
                'C_5A':C_5A}

        def time_step(self,t,states):

            phi = states[0]
            phi1d = states[1]
            phi2d = accelaration_lambda(**self.parameters, phi=phi, phi1d=phi1d)

            d_states_dt = np.array([phi1d, phi2d])
            return d_states_dt

        def simulate(self,t,phi0=np.deg2rad(10),phi1d0=0):

            initial_state = [phi0,phi1d0]

            t_span = [t[0], t[-1]]

            result = solve_ivp(fun=self.time_step, t_span=t_span,  y0=initial_state, t_eval=t)
            assert result.success
            df_result = pd.DataFrame(index=result.t, data=result.y.T, columns = ['phi','phi1d'])
            return df_result

    A_44 = 1.0
    B_1 = 0.3
    C_1 = 5.0
    B_1A = B_1/A_44
    C_1A = C_1/A_44
    omega0=omega0_lambda(A_44=A_44, C_1=C_1)

    t = np.linspace(0,10,1000)
    phi_0=np.deg2rad(10)
    phi_01d=0

    ## State space:
    model = RollDecayStateSpace(B_1A=B_1A, C_1A=C_1A)

    df_state_space = model.simulate(t=t, phi0=phi_0, phi1d0=phi_01d)

    ## Analytical
    phi_analytical = analytical_lambda(A_44=A_44, B_1=B_1, omega0=omega0, phi_0=phi_0, phi_01d=phi_01d, 
                                      t=t)
    
    fig,ax=plt.subplots()   
    ax.plot(t, phi_analytical, '-', label='analytical')
    
    df_state_space.plot(y='phi', style='--', ax=ax, label='numerical')
    ax.set_ylabel(r'$\phi$ $[rad]$')
    ax.set_xlabel(r'time $[s]$')
    ax.grid(True)
    ax.legend()
    