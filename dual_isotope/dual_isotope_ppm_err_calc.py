# %%
import pandas as pd
from tkinter.filedialog import askopenfilename
import os

# %%
# Function to calculate PPM error margin
def calculate_ppm_error_margin(mz, ppm):
    return mz * ppm / 1e6

# Function to get m/z range from a given m/z value and error margin
def get_mz_range(mz, error_margin):
    return mz - error_margin, mz + error_margin

# Function to calculate the PPM difference
def calculate_ppm_difference(mz1, mz2):
    return abs(mz1 - mz2) / mz1 * 1e6

# Read the CSV file
filepath = askopenfilename()
df_mz = pd.read_csv(filepath)

# List to collect the results
matches = []

# Constants for the mass error and retention time threshold
MASS_ERROR_PPM = 15
RT_THRESHOLD = 0.3

# Iterate over the DataFrame
for i in range(len(df_mz) - 1):
    for j in range(i + 1, len(df_mz)):
        mz_i = df_mz.at[i, 'mz']
        mz_j = df_mz.at[j, 'mz']
        rt_i = df_mz.at[i, 'rt']
        rt_j = df_mz.at[j, 'rt']

        # Calculate the error margins for each m/z
        error_i = calculate_ppm_error_margin(mz_i, MASS_ERROR_PPM)
        error_j = calculate_ppm_error_margin(mz_j, MASS_ERROR_PPM)
        
        # Calculate the m/z ranges
        mz_i_min, mz_i_max = get_mz_range(mz_i, error_i)
        mz_j_min, mz_j_max = get_mz_range(mz_j, error_j)
        
        # Check if the ranges overlap, indicating a match within the error margin
        if ((mz_i_min <= mz_j <= mz_i_max) or (mz_j_min <= mz_i <= mz_j_max)) and abs(rt_i - rt_j) < RT_THRESHOLD:
            ppm_error = calculate_ppm_difference(mz_i, mz_j)
            matches.append({
                'name_1': df_mz.at[i, 'name'], 'mz_1': mz_i,
                'name_2': df_mz.at[j, 'name'], 'mz_2': mz_j,
                'ppm_error': ppm_error
                
            })
            print(f"Added {df_mz.at[i, 'name']} and {df_mz.at[j, 'name']}.")

# Create DataFrame from the matches list
matches_df = pd.DataFrame(matches)

                
matches_df.to_csv('C:/Users/nmatulionis/Desktop/CN_metabolites_within_15ppm_pos.csv', index=False)

# %%



