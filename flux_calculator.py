import numpy as np
import pandas as pd

# read csv files
df_Channel_0_data = pd.read_csv('data/Channel_0.csv')
df_Channel_1_data = pd.read_csv('data/Channel_1.csv')
df_Channel_2_data = pd.read_csv('data/Channel_2.csv')
df_constants = pd.read_csv('constants.csv')
df_test_conditions = pd.read_csv('test_conditions.csv')

# create np.arrays with mass data, constants and test conditions
mass_0_data = pd.DataFrame(df_Channel_0_data['Weight [Bridge Input Ch:0 -> 1046 S/N:583686]']).to_numpy()
mass_1_data = pd.DataFrame(df_Channel_1_data['Weight [Bridge Input Ch:1 -> 1046 S/N:583686]']).to_numpy()
mass_2_data = pd.DataFrame(df_Channel_2_data['Weight [Bridge Input Ch:2 -> 1046 S/N:583686]']).to_numpy()
constants = pd.DataFrame(df_constants).to_numpy()
test_time = pd.Series(df_test_conditions['Measurement Start time (24hr time)']).to_numpy()
test_pressure = pd.Series(df_test_conditions['Pressure (PSI)']).to_numpy()

# allocate variables associated with 'constants.csv'
length = constants[0, 0]  # length in cm
diameter = constants[0, 1]  # diameter in mm
fiber_number = constants[0, 2]  # integer
duration = constants[0, 3]  # time in seconds

# calculate the hollow fiber surface area
surface_area = 2 * np.pi * diameter / 2 / 1000 * length / 100 * fiber_number

# convert pressure from PSI to bar
test_pressure_bar = test_pressure*0.0689476

# create rolling average vectors
rolling_average_0 = np.zeros_like(mass_0_data, dtype=float)
rolling_average_1 = np.zeros_like(mass_1_data, dtype=float)
rolling_average_2 = np.zeros_like(mass_2_data, dtype=float)

# window (seconds) over which the data is smoothed (averaged)
window_size = 10

# fill array with averaged values - must be done for all three channels due to the fact they could be different sizes
for i in range(window_size // 2, len(mass_0_data) - window_size // 2):
    rolling_average_0[i] = np.mean(mass_0_data[i - window_size // 2 + 1: i + window_size // 2 + 1])

for i in range(window_size // 2, len(mass_1_data) - window_size // 2):
    rolling_average_1[i] = np.mean(mass_1_data[i - window_size // 2 + 1: i + window_size // 2 + 1])

for i in range(window_size // 2, len(mass_2_data) - window_size // 2):
    rolling_average_2[i] = np.mean(mass_2_data[i - window_size // 2 + 1: i + window_size // 2 + 1])

# preallocate flux vectors
flux_0 = np.zeros(len(test_time))
flux_1 = np.zeros(len(test_time))
flux_2 = np.zeros(len(test_time))

# Calculate the flux values for each of the channels at all the test times specified in test_conditions.csv
for i in range(0, len(test_time)):
    # Define the substring to match the specific test time for each loop
    substring = df_test_conditions['Measurement Start time (24hr time)'].iloc[i]

    # Find rows where the 'Date' (time) column contains the substring
    matching_row_0 = df_Channel_0_data[df_Channel_0_data['Date'].str.contains(substring)]
    matching_row_1 = df_Channel_1_data[df_Channel_1_data['Date'].str.contains(substring)]
    matching_row_2 = df_Channel_2_data[df_Channel_2_data['Date'].str.contains(substring)]

    # Get the indices of the matching rows
    time_index_0 = matching_row_0.index
    time_index_1 = matching_row_1.index
    time_index_2 = matching_row_2.index

    # calculate the change in mass (kg) over Test Duration time specified in 'constants.csv' by calculating
    # ( mass(final) - mass(initial) ) / 1000 which includes unit conversion from g to kg.
    mass_change_0 = (rolling_average_0[time_index_0 + duration.astype(int) - 1] - rolling_average_0[time_index_0])/1000
    mass_change_0 = mass_change_0.item()
    mass_change_1 = (rolling_average_1[time_index_1 + duration.astype(int) - 1] - rolling_average_1[time_index_1])/1000
    mass_change_1 = mass_change_1.item()
    mass_change_2 = (rolling_average_2[time_index_2 + duration.astype(int) - 1] - rolling_average_2[time_index_2])/1000
    mass_change_2 = mass_change_2.item()

    # calculate the flux converting seconds to hours
    flux_0[i] = mass_change_0 / surface_area / (duration / 3600)
    flux_1[i] = mass_change_1 / surface_area / (duration / 3600)
    flux_2[i] = mass_change_2 / surface_area / (duration / 3600)

# Create data series of output variables to be exported to a .csv file
output_time = df_test_conditions['Measurement Start time (24hr time)']
output_pressure_bar = pd.Series(test_pressure_bar, name='Pressure (bar)')
output_flux_0 = pd.Series(flux_0, name='Flux 0 (LMH)')
output_flux_1 = pd.Series(flux_1, name='Flux 1 (LMH)')
output_flux_2 = pd.Series(flux_2, name='Flux 2 (LMH)')

# Concatenate output data series into output data frame
df_outputs = pd.concat([output_time, output_pressure_bar, output_flux_0, output_flux_1, output_flux_2], axis=1)

# Export outputs to .csv file
df_outputs.to_csv(f"outputs.csv")

print(df_outputs)
