import numpy as np
import pandas as pd

# Read csv files
channels = [pd.read_csv(f'data/Channel_{i}.csv') for i in range(3)]
df_constants = pd.read_csv('inputs/constants.csv')
df_test_conditions = pd.read_csv('inputs/test_conditions.csv')

# Extract relevant data from the channels and convert to numpy arrays
mass_data = [channel[f'Weight [Bridge Input Ch:{i} -> 1046 S/N:583686]'].to_numpy() for i, channel in
             enumerate(channels)]
constants = df_constants.to_numpy()
test_time = df_test_conditions['Measurement Start time (24hr time)'].to_numpy()
test_pressure = df_test_conditions['Pressure (PSI)'].to_numpy()

# Allocate variables associated with 'constants.csv'
length, diameter, fiber_number, duration, temperature = constants[0]

# Calculate the hollow fiber surface area
surface_area = np.pi * diameter / 1000 * length / 100 * fiber_number

# Determine density of water from Kell's equation converted to g/ml
density = ((999.83952 + (16.945176 * temperature) - (7.9870401 * (10 ** -3) * (temperature ** 2)) -
            (46.170461 * (10 ** -6) * (temperature ** 3)) + (105.56302 * (10 ** -9) * (temperature ** 4)) -
            (280.54253 * (10 ** -12) * (temperature ** 5))) / (1 + (16.879850 * (10 ** -3) * temperature))) / 1000

# Convert mass to volume
volume_data = [mass_data[i] / density for i in range(3)]

# Convert pressure from PSI to bar
test_pressure_bar = test_pressure * 0.0689476

# Create rolling average vectors
window_size = 10
rolling_averages = [pd.Series(volume).rolling(window=window_size, center=True).mean().to_numpy() for volume in
                    volume_data]

# Preallocate flux vectors
flux = np.zeros((3, len(test_time)))

# Calculate the flux values for each of the channels at all the test times specified in test_conditions.csv
for i, start_time in enumerate(test_time):
    for j in range(3):
        matching_rows = channels[j][channels[j]['Date'].str.contains(start_time)]
        if matching_rows.empty:
            print(f'Error - Data missing for Channel_{j} at time {start_time}')
        if not matching_rows.empty:
            time_index = matching_rows.index[0]
            volume_change = (rolling_averages[j][time_index + duration.astype(int) - 1] -
                             rolling_averages[j][time_index]) / 1000
            flux[j, i] = volume_change / surface_area / (duration / 3600)

average_flux = np.mean([flux[0], flux[1], flux[2]], axis=0)
flux_std = np.std([flux[0], flux[1], flux[2]], axis=0)
flux_se = flux_std / average_flux * 100


# Create data series of output variables to be exported to a .csv file
output_data = {
    'Measurement Start time (24hr time)': df_test_conditions['Measurement Start time (24hr time)'],
    'Pressure (bar)': test_pressure_bar,
    'Flux 0 (LMH)': flux[0],
    'Flux 1 (LMH)': flux[1],
    'Flux 2 (LMH)': flux[2],
    'Average Flux (LMH)': average_flux,
    'Standard Deviation (LMH)': flux_std,
    'Standard Error (%)': flux_se,
}

# Create output DataFrame and export to .csv file
df_outputs = pd.DataFrame(output_data)
df_outputs.to_csv("outputs/outputs.csv", index=False)
