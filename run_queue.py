import pandas as pd
import plotly.express as px

# Load the dataset
df = pd.read_csv('C://Users//nmatulionis//Desktop//run queue.csv')

# Pre-process the dataset
split_rows = []
for _, row in df.iterrows():
    labs = row['lab_name'].split('/')
    for lab in labs:
        new_row = row.copy()
        new_row['lab_name'] = lab.strip().title()
        split_rows.append(new_row)
df = pd.DataFrame(split_rows)

# Convert 'date_created' to datetime and extract the year
df['year'] = pd.to_datetime(df['date_created']).dt.year

# Group by year and lab_name, summing the number of samples for each lab
grouped_data = df.groupby(['year', 'lab_name'])['num_samples'].sum().reset_index()

# Set fixed size for pie charts
chart_width = 1200
chart_height = 600

# Set the text size
text_size = 16  # Adjust this value as needed

# Generate pie charts for each year
for year in grouped_data['year'].unique():
    yearly_data = grouped_data[grouped_data['year'] == year]
    yearly_total = yearly_data['num_samples'].sum()
    small_labs = yearly_data[yearly_data['num_samples'] / yearly_total < 0.03]

    # Update lab names to include number of samples
    yearly_data['label'] = yearly_data.apply(lambda row: f"{row['lab_name']} ({row['num_samples']})", axis=1)

    # Check if there are any labs in the "Other" category for this year
    if not small_labs.empty:
        other_labs_info = small_labs.apply(lambda row: f"{row['lab_name']} ({row['num_samples']}, {row['num_samples']/yearly_total:.2%})", axis=1).tolist()
        other_samples = small_labs['num_samples'].sum()
        # Add the "Other" category
        yearly_data = yearly_data[yearly_data['num_samples'] / yearly_total >= 0.03]
        yearly_data = yearly_data.append({'label': 'Other', 'num_samples': other_samples}, ignore_index=True)

        # Create the pie chart
        fig = px.pie(yearly_data, values='num_samples', names='label', title=f'Christofk Lab Metabolomics Samples for {year}')
        fig.update_traces(textposition='auto', textinfo='percent+label', insidetextorientation='horizontal')
        fig.update_layout(showlegend=False, width=chart_width, height=chart_height, 
                          uniformtext_minsize=text_size, uniformtext_mode='hide')

        # Add custom annotation for the "Other" category at a fixed position
        other_labs_text = 'Other includes:<br>' + '<br>'.join(other_labs_info)
        fig.add_annotation(text=other_labs_text, x=1.1, y=1, xref='paper', yref='paper', showarrow=False, align='left', valign='top', font=dict(size=text_size))

        # Save as SVG
        fig.write_image(f'Christofk_Metabolomics_{year}.svg', format='svg')
    else:
        # Create the pie chart without "Other" category
        fig = px.pie(yearly_data, values='num_samples', names='label', title=f'Christofk Lab Metabolomics Samples for {year}')
        fig.update_traces(textposition='auto', textinfo='percent+label', insidetextorientation='horizontal')
        fig.update_layout(showlegend=False, width=chart_width, height=chart_height, 
                          uniformtext_minsize=text_size, uniformtext_mode='hide')

        # Save as SVG
        fig.write_image(f'Christofk_Metabolomics_{year}.svg', format='svg')
