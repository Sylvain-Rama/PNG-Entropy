# -*- coding: utf-8 -*-
"""
Created on Fri May 22 11:14:03 2020

@author: Sylvain Rama

This script will convert csv or abf files to PNG, save a direct file and a transposed copy and log the file sizes in a Pandas dataframe.
pyPNG is quite a pain with Numpy arrays, crashing with the error "TypeError: can't set bytearray slice from numpy.ndarray"
As a result, signal entropy of abf file is on the transposed value. Noise entropy is on the direct value. This is reversed when using csv file.

From the Materials & Methods in:
    
A quick and easy way to estimate entropy and mutual information for neuroscience

Mickael Zbili(1), Sylvain Rama(2)*

1, Blue Brain Project, École polytechnique fédérale de Lausanne (EPFL) Biotech Campus, Geneva, Switzerland.
2, UCL Queen Square Institute of Neurology, University College London, London, United Kingdom.
*, Correspondence: Sylvain Rama, s.rama@ucl.ac.uk
"""

#%% Imports 
import pyabf
import numpy as np
import os
import pandas as pd
import png

import tkinter as tk
from tkinter import filedialog


#%% TKinter GUI for Selecting files.
root = tk.Tk()
root.overrideredirect(True)
root.geometry('0x0+0+0')
root.focus_force()

initial_folder = "D:\Papiers\PNG & Entropy\Fig1"
FT = [("All files", "*.*"), ("Abf files", "*.abf"), 
      ("Excel files", "*.xlsx"), ("CSV files", "*.csv")]

ttl = 'Select Files'

file_paths = filedialog.askopenfilenames(parent=root, title=ttl, filetypes=FT, initialdir = initial_folder )

root.withdraw()


# Preparing names and all for the dataframe.
size_values = np.zeros((2, len(file_paths)))
sizes_df = pd.DataFrame(size_values)
names = []
for paths in np.arange(0, len(file_paths), 1):
    names.append(os.path.basename(os.path.normpath(file_paths[paths])))

sizes_df.columns = names
sizes_df.index = ['Size of the file1', 'Size of the File2']

#%% Main loop for each selected file.
for i in range(len(file_paths)):
    
    split = os.path.split(file_paths[i])
    file_extension = os.path.splitext(split[1])[1][1:]
    
      
    # Extracting the signals according to type of files
    if file_extension == 'abf':
        file = pyabf.ABF(file_paths[i])
        
        test=file.data[0]
        noisy_signals=np.reshape(test, (file.sweepCount, file.sweepPointCount))
        # This will give column-wise sweeps, so the standard size is actually the value for the noise.
        # The transposed value is for the signal entropy rate.
        # We cannot transpose it here to have the direct value, as it crashes pyPNG.
        
        
        
        # Binning the signals to U8 if it is an abf.
        noisy_signals = noisy_signals - np.min(noisy_signals)
        noisy_signals = noisy_signals / np.max(noisy_signals)
        noisy_signals = np.uint8(noisy_signals * 255)
        
        
    
    # We suppose the csv files are not above U8.
    if file_extension == 'csv':
        file=pd.read_csv(file_paths[i], dtype='float')
        noisy_signals = file.to_numpy()
        noisy_signals = noisy_signals.T
    
    
    # Transposing here
    # /!\ PyPNG is a pain with Numpy and crashes when transposing the arrays. 
    # See https://github.com/drj11/pypng/issues/91
    # https://github.com/drj11/pypng/commit/c4935f49d4ab1a66983e33ede232ca2f79d34a60
    
    noisy_signals_transposed =  noisy_signals.transpose().copy()
    
      
    name = os.path.splitext(split[1])[0]
    png_name = os.path.join(split[0], name +'.png')
    
    # 2 elements to save: standard and transposed arrays
    to_save = [noisy_signals, noisy_signals_transposed]
    
    # Saving each array as PNG, getting the size of the file and putting it in a Pandas dataframe.
    for j in [0,1]:
            
        png_array = np.array(to_save[j], dtype=np.uint8)
        png.from_array(png_array, mode="L").save(png_name)
        
        # size = os.path.getsize(png_name)
        sizes_df.iloc[j, i] = os.path.getsize(png_name)


#%% Saving the final results as ax Excel sheet
xls_name = os.path.join(split[0], 'File_sizes.xlsx')        
with pd.ExcelWriter(xls_name) as writer:  
        sizes_df.to_excel(writer, sheet_name='PNG Sizes', index=False)
        