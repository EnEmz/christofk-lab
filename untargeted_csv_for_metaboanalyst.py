import pandas as pd
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Hide the main tkinter window
Tk().withdraw()

# Function to modify the CSV file
def modify_csv(filepath):
    # Check if the file exists and is a CSV file
    if not os.path.isfile(filepath) or not filepath.lower().endswith('.csv'):
        raise ValueError("The file must exist and should be a CSV file.")

    df = pd.read_csv(filepath)

    if 'row m/z' not in df.columns or 'row retention time' not in df.columns:
        raise ValueError("The CSV file must contain 'row m/z' and 'row retention time' columns.")

    df['Sample'] = df['row m/z'].astype(str) + '__' + df['row retention time'].astype(str)

    # Insert the 'Group' row after the header
    group_values = ['Group'] + ['insert group'] * (len(df.columns) - 1)
    group_row = pd.DataFrame([group_values], columns=df.columns)
    df = pd.concat([group_row, df], ignore_index=True)

    # Remove the original 'row m/z' and 'row retention time' columns from the column order list
    column_order = ['Sample'] + [col for col in df if col not in ['row m/z', 'row retention time']]
    df = df[column_order]

    # Create the new output path by appending '_metaboanalyst' before the file extension
    base, extension = os.path.splitext(filepath)
    outputpath = base + '_metaboanalyst' + extension
    df.to_csv(outputpath, index=False)

    return outputpath

# Ask the user to select a file
filepath = askopenfilename()
if filepath:
    output_path = modify_csv(filepath)
    print(f"Modified file saved to: {output_path}")
else:
    print("No file selected.")