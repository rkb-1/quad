import csv
import os
import sys
import numpy as np
import pandas 
import scipy.interpolate as interp

# Settings
des_time_step = 0.0025                 #400hz             # Desired time step that you want to upscale the data to  
#des_time_step = 0.001    # 1khz
#des_time_step =  0.005             #200 hz

search_dir = '/home/dfki.uni-bremen.de/rkumar/quadruped-developments/mjbots-quad/quad/trajectories/' # Set search directory
log_ident = 'planarProblemBackflip_23012023_frameCorrected'                                   # Set log file identifier
# acc_thresh = 10                                   # Threshold for acceleration values; all exceeding nodes are deleted
print('desired timestep: ', des_time_step)
print('search directory: ', search_dir)
WITHFILTER = 'filter' in sys.argv

# Find all log files that shall be upscaled
def get_all_log_files(log_ident, path):
    result = []
    alreadyFilled = False
    for root, dirs, files in os.walk(path):
         for filename in files:
            if log_ident in filename and not 'TaskSpace' in filename and not 'interp' in filename:
                result.append(os.path.join(root, filename))
            if 'filled' in filename: 
                alreadyFilled = True
    return result, alreadyFilled
logsToUpscale, alreadyFilled = get_all_log_files(log_ident, search_dir)


# Upscale all log files
numFiles = len(logsToUpscale)
count = 1
print('#######################')
print('Upscaling in process...')
print('#######################')
for fileName in logsToUpscale:
    print('file ' + str(count) + '/' + str(numFiles) + ': ' + str(fileName))
    # Load the data
    data = pandas.read_csv(fileName)
    cols = list(data.columns) 
    if 't[s]' not in data.columns:
        print('Error: Your data does not contain a ''t[s]'' column with time stamps!')
    # Interpolate the data
    interpolator = {col: interp.CubicSpline(data['t[s]'], data[col]) for col in cols}
    total_time = data.iloc[-1]['t[s]']
    data_interp = []
    for t in np.arange(0, total_time+des_time_step, des_time_step):
        data_interp.append([interpolator[col](t).item() for col in cols])
    # Write interpolated data
    with open(os.path.splitext(fileName)[0]+'_interp.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(cols) # Write header
        writer.writerows(data_interp[:-1]) # Write data
    count += 1
print('Done.')
