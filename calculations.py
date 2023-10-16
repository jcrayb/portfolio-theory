import gurobipy as gp
import numpy as np
import pandas as pd
import numpy.linalg as la
from gurobipy import GRB
from dev_email import send_email
import timeit

import quarters
import companies

start_year = 1995
end_year = 2019

model = gp.Model('portfolio')
model.params.NonConvex = 2
model.setParam('NonConvex', 2)

a = np.array([0.023734, 1.329796395805503/100])

def get_stock_weights(start_year, end_year, a):
    rfr = quarters.get_mean_rfr_between_years(start_year, end_year)
    gdp = quarters.get_gdp_growth_between_years(start_year, end_year)
    
    returns = pd.read_csv(f'./data/returns/returns_{start_year}-{end_year}.csv').set_index('Unnamed: 0')

    mu1 = returns.mean().to_numpy()
    mu2 = np.array([np.mean(rfr), np.mean(gdp)])
    
    all_companies = returns.columns
    n_companies = returns.shape[1]

    returns['avg_rfr'] = rfr
    returns['gdp_growth'] = gdp

    total_points = returns.shape[1]
    
    returns_array = returns.to_numpy().T.astype(float)
    cov_array = np.cov(returns_array)

    sigma11 = cov_array[0:n_companies, 0:n_companies]
    sigma21 = cov_array[n_companies:total_points, 0:n_companies]
    sigma12 = cov_array[0:n_companies, n_companies:total_points]
    sigma22 = cov_array[n_companies:total_points, n_companies:total_points]

    mu = mu1 + sigma12@la.inv(sigma22)@(a-mu2)
    sigma = sigma11 - sigma12@la.inv(sigma22)@sigma21

    w = model.addMVar(n_companies, name='weights', lb=0, ub=1)
    
    #expectation = model.addVar(name='expected_returns')
    variance = model.addVar(name='variance_returns')
    
    inv_var = model.addVar(name='inverse_variance')
    model.addConstr(variance ==  w@sigma@w, name='integrity')
    model.addConstr(w.sum() ==  1, name='integrity')
    model.addConstr(variance * inv_var ==  1, name='inverse_variance_constr')
    
    
    model.setObjective(w @ mu * inv_var, GRB.MAXIMIZE)
    model.write('./new_sol.lp')
    model.optimize()
    return model.getVars()

for year in range(start_year, end_year):
    weights = get_stock_weights(year, end_year, a)

