import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import requests

# Chargement des données
@st.cache
def load_population_data():
    url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world_population.csv"
    return pd.read_csv(url)

@st.cache
def load_geospatial_data():
    url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world.geojson"
    return gpd.read_file(url)

population_data = load_population_data()
geospatial_data = load_geospatial_data()

# Configuration de la page
st.set_page_config(page_title="Tableau de bord géospatial")

# Titre de l'application
st.title("Tableau de bord interactif : Population mondiale")

# Sélection du pays
countries = population_data['Country/Territory'].unique()
selected_country = st.selectbox("Sélectionnez un pays :", sorted(countries))

# Filtrage des données pour le pays sélectionné
country_data = population_data[population_data['Country/Territory'] == selected_country]
country_geometry = geospatial_data[geospatial_data['ADMIN'] == selected_country]

target_years = ["1970 Population", "1980 Population", "1990 Population", "2000 Population","2010 Population", "2015 Population", "2020 Population", "2022 Population"]
selection = {
    "Year": target_years,
    "Population" : [country_data[year] for year in target_years] 
}


# Affichage des statistiques clés
if not country_data.empty and not country_geometry.empty:
    st.subheader(f"Statistiques pour {selected_country}")
    total_area = country_geometry['geometry'].area.iloc[0] / 10**6  # Convertir m² en km²
    population_2022 = country_data[country_data['Year'] == 2022]['Population'].values[0]
    density = population_2022 / total_area
    world_population_percentage = (population_2022 / population_data[population_data['Year'] == 2022]['Population'].sum()) * 100

    stats = {
        "Superficie (km²)": round(total_area, 2),
        "Densité de population (hab/km²)": round(density, 2),
        "Pourcentage de la population mondiale": f"{world_population_percentage:.2f}%"
    }
    st.write(stats)

    # Visualisation de la carte
    st.subheader("Carte interactive")
    capital_city = country_geometry['Capital'].iloc[0]
    capital_coords = country_geometry['geometry'].iloc[0].centroid.coords[0]

    folium_map = folium.Map(location=capital_coords, zoom_start=5)
    folium.Marker(location=capital_coords, popup=f"Capitale : {capital_city}").add_to(folium_map)
    folium.GeoJson(data=country_geometry).add_to(folium_map)
    st_folium(folium_map, width=700, height=500)

    # Visualisation des données démographiques
    st.subheader("Démographie")
    years = st.multiselect("Sélectionnez les années :", sorted(country_data['Year'].unique()), default=[2020, 2022])
    filtered_data = country_data[country_data['Year'].isin(years)]
    fig = px.bar(filtered_data, x="Year", y="Population", title="Population au fil des années", labels={"Population": "Population"})
    st.plotly_chart(fig)
else:
    st.warning("Données non disponibles pour ce pays.")
