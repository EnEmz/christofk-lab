import requests
import pandas as pd
import re

def get_pathways_for_compound(compound_id):
    """Fetch the list of pathways associated with a given KEGG compound ID."""
    print(f"Fetching pathways for compound ID: {compound_id}")
    base_url = f"https://rest.kegg.jp/link/pathway/{compound_id}"
    response = requests.get(base_url)
    if response.status_code == 200:
        # If pathways are found, process the response
        return response.text.strip()
    else:
        # If there was an error, print an error message
        print(f"Error: HTTP {response.status_code} for KEGG ID {compound_id}")
        return 'N/A'

def get_pathway_names_from_maps(map_ids):
    """Fetch pathway names for given map IDs."""
    pathway_names = []
    for map_id in map_ids:
        url = f"https://rest.kegg.jp/get/{map_id}"
        response = requests.get(url)
        if response.status_code == 200:
            # Extract pathway name from response
            match = re.search(r"NAME\s+(.+)", response.text)
            if match:
                pathway_name = match.group(1)
                pathway_names.append(pathway_name)
                print(f"Found {pathway_name} for {map_id}")
            else:
                pathway_names.append("Name not found")
        else:
            print(f"Error fetching {map_id}: HTTP {response.status_code}")
            pathway_names.append("Fetch error")
    return "; ".join(pathway_names)

def extract_map_ids(pathway_text):
    """Extract map IDs from pathway text."""
    return re.findall(r"map\d{5}", pathway_text)

# Replace with the actual file path on your computer
file_path = 'C:/Users/nmatulionis/Desktop/metabolite_classes_w_KEGG.xlsx'
print(f"Reading Excel file from {file_path}")
df = pd.read_excel(file_path)

print(df)

# Assuming the column with KEGG IDs in your Excel is named 'kegg_id'
print("Processing compound IDs...")
df['kegg_id'] = df['kegg_id'].astype(str)
df['kegg_pathways'] = df['kegg_id'].apply(get_pathways_for_compound)

print("Processing to fetch pathway names...")
df['map_ids'] = df['kegg_pathways'].apply(extract_map_ids)
df['pathway_names'] = df['map_ids'].apply(get_pathway_names_from_maps)

# Optionally, you can drop the 'map_ids' column if it's no longer needed
df.drop('map_ids', axis=1, inplace=True)

# Replace with your desired output path
output_path = 'C:/Users/nmatulionis/Desktop/metabolite_classes_w_KEGG_pathways.xlsx'
print(f"Saving updated Excel file to {output_path}")
df.to_excel(output_path, index=False)

print("All done! The updated Excel file has been saved.")