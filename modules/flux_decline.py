import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from lmfit import Model, Parameters

# Import .csv data 'flux_values.csv'
plot_data = pd.read_csv('outputs/flux_values.csv')
config = pd.read_csv('inputs/experiment_configuration.csv')
number_load_cells = config['Number of load cells'][0]

try:
    # Attempt to convert to datetime
    pd.to_datetime(plot_data['Measurement Start time (24hr time)'], format='%H:%M:%S')
except ValueError:
    # Warn and return NaT for invalid rows
    print(f"\nInvalid time format detected in: test_conditions.csv 'Measurement Start time (24hr time)'")
    exit()


# Convert the 'Measurement Start time (24hr time)' column to datetime
plot_data['Measurement Start time (24hr time)'] = pd.to_datetime(plot_data['Measurement Start time (24hr time)'],
                                                                 format='%H:%M:%S')

# Calculate the time difference in seconds relative to the initial time
initial_time = plot_data['Measurement Start time (24hr time)'].iloc[0]
time_seconds = (plot_data['Measurement Start time (24hr time)'] - initial_time).dt.total_seconds().to_numpy()
time_minutes = time_seconds/60

# Assign variables from plot_data
flux = plot_data['Average Flux (LMH)'].to_numpy()
flux_std = plot_data['Standard Deviation (LMH)'].to_numpy()

# Define exponential function
def exponential(t, a0, a1, t0):
    return a0 + a1*np.exp(-t/t0)

# Convert to lmfit model
exp_model = Model(exponential)

# Define initial parameter values and bounds
exp_params = Parameters()
exp_params.add('a0', value=2500, min=0)
exp_params.add('a1', value=1500, min=0)
exp_params.add('t0', value=100, min=0)

# Define t values for model plotting
t = np.linspace(min(time_minutes), max(time_minutes), 100)

# Compute non-linear regression
try:
    exp_result = exp_model.fit(flux, exp_params, t=time_minutes, method='least_squares')
except RuntimeError as e:
    print(f"Error during curve fitting: {e}")
    exit()
a0 = exp_result.params['a0'].value
a1 = exp_result.params['a1'].value
t0 = exp_result.params['t0'].value
# LMfit v1.3.2 calculates: residuals = model - data, therefore to plot: residuals = data - model we must use a negative sign.
residuals = -exp_result.residual
r_squared = exp_result.rsquared

# Print fitting statistics if required
# print(f'\nExponential model fitting statistics:\n\n{exp_result.fit_report()}')

# Plot flux decline
fig1 = plt.figure()

x = np.linspace(0, time_minutes[-1], 1001)
average_line, = plt.plot(time_minutes, flux, c='k', label='Average Flux')
if number_load_cells > 1:
    fill_area = plt.fill_between(time_minutes, flux + flux_std, flux - flux_std, color="0.8", label=r'Standard Deviation')

model_line, = plt.plot(t, exp_result.eval(exp_result.params, t=t), '--', c='r', label='Model')

plt.xlabel('Time (mins)')
plt.ylabel(u'Flux (Lm\u207b\u00b2Hr\u207b\u00b9)')
plt.axis((0, max(time_minutes), 0, max(flux + flux_std) * 1.1))
plt.legend(loc='lower right')
plt.savefig('outputs/flux_decline/flux_decline.svg')
plt.savefig('outputs/flux_decline/flux_decline.jpg', dpi=300)

plt.close()

# Plot residuals of exponential model
fig2 = plt.figure()

points = plt.plot(time_minutes, residuals,
                  marker='o', markeredgecolor='k', color='#D9743A', linestyle='None', alpha=0.7)

plt.xlabel('Time (mins)')
plt.ylabel(u'Residual (Lm\u207b\u00b2hr\u207b\u00b9)')
plt.axis((0, max(time_minutes), -max(abs(residuals)) * 1.1, max(abs(residuals)) * 1.1))
plt.savefig('outputs/flux_decline/residuals.svg')
plt.savefig('outputs/flux_decline/residuals.jpg', dpi=300)

plt.close()

# Define parameters of exponential model
model_paremeters = ['a0', 'a1', 't0', 'R2']
parameter_values = np.concatenate(([a0], [a1], [t0], [r_squared]))

# Create database of model parameter values
exponential_model = {
    'Model Parameters': model_paremeters, u'Parameter Values': parameter_values
}

# Save model parameter values
df_outputs = pd.DataFrame(exponential_model)
df_outputs.to_csv("outputs/flux_decline/model_parameters.csv", index=False)

print('\nFlux decline figures saved to outputs/flux_decline')
