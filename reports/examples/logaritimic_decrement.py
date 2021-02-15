import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from scipy.integrate import solve_ivp
import pandas as pd
from sympy import latex

from rolldecayestimators import equations
from rolldecayestimators import symbols
from rolldecayestimators import lambdas
from rolldecayestimators.substitute_dynamic_symbols import lambdify

lambda_B_1_zeta = lambdify(sp.solve(equations.B_1_zeta_eq, symbols.B_1)[0])

eq_phi1d = sp.Eq(symbols.phi_dot_dot,
      sp.solve(equations.roll_decay_equation_cubic_A,symbols.phi_dot_dot)[0])

accelaration_lambda = lambdify(sp.solve(eq_phi1d,symbols.phi_dot_dot)[0])


def find_peaks(df_state_space):
    
    df_state_space['phi_deg'] = np.rad2deg(df_state_space['phi'])

    mask = (np.sign(df_state_space['phi1d']) != np.sign(np.roll(df_state_space['phi1d'],-1))
           )
    mask[0] = False
    mask[-1] = False

    df_max = df_state_space.loc[mask].copy()
    df_max['id'] = np.arange(len(df_max)) + 1
    return df_max

def calculate_decrements(df_amplitudes):
    ## Calculate decrements:
    df_decrements = pd.DataFrame()
    for i in range(len(df_amplitudes) - 2):
        s1 = df_amplitudes.iloc[i]
        s2 = df_amplitudes.iloc[i + 2]
        decrement = s1 / s2
        decrement.name = s1.name
        df_decrements = df_decrements.append(decrement)

    return df_decrements

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

phi_0 = 35
phi_a_deg = np.linspace(0,phi_0, 100)
phi_a = np.deg2rad(phi_a_deg)
B_1 = 0.05
B_2 = 0.9
A_44 = 1.0
B_1A = B_1/A_44
B_2A = B_2/A_44
C_1 = 5.0
C_1A = C_1/A_44
omega0=lambdas.omega0_linear_lambda(A_44=A_44, C_1=C_1)
t = np.linspace(0,6,1000000)
phi_0=np.deg2rad(phi_0)
phi_01d=0

## State space:
model = RollDecayStateSpace(B_1A=B_1A, B_2A=B_2A, C_1A=C_1A)
df_state_space = model.simulate(t=t, phi0=phi_0, phi1d0=phi_01d)
df_max = find_peaks(df_state_space)
df_amplitudes = df_max.copy()

## Calculate decrements:
df_decrements = calculate_decrements(df_amplitudes=df_amplitudes)

## Calculate damping from decrements:
df_amplitudes['zeta_n'] = 1 / (2 * np.pi) * np.log(df_decrements['phi'])
## Convert to B damping [Nm*s]
df_amplitudes['B'] = lambda_B_1_zeta(A_44=A_44, omega0=omega0, zeta=df_amplitudes['zeta_n'])
df_amplitudes['B'] = df_amplitudes['B'].astype(float)


## Try different amplitudes:

df_amplitudes['phi_a'] = df_amplitudes['phi'].abs()
df_amplitudes_1 = df_amplitudes.copy()
df_amplitudes_2 = df_amplitudes.copy()
df_amplitudes_3 = df_amplitudes.copy()
df_amplitudes_4 = df_amplitudes.copy()
df_amplitudes_2['phi_a'] = np.roll(df_amplitudes['phi_a'],-1)
df_amplitudes_2['id'] = np.roll(df_amplitudes['id'],-1)
df_amplitudes_3['phi_a'] = np.roll(df_amplitudes['phi_a'],-2)
df_amplitudes_3['id'] = np.roll(df_amplitudes['id'],-2)
df_amplitudes_4['phi_a'] = (df_amplitudes['phi_a'] + np.roll(df_amplitudes['phi_a'],-1) + 
                           np.roll(df_amplitudes['phi_a'],-2)
                           )/3
df_amplitudes.dropna(inplace=True)
df_amplitudes_1.dropna(inplace=True)
df_amplitudes_2.dropna(inplace=True)
df_amplitudes_3.dropna(inplace=True)
df_amplitudes_4.dropna(inplace=True)
## Plotting:
df_amplitudes['phi_a_deg'] = np.rad2deg(df_amplitudes['phi_a'])
df_amplitudes_1['phi_a_deg'] = np.rad2deg(df_amplitudes_1['phi_a'])
df_amplitudes_2['phi_a_deg'] = np.rad2deg(df_amplitudes_2['phi_a'])
df_amplitudes_3['phi_a_deg'] = np.rad2deg(df_amplitudes_3['phi_a'])
df_amplitudes_4['phi_a_deg'] = np.rad2deg(df_amplitudes_4['phi_a'])
phi_a_ = np.array([df_amplitudes_1['phi_a'].min(),df_amplitudes_2['phi_a'].min(),df_amplitudes_3['phi_a'].min(),
          df_amplitudes_1['phi_a'].max(),df_amplitudes_2['phi_a'].max(),df_amplitudes_3['phi_a'].max()])
B_e = lambdas.B_e_lambda(B_1=B_1, B_2=B_2, omega0=omega0, 
                                          phi_a=phi_a_)

def show():
    show_figure_1()
    show_figure_2()

def show_figure_1():
    
    ## First figure:
    fig,ax=plt.subplots()
    label=r'$B_1$:%0.1f, $B_2$:%0.1f, $C_1$:%0.1f' % (B_1,B_2,C_1)
    df_state_space.plot(y='phi_deg', style='--', ax=ax, label=label)

    df_max.plot(y='phi_deg', style='.', label='peaks', ax=ax)
    ax.set_ylabel(r'$\phi$ $[deg]$')
    ax.set_xlabel(r'time $[s]$')
    ax.grid(True)
    ax.legend(loc='upper left')

    for time, row in df_max.iterrows():
        text=r'$\phi_{a,%i}$' % row['id']
        ax.annotate(text, xy=(time,row['phi_deg']), xytext=(time,0.98*row['phi_deg']))

    ax = fig.add_axes([0.63, 0.60, .25, .25], zorder=1)
    df_zoom = df_state_space.loc[5.4:5.9]
    ax.annotate(text, xy=(time,row['phi_deg']), xytext=(time,0.98*row['phi_deg']))
    df_zoom.plot(y='phi_deg', style='--', ax=ax)
    df_max.loc[df_zoom.index[0]:df_zoom.index[-1]].plot(y='phi_deg', style='.', label='peaks', ax=ax)
    ax.grid()
    ax.get_legend().set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([]);

def show_figure_2():

    ## Second figure
    fig,ax=plt.subplots()
    ax.plot(np.rad2deg(phi_a_), B_e, '--',
            label=r'$%s$' % latex(equations.B_e_equation))

    df_amplitudes_1.plot(x='phi_a_deg', y='B', label='A', style='.-', ax=ax)
    df_amplitudes_2.plot(x='phi_a_deg', y='B', label='B', style='.-', ax=ax)
    df_amplitudes_3.plot(x='phi_a_deg', y='B', label='C', style='.-', ax=ax)
    df_amplitudes_4.plot(x='phi_a_deg', y='B', label='D', style='.-', ax=ax)

    for df_ in [df_amplitudes_1,df_amplitudes_2,df_amplitudes_3]:
        for time, row in df_.iterrows():
            text='%i' % row['id']
            ax.annotate(text, xy=(row['phi_a_deg'],row['B']))

    ax.set_ylabel(r'$B$ $[Nm*s]$')
    ax.set_xlabel(r'$\phi_a$ $[deg]$')
    ax.legend()

    ylim = ax.get_ylim()
    ax.set_ylim((0,ylim[1]))
    ax.grid()
