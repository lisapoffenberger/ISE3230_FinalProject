#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 12:14:43 2021

Final Project
@author: Lisa Poffenberger
"""

import cvxpy as cp
import pandas as pd
import numpy as np

# ---- Create x matrix of boolean variables----
x = cp.Variable((10,10), boolean = True)

# ---- Calculate cost matrix ----
df = pd.read_excel('CPD_crime_w_latlongs_removing_outliers_adding_weights.xlsx', sheet_name='removing_outliers_from_tableau')
cost_matrix = np.zeros((10,10))
# From a given longitude value of a crime, find the closest longitude 'block' within the x-matrix.
def get_col_of_matrix(long):
    dist_between_xs = 0.001389
    x_11_long = -83.009722+(dist_between_xs/2) # get mid of box to be x_11
    return(round((long - x_11_long)/dist_between_xs))

# From a given latitude value of a crime, find the closest latitude 'block' within the x-matrix.
def get_row_of_matrix(lat):
    dist_between_xs = 0.001389
    x_11_lat = 40.008333-(dist_between_xs/2) # get mid of box to be x_11
    return(round((x_11_lat - lat)/dist_between_xs))

# Create variables 'closest_x_row' and 'closest_x_col' initialized to lat and long values
df['closest_x_row'] = df['Latitude']
df['closest_x_col'] = df['Longitude']

# Find row and column indices of closest x location for all crime data points
for i in range(len(df)):
    #print(i)
    df['closest_x_row'][i] = get_row_of_matrix(df['Latitude'][i])
    df['closest_x_col'][i] = get_col_of_matrix(df['Longitude'][i])
    
# Add up weights at each x point
for i in range(len(cost_matrix)):
    for j in range(len(cost_matrix[0])):
        #print(i,j)
        cost_matrix[i,j] = sum(df[(df['closest_x_row'] == i) & (df['closest_x_col'] == j)]['Weight'])


# ---- Calculate objective function ---- 
def get_obj_func(x, cost_matrix):
    sum = 0
    for i in range(len(cost_matrix)):
        for j in range(len(cost_matrix[0])):
            sum += cost_matrix[i,j]*x[i,j]
    return sum

obj_func = get_obj_func(x,cost_matrix)

# ---- Enter constraints ---- 
constraints = []

# On-campus points should be 0 since no lights need to be placed on campus
constraints.append(x[0,9] == 0)
constraints.append(x[0,8] == 0)
constraints.append(x[0,7] == 0)
constraints.append(x[0,6] == 0)
constraints.append(x[0,5] == 0)

# We can have max 20 lights total
def get_matrix_sum(x):
    x_sum = 0
    for i in range(len(cost_matrix)):
        for j in range(len(cost_matrix[0])):
            x_sum += x[i,j]
    return x_sum
constraints.append(get_matrix_sum(x) <= 20)

# No two lights can be right next to each other
for i in range(9):
    for j in range(10):
        constraints.append(x[i,j] + x[i+1,j] <= 1)

for i in range(10):
    for j in range(9):
        constraints.append(x[i,j] + x[i,j+1] <= 1)
        
# Add non-negativity constraint
for i in range(10):
    for j in range(10):
        constraints.append(x[i,j] >= 0)
    
problem = cp.Problem(cp.Maximize(obj_func), constraints)

problem.solve(solver=cp.GUROBI,verbose = True)

print("obj_func =")
print(obj_func.value)
print("x =")
print(x.value)

