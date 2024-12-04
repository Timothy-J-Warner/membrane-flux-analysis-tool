import numpy as np
import pandas as pd
import subprocess
import sys


# Import configuration files
config = pd.read_csv('inputs/experiment_configuration.csv')
membrane_properties = pd.read_csv('inputs/membrane_properties.csv')
module_selection = pd.read_csv('inputs/module_selection.csv', dtype=str)

# Allocate variables associated with 'experiment_configuration.csv'
number_load_cells = config['Number of load cells'][0]
pressure_unit = config['Input pressure unit (bar or PSI or MPa)'][0]
smoothing_interval = config['Data smoothing interval (# of points)'][0]
test_duration = config['Test Duration (s)'][0]
data_interval = config['Data Interval (s)'][0]
temperature = config['Test Temperature (C)'][0]

# Allocate variables associated with 'membrane_properties.csv'
mem_type = membrane_properties['Membrane type (HF or FS)'][0]
flat_sheet_area = membrane_properties['Flat sheet area (m^2)'][0]
fiber_length = membrane_properties['Fiber Length (cm)'][0]
fiber_diameter = membrane_properties['Fiber Diameter (mm)'][0]
mem_per_load_cell = membrane_properties['Membranes per load cell'][0]

# Read data and test conditions files
channels = [pd.read_csv(f'data/Channel_{i}.csv') for i in range(number_load_cells)]
df_test_conditions = pd.read_csv('inputs/test_conditions.csv')

# Extract mass data from the channels and convert to numpy arrays
mass_data = [0] * number_load_cells
for i in range(number_load_cells):
    mass_data[i] = channels[i].iloc[:, 1].to_numpy()

# Convert test conditions to numpy arrays
test_time = df_test_conditions['Measurement Start time (24hr time)'].to_numpy()
test_pressure = df_test_conditions['Pressure'].to_numpy()

# Convert test duration and data interval into number of points
data_points = test_duration / data_interval

# Convert pressure to bar if required
if pressure_unit == 'bar':
    test_pressure_bar = test_pressure
elif pressure_unit == 'PSI':
    test_pressure_bar = test_pressure * 0.0689476
elif pressure_unit == 'MPa':
    test_pressure_bar = test_pressure * 10
else:
    print('\nFlux not calculated.\n\nInvalid pressure unit selected.')
    exit()


# Determine the membrane surface area based on geometry
if mem_type == 'FS':
    surface_area = flat_sheet_area * mem_per_load_cell
elif mem_type == 'HF':
    surface_area = np.pi * fiber_diameter / 1000 * fiber_length / 100 * mem_per_load_cell
else:
    print('\nFlux not calculated.\n\nChoose valid membrane geometry (FS or HF)')
    exit()


# Determine density of water from Kell's equation converted to g/ml
density = ((999.83952 + (16.945176 * temperature) - (7.9870401 * (10 ** -3) * (temperature ** 2)) -
            (46.170461 * (10 ** -6) * (temperature ** 3)) + (105.56302 * (10 ** -9) * (temperature ** 4)) -
            (280.54253 * (10 ** -12) * (temperature ** 5))) / (1 + (16.879850 * (10 ** -3) * temperature))) / 1000

# Convert mass to volume
volume_data = [mass_data[i] / density for i in range(number_load_cells)]

# Create rolling average vectors
window_size = smoothing_interval
rolling_averages = [pd.Series(volume).rolling(window=window_size, center=True).mean().to_numpy() for volume in
                    volume_data]

# Preallocate flux vectors
flux = np.zeros((number_load_cells, len(test_time)))

# Calculate the flux values for each of the channels at all the test times specified in test_conditions.csv
for i, start_time in enumerate(test_time):
    for j in range(number_load_cells):
        matching_rows = channels[j][channels[j].iloc[:, 0].str.contains(start_time)]
        if matching_rows.empty:
            print(f'Error - Data missing for Channel_{j} at time {start_time}')
        if not matching_rows.empty:
            time_index = matching_rows.index[0]
            volume_change = (rolling_averages[j][time_index + data_points.astype(int) - 1] -
                             rolling_averages[j][time_index]) / 1000
            flux[j, i] = volume_change / surface_area / (test_duration / 3600)


# Generate statistics from the flux data
average_flux = np.mean(flux, axis=0)
flux_std = np.std(flux, axis=0)
flux_se = flux_std / average_flux * 100

# Create data series of output variables to be exported to a .csv file
df_flux_values = pd.DataFrame({
    'Measurement Start time (24hr time)': df_test_conditions['Measurement Start time (24hr time)'],
    'Pressure (bar)': test_pressure_bar,
})

# Generate a number of flux columns based on number of load cells used
flux_data = pd.DataFrame([])
for i in range(number_load_cells):
    flux_series_data = pd.DataFrame({f'Flux {i} (LMH)': flux[i]})
    flux_data = pd.concat([flux_data, flux_series_data], axis=1)

# Add flux data to outputs dataframe
df_flux_values = df_flux_values.join(flux_data)

# Generate statistics dataframe
flux_stats = pd.DataFrame({
    'Average Flux (LMH)': average_flux,
    'Standard Deviation (LMH)': flux_std,
    'Standard Error (%)': flux_se,
})

# Add statistics to outputs dataframe
df_flux_values = df_flux_values.join(flux_stats)

# Export to .csv file
df_flux_values.to_csv("outputs/flux_values.csv", index=False)

print('\nFlux values saved to outputs/flux_values.csv')

########################################################################################################################

# Additional Modules

# Permeance

if module_selection['Permeance'][0] == 'True':
    subprocess.run([sys.executable, "modules/permeance.py"])


# Flux decline

if module_selection['Flux decline'][0] == 'True':
    subprocess.run([sys.executable, "modules/flux_decline.py"])

