# Membrane Flux Analysis Tool

## Table of Contents

- About The Project
- Built With
- Features
- Getting Started
  - Prerequisites
  - Installation
- Usage
- Limitations
- Configuration
- Modules
  - Permeance
  - Flux decline
- Contributing
- Roadmap
- License
- Contact
- Acknowledgements

## About The Project

The program was written to rapidly calculate the water flux of hollow fiber membranes from time-mass data generated by
data-logging load cells, input values describing the properties of the membranes, and specified test conditions
including time at which the flux testing window should begin and the test pressure at the test time. The program 
converts mass to volume based on test room temperature and Kell's equation [[1]](https://www.doi.org/10.1021/je60064a005), 
applies data smoothing to reduce fluctuations in the volume data calculated from the load cells then uses changes in 
volume and properties of the membranes to calculate flux based on specified test conditions.

## Built With

- [Python](https://www.python.org/) - A high-level programming language used for general-purpose programming.

## Features

- Feature 1: Reading time-mass data, calculating flux and recording results in flux_values.csv file.
- Feature 2: Permeance module to calculate permeance and plot flux vs pressure.
- Feature 3: Flux decline module to plot and model a decrease in flux over time.

## Getting Started

### Prerequisites

- Python 3.7+
- Libraries:
  - numpy
  - pandas
  - matplotlib
  - SciPy
  - lmfit

### Installation

Clone or fork the GitHub repository from https://github.com/Timothy-J-Warner/membrane-flux-analysis-tool.

## Usage

- Update the files membrane_properties.csv, test_conditions.csv and experiment_configuration.csv
- Data files in folder "data" have name with form Channel_i.csv where i is a sequential integer starting from 0.
- Define additional modules to use by modifying module_selection.csv
- Run the python script "membrane-flux-analysis-tool.py"
- Flux data stored in outputs.csv
- Outputs from modules stored in individual folders in outputs directory

## Limitations
- The time-mass data files must be named 'Channel_0.csv', 'Channel_1.csv', etc.
- If channel data is in HH:MM:SS format then test_conditions.csv must have time in HH:MM:SS format.
- HH:MM:SS format is required for flux decline plotting.
- Pressure measurements must be recorded during the experiment manually to be included in the test conditions file.


## Configuration

### Data files:
The time-mass data files must be named 'Channel_0.csv', 'Channel_1.csv', etc. and placed in the directory
'data'. The time data column should contain a time formatted HH:MM:SS but does not matter if a date, fractional
second or additional data identifier is present or not.

### membrane_properties.csv file contains:
  - Membrane type (HF or FS). Input HF for hollow fiber membranes and FS for flat sheet membranes
  - Flat sheet area (m^2). Only utilized when flat sheet membrane is selected
  - Hollow fiber membrane length (Length (cm)). Only utilized when hollow fiber membrane is selected
  - Hollow fiber membrane outside diameter (Diameter (mm)). Only utilized when hollow fiber membrane is selected
  - Number of membranes tested simultaneously (number of membranes flowing to a single load cell)

### experiment_configuration.csv file contains:
  - Number of load cells
  - Input pressure unit (bar or PSI or MPa)
  - The length of time over which the mass change will be measured for flux calculations (Test Duration (s))
  - The data interval at which the load cell collects data (Data Interval (s))
  - The temperature of the room at which the test took place (C)
  - The number of data points over which a rolling average of the data applies (Data smoothing interval (# of points))

### test_conditions.csv file contains:
  - The time at which the flux measurement begins
  - The pressure over the measurement duration 

### module_selection.csv file contains:
- The names of individual modules
- True or False (case-sensitive) values to define which modules are used.

## Modules

### Permeance
The permeance module takes flux calculated at each time specified in test_conditions.csv and plots it again the pressure
(bar) at that time. It performs linear regression on the data from each load cell, plots trendlines and records the 
regression parameters in permeance_values.csv in directory outputs/permeance. The permeance plot is saved as a .jpg and
.svg file in the same directory. It is recommended to define test conditions at different pressures for this module.

### Flux Decline
The flux decline module plots the decrease in flux over time during membrane separation due to fouling or compression. 
The average flux at each time point is plotted along with the measurement standard deviation (for two or more load cells) 
and an established exponential model from the literature superimposed on the data [[2]](https://www.doi.org/10.1016/j.desal.2014.04.010).
The parameters of the exponential model are saved as model_parameters.csv in directory outputs/flux_decline along with
the flux decline and residual plots in .jpg and .svg format. The time in test_conditions.csv must be in HH:MM:SS format, 
and it is recommended that the times are regular intervals and the pressure kept constant.

## Contributing

Contact Timothy Warner to contribute or fork the repository at 
https://github.com/Timothy-J-Warner/membrane-flux-analysis-tool.

## Roadmap

- [x] Development of minimum viable code to calculate flux based on the provided data and inputs
- [ ] Graphical user interface (GUI)
    - [ ] Modify inputs file based on GUI
    - [ ] Select data files for analysis
    - [ ] Run button for the tool
- [x] Provide additional setting such as:
  - [x] Choosing between flat sheet and hollow fiber membrane
  - [x] Choosing the number of data files to read and analyse – between 1 and 9 files
  - [x] Choosing input units for pressure – metric vs imperial
- [x] Improved functionality
    - [x] Linear regression of flux values to calculate permeance of each data set
    - [x] Plotting of flux vs pressure
      - [x] Saving of image files
    - [x] Generation of useful test statistics
    - [x] Generalising the code, so it can function with different time intervals and different rolling average windows.
    - [x] Allow for the addition of pressure data logging
- [x] Quality Control
  - [x] Eliminated known bug when time values are missing from the raw data.
  - [x] Ensure the code functions as expected.
  - [x] Provide useful error messages and guide users to error free use of the software.
- [ ] Packaging of code to standalone application
    - [ ] Generate .exe so the program can be run without installing python

## Licence

This software is licensed under the MIT License. See LICENSE for more details.

## Contact

Timothy Warner - warnet2@mcmaster.ca

## Acknowledgements

- Project contributors: Timothy Warner, Nathan Mullins, Charles-Francois de Lannoy
- [Python](https://www.python.org/) - A high-level programming language used for general-purpose programming.
- [NumPy](https://numpy.org/) - A fundamental package for scientific computing with Python.
- [pandas](https://pandas.pydata.org/) - A powerful data analysis and manipulation library for Python.
- [Matplotlib](https://matplotlib.org/) - A comprehensive library for creating static, animated, and interactive visualizations in Python.
- [SciPy](https://scipy.org/) - Fundamental algorithms for scientific computing in Python
- [LMfit](https://lmfit.github.io/lmfit-py/) - A set of tools for non-linear least-squares minimization and curve fitting.

## References

- [[1]](https://www.doi.org/10.1021/je60064a005) G. S. Kell, “Density, thermal expansivity, and compressibility of liquid 
water from 0 deg. to 150 deg. C - Correlations and tables for atmospheric pressure and saturation reviewed and 
expressed on 1968 temperature scale,” J. Chem. Eng. Data, vol. 20, no. 1, pp. 97–105, Jan. 1975, doi: 10.1021/je60064a005.
- [[2]](https://www.doi.org/10.1016/j.desal.2014.04.010) Y. A. Hussain and M. H. Al-Saleh, “A viscoelastic-based model for 
TFC membranes flux reduction during compaction,” Desalination, vol. 344, pp. 362–370, Jul. 2014, doi: 10.1016/j.desal.2014.04.010.


