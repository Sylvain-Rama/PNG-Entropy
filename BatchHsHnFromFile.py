# -*- coding: utf-8 -*-
"""
Created on Sat May 16 15:39:13 2020

@author: Sylvain Rama

Main script to calculate all the possible values of entropy according to the T, v and Size parameters.
This will ask for a list of abf or csv data files and will create an Excel Spreadsheet with all Hs & Hn values for each data file.

From the Materials & Methods in:
    
A quick and easy way to estimate entropy and mutual information for neuroscience

Mickael Zbili(1), Sylvain Rama(2)*

1, Blue Brain Project, École polytechnique fédérale de Lausanne (EPFL) Biotech Campus, Geneva, Switzerland.
2, UCL Queen Square Institute of Neurology, University College London, London, United Kingdom.
*, Correspondence: Sylvain Rama, s.rama@ucl.ac.uk
"""

#%% Imports
import Main_Entropy_Module as em

import pandas as pd
import os
import pyabf
import numpy as np
import tkinter as tk
from tkinter import filedialog

#%% TKinter GUI for selecting files.
root = tk.Tk()
root.overrideredirect(True)
root.geometry('0x0+0+0')
root.focus_force()

initial_folder = "C:/" # Change the default directory here.
FT = [("All files", "*.*"), ("Abf files", "*.abf"), 
      ("Excel files", "*.xlsx"), ("CSV files", "*.csv")]

ttl = 'Select Files'

file_paths = filedialog.askopenfilenames(parent=root, title=ttl, filetypes=FT, initialdir = initial_folder )

root.withdraw()


#%% Loop for each selected file

for file_path in file_paths:
    
    split = os.path.split(file_path)
    file_extension = os.path.splitext(split[1])[1][1:]
    
    file_name = os.path.basename(os.path.normpath(file_path))
    
    # Extracting the signals according to type of files
    if file_extension == 'abf':
        file = pyabf.ABF(file_path)
        
        signal=file.data[0]
        noisy_signals=np.reshape(signal, (file.sweepCount, file.sweepPointCount))
        
        noisy_signals = noisy_signals.T # My algorithm is column-wise...
    
    if file_extension == 'csv':
        file=pd.read_csv(file_path, dtype='float')
        noisy_signals = file.to_numpy()
 

    
    # Function to calculate all the HS & Hn values. Change the values for T, v and Size.
    Hs_df, Hn_df = em.populate_HsHn(noisy_signals,
                          T_serie = [1, 2, 3, 4, 5, 6, 7, 8], # T parameter, number of possible letters per words
                          v_serie = [2, 4, 8, 16, 32, 64, 128, 256], # v parameter, number of possible quantization bins
                          s_serie = [1, 0.9, 0.8, 0.7, 0.6, 0.5] # Size parameter, for extrapolation to infinite sizes.
                          ) 
    
    # Saving the values in an Excel file
    split_path = os.path.split(file_path)
    name = os.path.splitext(split_path[1])[0]
    # Which will have this name        
    H_file_name = os.path.join(split[0], 'Hs_Hn ' + name +'.xlsx')
    
    # Each Excel file will have Hs on the first Spreadsheet and Hn on the second spreadsheet
    with pd.ExcelWriter(H_file_name) as writer:  
        Hs_df.to_excel(writer, sheet_name='Hs', index=False)
        Hn_df.to_excel(writer, sheet_name='Hn', index=False)
        
    print( "File created: " + H_file_name)


