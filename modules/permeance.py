import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# Import .csv data 'flux_values.csv'
plot_data = pd.read_csv('outputs/flux_values.csv')

# Import configuration files
config = pd.read_csv('inputs/experiment_configuration.csv')
number_load_cells = config['Number of load cells'][0]

# Predefine the colours that may be used for the plots
colours = ['#D00000', '#3185FC', '#1B998B', '#FFBA08', '#FF9B85', '#5D2E8C', '#76A53C', '#FF7B9C', '#46237A', '#8FE388']

# Specify the possible formats usable by the plots
markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', 'P', '*', 'h', 'H', 'X', 'd', '|', '_', '+', 'x', '.', ',']

# Convert data frames into usable nd arrays
pressure = plot_data['Pressure (bar)'].to_numpy()
flux = [plot_data[f'Flux {i} (LMH)'].to_numpy() for i in range(number_load_cells)]

# Preallocate variable for the linear regression
lin_reg = [stats.linregress(pressure, flux[i]) for i in range(number_load_cells)]
intercept = np.zeros(number_load_cells)
slope = np.zeros(number_load_cells)
r2 = np.zeros(number_load_cells)

# Calculate linear regression for each of the load cells
for i in range(number_load_cells):
    intercept[i] = lin_reg[i].intercept
    slope[i] = lin_reg[i].slope
    r2[i] = lin_reg[i].rvalue ** 2

# Plot flux (LMH) vs pressure (bar)
fig = plt.figure(layout="constrained")
for i in range(number_load_cells):
    points, = plt.plot(pressure, flux[i], marker=markers[i], color=colours[i], label=f'Flux {i}', linestyle='None')
    trend, = plt.plot(pressure, slope[i] * pressure + intercept[i], '--', c=colours[i])

# Format plot
plt.xlabel('Pressure (bar)')
plt.ylabel(u'Flux (Lm\u207b\u00b2Hr\u207b\u00b9)')
plt.axis((0, max(pressure) * 1.1, 0, np.max(flux) * 1.1))
plt.savefig('outputs/permeance/permeance.svg')
plt.savefig('outputs/permeance/permeance.jpg', dpi=300)

# Record linear regression parameters
slope_output = np.append(slope, [np.mean(slope), np.std(slope)], axis=None)
intercept_output = np.append(intercept, [np.mean(intercept), np.std(intercept)], axis=None)
r2_output = np.append(r2, [np.mean(r2), np.std(r2)], axis=None)

# Generate 'Specimen' list
specimen_list = [str(i + 1) for i in range(number_load_cells)]
specimen_list.extend(['Mean', 'Standard Deviation'])

# Generate permeance outputs database
permeance_output = { 'Specimen': specimen_list,
                     'Permeance (LMH/bar)': slope_output,
                     'Intercept (LMH/bar)': intercept_output,
                     'r^2': r2_output
                     }

# Save permeance outputs
df_permeance_output = pd.DataFrame(permeance_output)
df_permeance_output.to_csv('outputs/permeance/permeance_values.csv', index=False)

print('\nPermeance values and figures saved to outputs/permeance')
