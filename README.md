# PNG-Entropy
Repository made for the PNG &amp; Entropy Paper

From the Materials & Methods in:
    
A quick and easy way to estimate entropy and mutual information for neuroscience

Mickael Zbili(1), Sylvain Rama(2)*

1, Blue Brain Project, École polytechnique fédérale de Lausanne (EPFL) Biotech Campus, Geneva, Switzerland.

2, UCL Queen Square Institute of Neurology, University College London, London, United Kingdom.

*, Correspondence: Sylvain Rama, rama.sylvain@gmail.com


List of Python scripts:
All scripts were done in Anaconda 3.7 with Numpy, Pandas, pyABF, pyPNG and Bokeh.

pyABF: https://pypi.org/project/pyabf/

pyPNG: https://pypi.org/project/pypng/

Demo_EntropyByWordsLetters.py: 

Python script made to demonstrate the impact of quantization and sampling (parameters v and T) on the calculation of entropy.

BatchHsHnFromFile.py:

Main script to calculate all the possible values of entropy according to the T, v and Size parameters.
This will ask for a list of abf or csv data files and will create an Excel Spreadsheet with all Hs & Hn values for each data file.

PlotHsHnFromExcel.py:

This will take the HS & Hn Excel files created by BatchHsHnFromFile.py, plot the values and perform the 3 quadratic extrapolations.
The final values of Rs and Rn will be used to calculate I = Rs - Rn.

Main_Entropy_Module.py:

Main Module to calculate Entropy by the direct way with correction of the sampling bias. This is needed by the two previous scripts.

BatchSaveAsPNG.py:

This script will convert csv or abf files to PNG, save a direct file and a transposed copy and log the PNG Rates (file sizes divided by the number of pixels in the image) in an Excel file.

GenerateRandomNoise.py:

This will create Gaussian White noise and sort it or not. Then save it as a csv, for later analyze of Hs & Hn or save it as PNG.

PNG_Scripts.llb: 

series of Labview scripts made using Labview 2017 and Vision 2017.

They are used for figures 2, 3, 4, 5 and 6. See the top level vi in the llb for description.
