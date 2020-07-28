# -*- coding: utf-8 -*-
"""
Created on Fri May 15 12:39:23 2020

@author: Sylvain Rama


This will take the HS & Hn Excel files created by BatchHsHnFromFile.py, plot the values and perform the 3 quadratic extrapolations.
The final values of Rs and Rn will be used to calculate I = Rs - Rn.

From the Materials & Methods in:
    
A quick and easy way to estimate entropy and mutual information for neuroscience

Mickael Zbili(1), Sylvain Rama(2)*

1, Blue Brain Project, École polytechnique fédérale de Lausanne (EPFL) Biotech Campus, Geneva, Switzerland.
2, UCL Queen Square Institute of Neurology, University College London, London, United Kingdom.
*, Correspondence: Sylvain Rama, s.rama@ucl.ac.uk
"""
#%% Imports
import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.io import output_file, show
from bokeh.palettes import inferno
from bokeh.layouts import gridplot, column
from bokeh.models import Div

import tkinter as tk
from tkinter import filedialog
import os

#%% Function for first limit
def first_limit(H_file, H_fit1_df, figure=None):
    for value_v in iterate_on_v:
        
        # Selecting each subset of the dataframe corresponding to the desired v value.
        H_subset = H_file[H_file['v_value'] == v_serie[value_v]]
    
        # Shifting to numpy for the fit.
        H_np_subset = H_subset.to_numpy()
    
        # Building all the Xs values for the fits. Repetition of the same array, as the X values are all the same.
        Xs = H_np_subset[:,1] # Size values are the 2nd column, index = 1
        Xs = 1 / Xs # Inverting the values as the graph shows 1/size
        poly_X = np.insert(Xs, 0, 0) # Adding a 0 to the X set to have the value at this point
       
        # Hard coded indexes to take all the T_values, should be ok as long as I do not change the dataframe structure
        H_Ys = H_np_subset[:, 2:np.shape(H_np_subset)[1]] 
                    
        # Creating a figure for the desired v value.    
        if (v_serie[value_v] == watch_v and figure != None):
            ListY = H_Ys.T.tolist()
            
            for plots in np.arange(0, len(ListY), 1):
                figure.circle(Xs, ListY[plots],
                                legend_label="All T For v="+str(watch_v),
                                line_width=1, color='black', 
                                size=10, fill_color='white')
                       
        #This is the main loop, populating the array with the fitted values
        for T in np.arange(0, len(T_serie), 1):
            if len(s_serie) > 1: # Fit only if there are enough points to do so.
                
                H_coeff_poly = np.polyfit(Xs, H_Ys[:,T], fit_order_1) # Fitting a polynom on the data
                H_poly_Y = np.polyval(H_coeff_poly, poly_X) # Calculating the values for each point and get the value at 0
                         
                # The point at X=0 is at the beginning of the array, putting it at the right place in the dataframe. 
                H_fit1_df.iloc[[value_v], [T]] = H_poly_Y[0] 
                
            else: # If only one point, just take the value of the point.
                H_fit1_df.iloc[[value_v], [T]] = H_Ys[:,T]
                H_poly_Y = H_Ys[:,T]
                
            
            # Showing the fit for the desired v_value
            if (v_serie[value_v] == watch_v and figure != None):
                figure.line(poly_X, H_poly_Y, # Adding points to check the quality of the fit.
                                legend_label="Fits",
                                line_width=2, color=colors[T])
                
                figure.square(0, H_poly_Y[0],
                                   line_width=1, color='black', 
                                   size=10, fill_color='white')
                
    return H_fit1_df


#%% Function for second limit
def second_limit(H_fit1_file, H_fit2_df, figure=None):
    Xs2 = np.asarray(v_serie)
    Xs2 = 1 / Xs2
    Ys2 = H_fit1_file.to_numpy()
    Ys2 = np.array(Ys2, dtype='float')
    
    
    # Main loop for 2nd extrapolation and plotting the figure
    for T2 in np.arange(0, len(T_serie), 1):
        poly_X = np.append(Xs2, 0) # Adding a 0 to the X set to have the value at this point
        
        if len(v_serie) > 1: # Fit only if there are enough points to do so.
            coeff_poly = np.polyfit(Xs2, Ys2[:,T2], fit_order_2) # Fitting a 4th order polynom on the data
            poly_Y = np.polyval(coeff_poly, poly_X) # Calculating the values for each point and get the value at 0
            # The point at X=0 is at the end of the array, putting it at the right place in the dataframe. 
         
            H_fit2_df.iloc[[0],[T2]] = poly_Y[-1]
            
        else: # If only one point, just take the value of the point.
            H_fit2_df.iloc[[0],[T2]] = Ys2[[0], [T2]]
            poly_Y = np.concatenate((Ys2[[0], [T2]] , Ys2[[0], [T2]]))
        
        if figure != None:
            figure.square(Xs2, Ys2[:,T2], # Data points
                                    legend_label="T Values",
                                    line_width=1, color='black', 
                                    size=10, fill_color='white')
        
            figure.line(poly_X, poly_Y, # Lines to check the quality of the fit.
                                    legend_label="Fit",
                                    line_width=2, color=colors[T2])
                        
            figure.diamond(0, poly_Y[-1],
                                    line_width=1, color='black', 
                                    size=15, fill_color='white')
    return H_fit2_df

#%% Function for third limit
def third_limit(H_fit2_file, figure=None):
    Xs3 = np.asarray(T_serie) * 1    # sampling value to get the T in s (sampling is 0.001)
    Xs3 = 1 / Xs3 
    Ys3 = H_fit2_file.to_numpy() 
    Ys3 = Ys3.reshape(len(Xs3))* Xs3 # Ys3 is a 2 dimensional array with only one row.
    
    if figure != None:
        figure.diamond(Xs3, Ys3, legend_label="R",
                   line_width=1, color='black',
                   size=15, fill_color='white')
        
    Xs3 = Xs3[:n_points]
    Ys3 = Ys3[:n_points]
    
    coeff_poly = np.polyfit(Xs3, Ys3, fit_order_3) # Linear fit on the data in the paper.
    poly_X = np.append(Xs3, 0) # Adding a 0 to the X set to have the value at this point.
    poly_Y = np.polyval(coeff_poly, poly_X) # Calculating the values for each point and get the value at 0
    # The point at X=0 is at the end of the array. 
    R = poly_Y[-1] 
    
    if figure != None:
        figure.line(poly_X, poly_Y, 
                    legend_label="R= " + "{:6.4f}".format(R),
                    line_width=2, color='red')
        figure.legend.location = "bottom_right"

    return R


#%% Beginning & general settings



# TKinter GUI for selecting files.
root = tk.Tk()
root.overrideredirect(True)
root.geometry('0x0+0+0')
root.focus_force()

initial_folder = "D:\Python Projects\Entropy Project"
FT = [("Excel files", "*.xlsx")]

ttl = 'Select Excel Files'

file_paths = filedialog.askopenfilenames(parent=root, title=ttl, filetypes=FT, initialdir = initial_folder )

root.withdraw()

# %% Parameters for fit orders
# Value of v to show in the plots
watch_v = 2

# Fit orders for the extrapolations. Change here for fit parameters
fit_order_1 = 1
fit_order_2 = 3

n_points = 5
fit_order_3 = 1


#%% Main Loop
for file_name in file_paths: 


    # Where is the Excel file? And get the Hs & Hn values from the 2 sheets.
    xlsx = pd.ExcelFile(file_name)
    Hs_df = pd.read_excel(xlsx, 'Hs')
    Hn_df = pd.read_excel(xlsx, 'Hn')
    
    # Getting the recorded values for T, v and sizes from the Excel file. Hs & Hn share the same parameters.
    T_serie = Hs_df.columns[2:].astype(int).drop_duplicates().tolist()
    v_serie = Hs_df['v_value'].drop_duplicates().tolist()
    s_serie = Hs_df['size_value'].drop_duplicates().tolist()
    
    # Building the main loops. Has to be defined before calling the functions.
    iterate_on_T = np.arange(0, len(T_serie))
    iterate_on_v = np.arange(0, len(v_serie))
    iterate_on_sizes = np.arange(0, len(s_serie))
    
    
    #%% Preparing first panel of the figure
    
    output_file(file_name[0:-4]+'html')
    PlotWidth = 1200
    PlotHeight = 800
    colors = inferno(len(T_serie))
    
    # Building the Column Names
    column_names= []
    for T in T_serie:
        column_names.append(str(T))
        
    # This will be the data frame for the second graph.
    Hs_fit1_df = pd.DataFrame(index = v_serie, columns=column_names, dtype='float')
    Hn_fit1_df = pd.DataFrame(index = v_serie, columns=column_names, dtype='float')
    
    # Initializing the first graphs for Hs & Hn.
    Hs_figfit_1 = figure(title="1st Hs Extrapolation",
                                x_axis_label='1/Size',
                                y_axis_label='bits')
    
    Hn_figfit_1 = figure(title="1st Hn Extrapolation",
                                x_axis_label='1/Size',
                                y_axis_label='bits')
    
    
    #%% First extrapolation to 0 for Hs & Hn, according to Size. Figures are optional. 
    # All the extrapolation values are stored in Hs_fit1_df & Hn_fit1_df.
    
    
    first_limit(Hs_df, Hs_fit1_df, figure=Hs_figfit_1)
    
    first_limit(Hn_df, Hn_fit1_df, figure=Hn_figfit_1)
    
    
    #%% Preparing second panel of the figure
    
    # Dataframe for 3rg graph.
    Hs_fit2_df = pd.DataFrame(index = [0], columns=T_serie, dtype='float')
    Hn_fit2_df = pd.DataFrame(index = [0], columns=T_serie, dtype='float')
    
    # Preparing the second panel picture
    Hs_figfit_2 = figure(title="2nd Hs Extrapolation",
                                x_axis_label='1/v',
                                y_axis_label='bits')
    
    Hn_figfit_2 = figure(title="2nd Hn Extrapolation",
                                x_axis_label='1/v',
                                y_axis_label='bits')
    
    #%% second extrapolation to 0 for Hs & Hn, according to v quantization values. Figures are optional. 
    # All the extrapolation values are stored in Hs_fit2_df & Hn_fit2_df.
    
    second_limit(Hs_fit1_df, Hs_fit2_df, figure=Hs_figfit_2)
    
    second_limit(Hn_fit1_df, Hn_fit2_df, figure=Hn_figfit_2)
    
    
    
    
    #%% Preparing Third graph and extrapolation
    
    # Preparing the second panel picture
    Hs_figfit_3 = figure(title="3rd Hs & Hn Extrapolation",
                                x_axis_label='1/T (samples-1)',
                                y_axis_label='bits / samples')
    
    Rs = third_limit(Hs_fit2_df, figure=Hs_figfit_3)
    
    Rn = third_limit(Hn_fit2_df, figure=Hs_figfit_3) # Last figure is shared between Hs & Hn.
    
    # Final Grid Layout   
    grid_layout = gridplot([[Hs_figfit_1, Hs_figfit_2, Hs_figfit_3], 
                            [Hn_figfit_1, Hn_figfit_2, None]], 
                           plot_width=400, plot_height=400,
                           toolbar_location="right")
    
    split_path = os.path.split(file_name)
    name = os.path.splitext(split_path[1])[0]
    
    # Figures as svg for editing in vector softwares.
    Hs_figfit_1.output_backend = "svg"
    Hs_figfit_2.output_backend = "svg"
    Hs_figfit_3.output_backend = "svg"
    
    Hn_figfit_1.output_backend = "svg"
    Hn_figfit_2.output_backend = "svg"
    
    show(column(Div(text='<h2>' + name + '</h2>'), grid_layout))