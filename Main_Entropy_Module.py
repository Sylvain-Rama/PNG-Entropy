# -*- coding: utf-8 -*-
"""
Created on Thu May  7 14:30:38 2020

@author: Sylvain Rama

Main Module to calculate Entropy by the direct way with correction of the sampling bias.

From the Materials & Methods in:
    
A quick and easy way to estimate entropy and mutual information for neuroscience

Mickael Zbili(1), Sylvain Rama(2)*

1, Blue Brain Project, École polytechnique fédérale de Lausanne (EPFL) Biotech Campus, Geneva, Switzerland.
2, UCL Queen Square Institute of Neurology, University College London, London, United Kingdom.
*, Correspondence: Sylvain Rama, s.rama@ucl.ac.uk
"""

#%% Imports & Global variables
import numpy as np
import pandas as pd
from collections import Counter




# Reason the v value (number of quantization bins) is limited. You can increase it here.

ALPHABET = list(map(chr, range(65, 330)))  


#%% Combinations of a letter sequence in sequences of n following letters.
def chunk_string(s, n):
    # combinations = [s[i:i+n] for i in range(len(s)-n+1)] # For overlapping combinations of letters
    combinations = [s[i:i+n] for i in range(0, len(s), n)] # Non-overlapping letters
    
    return combinations


#%% Direct calculation of Hs & Hn, main version
def calculate_HsHn(noisy_signals, v=2, size=1, T=1):
    
    # Will be used to cut the signal in 'sizes' part.
    length_signal = noisy_signals.shape[0] 
    repetitions = noisy_signals.shape[1]
    
    # Replacing values by v binned values. Bins are homogenous.
    signal_max = np.max(noisy_signals)
    signal_min = np.min(noisy_signals)
    bins = np.arange(start=signal_min, stop=signal_max, step=(signal_max-signal_min)/v)
    binned_signals = np.digitize(noisy_signals, bins)
    
    # Keeping a small chunk of size 1/s * length
    chunk_size = int(size*length_signal)
    chunk = binned_signals[:chunk_size,:]
    
    # Creating the letter list for every sweep and combining them into words.
    Hs_letter_list = []
    Hs_word_list = []
    Hs_word_count = []
    Hs_array = np.empty(repetitions)
    
    # Start to calculate Hs
    for sweeps in np.arange(0, repetitions,1):
        letter_list = ''
        for bins in chunk[:,sweeps]:
            letter_list += ALPHABET[bins-1]
        
        #List of every sweep as list of letters corresponding to bins
        Hs_letter_list.append(letter_list) 
                
        # Cutting the list in x fragments of T size.
        Hs_words = chunk_string(letter_list, T)
        # removing the last element, as it may not be of T letters
        Hs_words.pop()
        # List of list of every fragments, to be used after by Hn
        Hs_word_list.append(Hs_words)
        
        # Counting all occurences of words of T letters
        word_counts = Counter(Hs_words)
        words_counts = list(word_counts.values())
        Hs_word_count.append(words_counts)
        
        # Calculating the entropy Hs from the probabilities of the words.
        probabilities = words_counts / np.sum(words_counts)
        local_entropy = probabilities * np.log2(probabilities)
        Hs = - np.sum(local_entropy)
        Hs_array[sweeps] = Hs
            
    Hs = np.mean(Hs_array)
    
    # Transposing the Hs word list to get the Hn list
    Hn_transposed_letter_list = [list(x) for x in zip(*Hs_word_list)] 
    
    # Preparing the Hn array.            
    Hn_array=np.empty(len(Hn_transposed_letter_list))
   
    # Calculating the entropy Hn from the probabilities of the words.
    for ticks in np.arange(0,len(Hn_transposed_letter_list),1):
        Hn_word_counts = Counter(Hn_transposed_letter_list[ticks])
        Hn_words_counts = list(Hn_word_counts.values())

        Hn_probabilities = Hn_words_counts / np.sum(Hn_words_counts)
        Hn_local_entropy = Hn_probabilities * np.log2(Hn_probabilities)
        Hn = - np.sum(Hn_local_entropy)
        Hn_array[ticks] = Hn
    
    Hn = np.mean(Hn_array)

    return Hs, Hn


#%% Main function to iterate through T, v and size and calculate the values of Hs & Hn.
# It will fill 2 pandas dataframes with the Hs & Hn values : Hs_df & Hn_df.

def populate_HsHn(noisy_signals,
                  T_serie = [1, 2, 4, 6, 8, 10, 12, 14],
                  v_serie = [2, 4, 6, 8, 10, 12],
                  s_serie = [1, 0.95, 0.9, 0.8, 0.7, 0.6, 0.5]):
    
    
    # Preparing the names for the Pandas dataframes.
    column_names = ['size_value']
    for T in T_serie:
        column_names.append(str(T))
    v_column = np.tile(v_serie, len(s_serie))
    s_column = np.repeat(s_serie, len(v_serie))
        
    
    iterate_on_T = np.arange(0, len(T_serie))
    iterate_on_v = np.arange(0, len(v_serie))
    iterate_on_sizes = np.arange(0, len(s_serie))
    
    # Initializing the 3D arrays.
    Hs_values = np.zeros((len(s_serie), len(v_serie), len(T_serie)))
    
    Hn_values = np.zeros((len(s_serie), len(v_serie), len(T_serie)))
    
    # Main loop for Hs & Hn calculation & populating the arrays.
    for value_v in iterate_on_v:
        for value_T in iterate_on_T:
            for value_s in iterate_on_sizes:
                # Function to measure entropy, just before this function.
                Hs, Hn = calculate_HsHn(noisy_signals, 
                                          v = v_serie[value_v], 
                                          size = s_serie[value_s], 
                                          T = T_serie[value_T])
                
                Hs_values[value_s, value_v, value_T] = Hs
                Hn_values[value_s, value_v, value_T] = Hn
                
    # Reshaping, shifting to DataFrame.            
    # Rehsaping the 3d arrays in 2D form. Both Hs & Hn arrays have the same dimensions.       
    m,n,r = Hs_values.shape
    Hs_values_2D = np.column_stack((np.repeat(np.arange(m),n), Hs_values.reshape(m*n,-1)))
    Hn_values_2D = np.column_stack((np.repeat(np.arange(m),n), Hn_values.reshape(m*n,-1)))
    
    # Changing the s_column as it was simply the indexes
    Hs_values_2D[:, 0] = s_column
    Hn_values_2D[:, 0] = s_column
    # Making it a Pandas dataframe.
    Hs_df = pd.DataFrame(Hs_values_2D)
    Hn_df = pd.DataFrame(Hn_values_2D)
    # Renaming the column names, adding the column for v_values
    Hs_df.columns = column_names
    Hs_df.insert(loc=0, column='v_value', value=v_column)
    
    Hn_df.columns = column_names
    Hn_df.insert(loc=0, column='v_value', value=v_column)
    
    return Hs_df, Hn_df # All the final values in Pandas dataframes.
