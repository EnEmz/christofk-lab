import pandas as pd
import plotly.express as px

# Load the dataset
df = pd.read_csv('C://Users//nmatulionis//Desktop//run queue.csv')

# Preprocess the data by grouping and summing num_samples for each lab by year
grouped_data = df.groupby(['year', 'lab_name'])['num_samples'].sum().reset_index()

# Create a pie chart for each year
for year in grouped_data['year'].unique():
    yearly_data = grouped_data[grouped_data['year'] == year]
    
    # Sort labs by the number of samples
    yearly_data = yearly_data.sort_values('num_samples', ascending=False)
    
    # Generate labels for the pie chart
    yearly_data['label'] = yearly_data['lab_name'] + ' (' + yearly_data['num_samples'].astype(str) + ')'
    
    # Create the pie chart
    fig = px.pie(yearly_data, values='num_samples', names='label',
                 title=f'Sample Distribution for {year}',
                 color_discrete_sequence=px.colors.sequential.RdBu)
    
    # Update the layout of the chart
    fig.update_layout(template="plotly_white",
                      legend=dict(orientation="h", yanchor="bottom", y=-0.3))
    
    # Save the figure as an SVG file
    fig.write_image(f"pie_chart_{year}.svg", format='svg')
