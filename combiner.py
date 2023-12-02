# %%
import pandas as pd
from tkinter.filedialog import askopenfilename
import numpy as np
# %%

def combine_pool():

    file_name = 'all_mets_combined_6.xlsx'
    export_dir = "C:/Users/nmatulionis/Desktop/Python_Script_Dump/"

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)

    # %%
    main_filepath = askopenfilename()
    df_main_pool = pd.read_excel(main_filepath, sheet_name="PoolAfterDF")
    print("The filepath for main df is:\n", main_filepath)

    add_filepath = askopenfilename()
    df_add_pool = pd.read_excel(add_filepath, sheet_name="PoolAfterDF")
    print("The filepath for add df is:\n", add_filepath)

    # %%
    df_main_pool['Compound'] = df_main_pool['Compound'].str.strip()
    df_add_pool['Compound'] = df_add_pool['Compound'].str.strip()

    df_comb = df_main_pool.merge(df_add_pool, on='Compound', how='outer')

    df_comb = df_comb.fillna(0)

    # %%
    df_comb.T.reset_index().T.to_excel(export_dir + file_name, sheet_name='PoolAfterDF', index=False, header=None)

# %%

# %%
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_colwidth', None)

# %%
main_filepath = askopenfilename()
df_main_iso = df = pd.read_excel(main_filepath, sheet_name="Normalized")
print("The filepath for main df is:\n", main_filepath)
    
add_filepath = askopenfilename()
df_add_iso = pd.read_excel(add_filepath, sheet_name="Normalized")
print("The filepath for add df is:\n", add_filepath)

# %%
df_main_iso['Compound'] = df_main_iso['Compound'].str.strip()
df_add_iso['Compound'] = df_add_iso['Compound'].str.strip()

print (df_main_iso['C_Label'].dtypes)
df_main_iso['C_Label'] = df_main_iso['C_Label'].fillna(0).apply(np.int64)
df_add_iso['C_Label'] = df_add_iso['C_Label'].fillna(0).apply(np.int64)

# %%
df_comb = df_main_iso.merge(df_add_iso, on=['Compound','C_Label'], how='outer').fillna(0)


# %%



