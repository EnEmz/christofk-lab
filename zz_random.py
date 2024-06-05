import pandas as pd
import os
import re
from tkinter.filedialog import askopenfilename

hek_std_peak_area_met_list_pos = [
    'acetyl-carnitine',
    'alanine',
    'arginine',
    'asparagine',
    'betaine',
    'carnitine',
    'choline',
    'citrulline',
    'creatine',
    'creatinine',
    'cystathionine',
    'glycine',
    'leucine / isoleucine',
    'lysine',
    'methionine',
    'NAD+',
    'NADP+',
    'nicotinamide',
    'phenylalanine',
    'phosphocholine',
    'proline',
    'propionyl-carnitine',
    'S-adenosyl-methionine',
    'serine',
    'threonine',
    'valine',
]

hek_std_peak_area_met_list_neg = [
    '6-phosphogluconic acid',
    'acetyl-CoA',
    'ADP',
    'alpha-ketoglutarate',
    'aspartate',
    'ATP',
    'CDP',
    'cis-aconitate',
    'CMP',
    'CTP',
    'dihydroxyacetone-phosphate',
    'fructose-1;6-bisphosphate',
    'fructose-1-phosphate',
    'fructose-6-phosphate',
    'fructose',
    'fumarate',
    'GDP',
    'glucose-6-phosphate',
    'glucose',
    'glutamate',
    'glutamine',
    'glyceraldehyde-3-phosphate',
    'glycerol-3-phosphate',
    'GMP',
    'GSH',
    'GSSG',
    'GTP',
    'histidine',
    'hydroxyglutarate',
    'IMP',
    'lactate',
    'lauric acid',
    'malate',
    'myristic acid',
    'N-acetylglucosamine-phosphate',
    'N-acetylglutamate',
    'NADH',
    'NADPH',
    'oleic acid',
    'palmitic acid',
    'phosphoenolpyruvate',
    'phosphoglycerate',
    'pyruvate',
    'rib/ribul/xylul-ose-phosphate',
    'S-adenosyl-homocysteine',
    'succinate',
    'sedoheptulose-7-phoshate',
    'taurine',
    'trifluoromethanesulfonate',
    'tryptophan',
    'tyrosine',
    'UDP-glucuronic acid',
    'UDP',
    'UDP-N-acetylglucosamine',
    'uric acid',
    'UTP',
    'xylonic acid'
]

desktop_path = os.path.expanduser('~/Desktop')
read_folder = 'full_list'
export_folder = 'hek_list'

read_path = os.path.join(desktop_path, read_folder)
export_path = os.path.join(desktop_path, export_folder)

# Function to filter files based on metabolite lists
def filter_files():
    for filename in os.listdir(read_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(read_path, filename)
            df = pd.read_csv(file_path)
            
            # Determine if the file is positive or negative based on filename
            if 'pos' in filename:
                met_list = hek_std_peak_area_met_list_pos
            elif 'neg' in filename:
                met_list = hek_std_peak_area_met_list_neg
            else:
                continue
            
            # Extract the base name for matching
            def base_name(name):
                match = re.match(r"^(.+?)(?:\sM\d+)?$", name)
                return match.group(1) if match else name
            
            # Filter the rows
            df_filtered = df[df['name'].apply(lambda x: base_name(x) in met_list)]
            
            # Construct the export file path with '_hek' added before the file extension
            base, ext = os.path.splitext(filename)
            export_file_path = os.path.join(export_path, f"{base}_hek{ext}")
            
            # Save the filtered data
            df_filtered.to_csv(export_file_path, index=False)

# Run the filtering function
filter_files()

print("Filtering and exporting completed.")