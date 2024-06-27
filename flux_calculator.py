import numpy as np
import pandas as pd

# Configure input parameters
config = pd.read_csv('inputs/config.csv')
mem_type = config['Membrane type (HF or FS)'][0]
number_loadcells = config['Number of load cells'][0]
press_unit = config['Input pressure unit (bar or PSI or MPa)'][0]
smoothing_interval = config['Data smoothing interval (s)'][0]

# Read data, constants and test conditions files
channels = [pd.read_csv(f'data/Channel_{i}.csv') for i in range(number_loadcells)]
df_constants = pd.read_csv('inputs/constants.csv')
df_test_conditions = pd.read_csv('inputs/test_conditions.csv')

# Extract mass data from the channels and convert to numpy arrays
mass_data = [0] * number_loadcells
for i in range(number_loadcells):
    mass_data[i] = channels[i].iloc[:, 1].to_numpy()

# Convert constants and test conditions to numpy arrays
constants = df_constants.to_numpy()
test_time = df_test_conditions['Measurement Start time (24hr time)'].to_numpy()
test_pressure = df_test_conditions['Pressure'].to_numpy()

# Convert pressure to bar if required
if press_unit == 'bar':
    test_pressure_bar = test_pressure
elif press_unit == 'PSI':
    test_pressure_bar = test_pressure * 0.0689476
elif press_unit == 'MPa':
    test_pressure_bar = test_pressure * 10
else:
    print('\nFlux not calculated.\n\nInvalid pressure unit selected.')
    exit()

# Allocate variables associated with 'constants.csv'
surface_area, length, diameter, number_membranes, duration, temperature = constants[0]

# Determine the membrane surface area based on geometry
if mem_type == 'FS':
    surface_area = surface_area * number_membranes
elif mem_type == 'HF':
    surface_area = np.pi * diameter / 1000 * length / 100 * number_membranes
else:
    print('\nFlux not calculated.\n\nChoose valid membrane geometry (FS or HF)')
    exit()


# Determine density of water from Kell's equation converted to g/ml
density = ((999.83952 + (16.945176 * temperature) - (7.9870401 * (10 ** -3) * (temperature ** 2)) -
            (46.170461 * (10 ** -6) * (temperature ** 3)) + (105.56302 * (10 ** -9) * (temperature ** 4)) -
            (280.54253 * (10 ** -12) * (temperature ** 5))) / (1 + (16.879850 * (10 ** -3) * temperature))) / 1000

# Convert mass to volume
volume_data = [mass_data[i] / density for i in range(number_loadcells)]

# Create rolling average vectors
window_size = smoothing_interval
rolling_averages = [pd.Series(volume).rolling(window=window_size, center=True).mean().to_numpy() for volume in
                    volume_data]

# Preallocate flux vectors
flux = np.zeros((number_loadcells, len(test_time)))

# Calculate the flux values for each of the channels at all the test times specified in test_conditions.csv
for i, start_time in enumerate(test_time):
    for j in range(number_loadcells):
        matching_rows = channels[j][channels[j].iloc[:, 0].str.contains(start_time)]
        if matching_rows.empty:
            print(f'Error - Data missing for Channel_{j} at time {start_time}')
        if not matching_rows.empty:
            time_index = matching_rows.index[0]
            volume_change = (rolling_averages[j][time_index + duration.astype(int) - 1] -
                             rolling_averages[j][time_index]) / 1000
            flux[j, i] = volume_change / surface_area / (duration / 3600)


# Generate statistics from the flux data
average_flux = np.mean(flux, axis=0)
flux_std = np.std(flux, axis=0)
flux_se = flux_std / average_flux * 100

# Create data series of output variables to be exported to a .csv file
df_outputs = pd.DataFrame({
    'Measurement Start time (24hr time)': df_test_conditions['Measurement Start time (24hr time)'],
    'Pressure (bar)': test_pressure_bar,
})

# Generate a number of flux columns based on number of load cells used
flux_data = pd.DataFrame([])
for i in range(number_loadcells):
    flux_series_data = pd.DataFrame({f'Flux {i} (LMH)': flux[i]})
    flux_data = pd.concat([flux_data, flux_series_data], axis=1)

# Add flux data to outputs dataframe
df_outputs = df_outputs.join(flux_data)

# Generate statistics dataframe
output_stats = pd.DataFrame({
    'Average Flux (LMH)': average_flux,
    'Standard Deviation (LMH)': flux_std,
    'Standard Error (%)': flux_se,
})

# Add statistics to outputs dataframe
df_outputs = df_outputs.join(output_stats)

# Export to .csv file
df_outputs.to_csv("outputs/outputs.csv", index=False)
