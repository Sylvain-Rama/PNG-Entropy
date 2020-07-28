# -*- coding: utf-8 -*-
"""
Created on Fri May  1 17:16:16 2020

@author: Sylvain Rama
Python script made to demonstrate the impacts of quantization and sampling (parameters V and T) on the calculatio of entropy.

From the Materials & Methods in:
    
A quick and easy way to estimate entropy and mutual information for neuroscience

Mickael Zbili(1), Sylvain Rama(2)*

1, Blue Brain Project, École polytechnique fédérale de Lausanne (EPFL) Biotech Campus, Geneva, Switzerland.
2, UCL Queen Square Institute of Neurology, University College London, London, United Kingdom.
*, Correspondence: Sylvain Rama, s.rama@ucl.ac.uk


"""

#%% Imports
import numpy as np
from collections import Counter

from bokeh.plotting import figure
from bokeh.io import output_file, show
from bokeh.layouts import column, row
from bokeh.palettes import inferno
from bokeh.models import Label



#%% Parameters to change

number_of_v_bins = 2 # "v" parameter number of quantization bins
group_of_T_letters = 1 # "T" parameter for number of letters in words


#%% creating Words function
def chunk_string(s, n):
    # return [s[i:i+n] for i in range(len(s)-n+1)]
    # combinations = [s[i:i+n] for i in range(len(s)-n+1)] # For overlapping cominations of letters
    combinations = [s[i:i+n] for i in range(0, len(s), n)] # Non-overlapping letters
    
    
    return combinations # Keep only the non-overlapping letters

#%% Basic settings and creating some white noise
duration = 100
sampling = 1
spread = 8 # Number of possible values in the signal before entropy calculation

length = int(duration / sampling)

np.random.seed(0) # Change seed or remove
noisy_signals = np.random.randint(spread, size = length)

alphabet = list(map(chr, range(65, 65 + number_of_v_bins))) # Generate a list of upper case letters starting by 'A'


#%% Binning the Y values and creating colors for each bin
Y_max = np.max(noisy_signals)
Y_min = np.min(noisy_signals)
Y_bins = np.arange(start=Y_min, stop=Y_max, step=(Y_max-Y_min)/number_of_v_bins) # Quantization bins are homogenous
binned_Y = np.digitize(noisy_signals, Y_bins) # Changing all the signal for the quantized bin values

#Simply preparing the color array for the binned signal.
colors = inferno(number_of_v_bins)
color_list = []
for i in binned_Y:
    color_list.append(colors[i-1])
    
#%% Creating group of letters and counting their occurences

letter_list = ''
for i in binned_Y:
    letter_list = letter_list + (alphabet[i-1])  


word_counts = Counter(chunk_string(letter_list, group_of_T_letters))
words_names = list(word_counts.keys())
words_counts = list(word_counts.values())

# Calculating entropy here.
probabilities = words_counts / np.sum(words_counts)
local_entropy = probabilities * np.log2(probabilities)
entropy = - np.sum(local_entropy)



#%% Plotting the original trace and the downsampled one

output_file('Words & Letter Demo.html')
PlotWidth = 1200
PlotHeight = 600


resampling_figure = figure(title="Signal",
                           x_axis_label='Pixels',
                           y_axis_label='Values',
                           plot_width=int(PlotWidth/2),
                           plot_height=int(PlotHeight/2))

resampling_figure.line(np.arange(0, len(noisy_signals), 1), noisy_signals, 
                       line_width=2, color='black')

resampling_figure.legend.location = "bottom_right"


#%% Plotting the binned values

binning_figure = figure(title="Binned Signal, v= " + str(number_of_v_bins) + " quantization values",
                        x_axis_label='Pixels',
                        y_axis_label="Bin Value",
                        plot_width=int(PlotWidth/2),
                        plot_height=int(PlotHeight/2))

binning_figure.vbar(x=np.arange(0, len(noisy_signals), 1), top=binned_Y, width=1, 
                   fill_color=color_list,
                   line_alpha=0)
                   

binning_figure.legend.location = "bottom_right"

bins_label = Label(x=0, y=np.max(binned_Y), text= 'Bins as letters: ' + str(letter_list))
binning_figure.add_layout(bins_label)


#%% Count & entropy figure
count_figure = figure(title="Words Probabilities with T = " + str(group_of_T_letters) + " letter(s)",
                      x_range=words_names, 
                        x_axis_label='Words',
                        y_axis_label="Probability",
                        plot_width=int(PlotWidth/2),
                        plot_height=PlotHeight)

count_figure.vbar(x=words_names, top=probabilities, width=0.5,
                  fill_color='grey', legend_label="Entropy = " 
                   + ("{:.4f}".format(entropy)) + " bits per pixels")

count_figure.legend.location = "bottom_right"


#%% Assembling the final plot
traces_layout = column(resampling_figure, binning_figure)
figure_layout = row(traces_layout, count_figure)

show(figure_layout)


