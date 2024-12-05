# Changelog

## v0.2.3

- Fixed errors in README.md.
- Prepare documentation for public visibility of the GitHub project

## v0.2.2

- Generalized the permeance module for a user specified number of load cells with 10 colours and 20 markers for plotting.
- Created example data for the permeance module.
- Added module_selection.csv for choosing which additional modules to use.
- Software now prints which outputs have been generated.
- Added flux decline module.
- Provided example data for the permeance module.
- Updated README.md to reflect changes.
- Added a check for time format for flux decline.


## v0.2.1

- Updated README.md to reflect change in repository name.
- Changed file extension of CHANGELOG.txt to .md
- Changed main file name to "membrane-flux-analysis-tool.py"
- Removed redundant test folder
- Added example data show demonstrate to users how to generate permeance data
- Added a modules folder for future plotting functionality
- Added a module calling section at the end of "membrane-flux-analysis-tool.py"
- Integrated a permeance calculation and plotting module into the tool

## v0.2.0

- Renamed variable for clarity.
- Added the ability to specify a testing interval time for the load cells.
- Rearrange location of variables in input files.

## v0.1.3

- Added extra features to the code including selections for pressure input units, number of load cells, membrane
geometry and data smoothing interval.
- Warning messages are present that alert the user if the config.csv file is incorrectly formatted.
- Improved versatility of the code.
- The headings in "test_conditions.csv" are no longer used to identify columns for creating variables.
- The time in "test_conditions.csv" is now always in the first data column and the mass is in the second column.

## v0.1.2

Implemented a conversion from measured mass to volume using Kell's equation and updated all related areas of the code.

## v0.1.1

### Reading CSV Files:

Before: Each channel was read separately into different DataFrames.
After: The channels are read into a list of DataFrames using a list comprehension, reducing redundancy.
Data Extraction:

Before: Data for each channel was converted to numpy arrays separately.
After: Data extraction for each channel was combined into a single list comprehension, streamlining the process.

### Variable Allocation:

Before: Constants were assigned individually from the array.
After: Constants are unpacked directly from the array in a single line.
Rolling Average Calculation:

Before: Rolling averages were calculated using manual loops.
After: Rolling averages are calculated using Pandas' built-in rolling function, making the code more concise and
readable.

### Flux Calculation:

Before: Separate flux vectors were used for each channel.
After: A single 2D array is used for all channels, simplifying the code structure.


### Data Series Creation:

Before: Data series were created and concatenated separately.
After: Data series are combined into a dictionary and directly converted into a DataFrame.

### File Export:

Before: The DataFrame was exported without specifying the index parameter.
After: The DataFrame is exported with index=False to omit the index from the CSV file.

### Debugging

Before: Choosing an analysis time when there was a data time missing would cause the compling to fail.
After: Choosing an analysis time when there was a data time missing results in a zero value for mass at that time
and an error message describing the issue is printed.

## v0.1.0

- Development of minimum viable code to calculate flux based on the provided data and inputs
- Reading time-mass data, inputs and test conditions from .csv files.
- Applying data smoothing to the mass values.
- Finding mass values at the start and end of the specified test windows.
- Calculating flux from changes in mass and membrane properties.
- Generating outputs.csv file from analysis results.