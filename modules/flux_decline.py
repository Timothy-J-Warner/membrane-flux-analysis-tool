import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit

# Import .csv data 'flux_values.csv'
plot_data = pd.read_csv('outputs/flux_values.csv')

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

# Define exponential model for plot
def func(x, a, b, c):
    return a * np.exp(-b * x) + c

# Set non-linear regression bounds and initial guesses
parameter_bounds = ([0, 0, 0], [np.inf, np.inf, np.inf])
initial_guess = [1500, 0.01, 2500]
maxfev = 800

# Calculate non-linear regression for the exponential function with R2 value
popt, pcov = curve_fit(func, time_minutes, flux, p0=initial_guess, bounds=parameter_bounds, maxfev=maxfev)
residuals = flux - func(time_minutes, *popt)
ss_res = np.sum(residuals**2)
ss_tot = np.sum((flux - np.mean(flux)) ** 2)
r_squared = 1 - (ss_res / ss_tot)


# Plot flux decline
fig = plt.figure()

x = np.linspace(0, time_minutes[-1], 1001)
average_line, = plt.plot(time_minutes, flux, c='k', label='Average Flux')
max_line = plt.plot(time_minutes, flux + flux_std, '--', c='k', label='Standard deviation')
min_line = plt.plot(time_minutes, flux - flux_std, '--', c='k')
model_line, = plt.plot(x, func(x, *popt), '--', c='r', label='Model')

plt.xlabel('Time (mins)')
plt.ylabel(u'Flux (Lm\u207b\u00b2Hr\u207b\u00b9)')
plt.axis((0, max(time_minutes), 0, max(flux + flux_std) * 1.1))
plt.legend(loc='lower right')
plt.savefig('outputs/flux_decline/flux_decline.svg')
plt.savefig('outputs/flux_decline/flux_decline.jpg', dpi=300)

plt.close()

# Define parameters of exponential model
model_paremeters = ['a', 'b', 'c', 'R2']
parameter_values = np.concatenate((popt, [r_squared]))

# Create database of model parameter values
exponential_model = {
    'Model Parameters': model_paremeters, u'Parameter Values': parameter_values
}

# Save model parameter values
df_outputs = pd.DataFrame(exponential_model)
df_outputs.to_csv("outputs/flux_decline/model_parameters.csv", index=False)

print('\nFlux decline figures saved to outputs/flux_decline')
