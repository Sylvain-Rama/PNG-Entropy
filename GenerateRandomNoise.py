# -*- coding: utf-8 -*-
"""
Created on Mon May 11 14:53:40 2020

@author: Sylvain Rama

This will create Gaussian White noise and sort it or not. Then save it as a csv, for later analyze of Hs & Hn.

From the Materials & Methods in:
    
A quick and easy way to estimate entropy and mutual information for neuroscience

Mickael Zbili(1), Sylvain Rama(2)*

1, Blue Brain Project, École polytechnique fédérale de Lausanne (EPFL) Biotech Campus, Geneva, Switzerland.
2, UCL Queen Square Institute of Neurology, University College London, London, United Kingdom.
*, Correspondence: Sylvain Rama, s.rama@ucl.ac.uk

"""
#%% Imports
import numpy as np
import pandas as pd
import png
import os

from bokeh.plotting import figure
from bokeh.io import output_file, show


#%% Basic settings and creating the Gaussian signals with noise
duration = 100
sampling = 1
spread = 4 # Amplitude of the noise
repetitions = 100
sorted_signal = False #Choose True for sorting the signal
name = 'Noise'

length = int(duration / sampling)

np.random.seed(0) # Change seed or remove
raw = np.random.randint(spread, size = length * repetitions, dtype='int')
if sorted_signal:
    raw = np.sort(raw)
    name='Sorted'
noisy_signals = raw.reshape(length, repetitions) # Reshaping the signal as [duration , repetitions]

png_array = np.array(noisy_signals, dtype=np.uint8) # Conversion to 256 grey values

png.from_array(png_array, mode="L").save("D:/Python Projects/Entropy Project/Testpng.png")

size = os.path.getsize("D:/Python Projects/Entropy Project/Testpng.png")
print("Signal as PNG: " + str(size) + " Bytes")

#%% Saving the noisy signals as csv, for later use.
df = pd.DataFrame(noisy_signals, dtype='float')

df.to_csv(name + ' d=' + str(duration) + ' s=' + str(sampling) 
        + ' sp=' + str(spread) + ' n=' + str(repetitions) + '.csv', index=None)

#%% Showing the noise
output_file('RandomNoise.html')
PlotWidth = 400
PlotHeight = 400

noise_figure = figure(title=name,
                      x_range=(0, repetitions), y_range=(0, duration),
                      x_axis_label='Pixels', y_axis_label='Pixels',
                      plot_width=int(PlotWidth), plot_height=int(PlotHeight))


noise_figure.image(image=[noisy_signals], x=0, y=0, 
                    dw=repetitions, dh=duration, 
                    palette="Greys8", level='image')

noise_figure.grid.grid_line_width = 0
noise_figure.toolbar.logo = None
noise_figure.toolbar_location = None

show(noise_figure)
