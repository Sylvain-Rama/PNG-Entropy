# -*- coding: utf-8 -*-
"""
Created on Fri May 22 11:14:03 2020

@author: Sylvain Rama
"""

import pyabf
import numpy as np
import os
import pandas as pd
import png

import tkinter as tk
from tkinter import filedialog

# Selecting files.
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

size_values = np.zeros((2, len(file_paths)))
sizes_df = pd.DataFrame(size_values)
names = []
for paths in np.arange(0, len(file_paths), 1):
    names.append(os.path.basename(os.path.normpath(file_paths[paths])))

sizes_df.columns = names
sizes_df.index = ['Size of the file1', 'Size of the File2']

for i in range(len(file_paths)):
    
    split = os.path.split(file_paths[i])
    file_extension = os.path.splitext(split[1])[1][1:]
    
      
    # Extracting the signals according to type of files
    if file_extension == 'abf':
        file = pyabf.ABF(file_paths[i])
        
        test=file.data[0]
        noisy_signals=np.reshape(test, (file.sweepCount, file.sweepPointCount))
        
        noisy_signals = noisy_signals.T
    
    if file_extension == 'csv':
        file=pd.read_csv(file_paths[i], dtype='float')
        noisy_signals = file.to_numpy()
    
    # Binning the signals to U8.
    # noisy_signals = noisy_signals - np.min(noisy_signals)
    # noisy_signals = noisy_signals / np.max(noisy_signals)
    # noisy_signals = np.uint8(noisy_signals * 255)
    
    
    # length = np.shape(noisy_signals)[0] * np.shape(noisy_signals)[1]
    
    noisy_signals_transposed =  noisy_signals.transpose().copy()
    
    # name = os.path.splitext(split[1])[0]
    # png_name = os.path.join(split[0], name +'.png')
    
    # png_array = np.array(noisy_signals_transposed, dtype=np.uint8)
    # png.from_array(png_array, mode="L").save(png_name)
    
    # size = os.path.getsize(png_name)
    # sizes_df.iloc[0,i] = size
    
   
    name = os.path.splitext(split[1])[0]
    png_name = os.path.join(split[0], name +'.png')
    # to_save = [noisy_signals, noisy_signals_transposed][elements]
    
    png_array = np.array(noisy_signals_transposed, dtype=np.uint8)
    png.from_array(png_array, mode="L").save(png_name)
    
    # size = os.path.getsize(png_name)
    # sizes_df.iloc[elements, i] = size

# xls_name = os.path.join(split[0], 'File_sizes.xlsx')        
# with pd.ExcelWriter(xls_name) as writer:  
#         sizes_df.to_excel(writer, sheet_name='PNG Sizes', index=False)
        