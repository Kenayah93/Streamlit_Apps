import streamlit as st
import pandas as pd
import geopandas as gpd
import folium as fl
from streamlit_folium import st_folium
import plotly.express as px

# Page configuration (ensure this is the first Streamlit command in your script)
st.set_page_config(page_title="Geospatial Dashboard", layout="wide")

# Load the data
geospatial_data = gpd.read_file("https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world.geojson")
population_data = pd.read_csv("https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/main/13_final_project_data/world_population.csv")

# App title
st.title("Interactive Dashboard: Global Population")

# Country selection
countries = population_data['Country/Territory'].unique()
selected_country = st.selectbox("Select a country:", sorted(countries))

# Filter data for the selected country
country_data = population_data[population_data['Country/Territory'] == selected_country]
country_geometry = geospatial_data[geospatial_data['name'] == selected_country]

# Check the columns to make sure the 'Capital' column exists
st.write(country_geometry.columns)  # Display the column names to inspect

# Display key statistics
if not country_data.empty and not country_geometry.empty:
    st.subheader(f"Statistics for {selected_country}")
    total_area = country_geometry['geometry'].area.iloc[0] / 10**5 #   Convert square meters to square kilometers
    
    # Assuming population data is in columns like '2022 Population', '2020 Population', etc.
    population_2022_column = '2022 Population'  # Adjust this column name after inspecting the dataset
    population_2022 = country_data[population_2022_column].values[0]  # Get population for 2022
    
    # Calculate population density and percentage of world population
    density = population_2022 / total_area
    world_population_percentage = (population_2022 / population_data[population_data[population_2022_column].notna()]['World Population Percentage'].sum())  # * 100  Adjust if necessary
    
    stats = {
        "Area (km²)": round(total_area, 2),
        "Population Density (people/km²)": round(density, 1000),
        "World Population Percentage": f"{world_population_percentage:.2f}" # %
    }
    st.write(stats)

    # Interactive map visualization
    st.subheader("Interactive Map")

    # Check if 'Capital' column exists
    if 'Capital' in country_geometry.columns:
        capital_city = country_geometry['Capital'].iloc[0]
        capital_coords = country_geometry['geometry'].iloc[0].centroid.coords[0]
    else:
        capital_city = "Capital info not available"
        capital_coords = country_geometry['geometry'].iloc[0].centroid.coords[0]  # Use centroid if capital info is missing

    folium_map = fl.Map(location=capital_coords, zoom_start=5)
    folium_marker = fl.Marker(location=capital_coords, popup=f"Capital: {capital_city}").add_to(folium_map)
    folium_geo = fl.GeoJson(data=country_geometry).add_to(folium_map)
    st_folium(folium_map, width=700, height=500)

    # Demographic data visualization
    st.subheader("Demographics")
    
    # Select columns that contain 'Population' and include valid years (e.g., '2022 Population', '2020 Population')
    years = [col.split(' ')[0] for col in population_data.columns if 'Population' in col and col.split(' ')[0].isdigit()]
    
    # Set the default years to the first available years from the `years` list
    default_years = years[:2]  # Choose the first two years as the default (or you can customize this)
    
    selected_years = st.multiselect("Select years:", years, default=default_years)
    
    # Reshape the data
    filtered_data = country_data[['Country/Territory'] + [f'{year} Population' for year in selected_years]]
    filtered_data = filtered_data.melt(id_vars=['Country/Territory'], value_vars=[f'{year} Population' for year in selected_years], 
                                       var_name='Year', value_name='Population')
    
    # Create the plot
    fig = px.bar(filtered_data, x="Year", y="Population", title="Population over the years", labels={"Population": "Population"})
    st.plotly_chart(fig)
else:
    st.warning("Data not available for this country.")
