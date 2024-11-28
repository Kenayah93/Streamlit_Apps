import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# Chargement des données avec mise en cache et gestion des erreurs
@st.cache_data
def load_population_data():
    url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world_population.csv"
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error("Erreur lors du chargement des données de population.")
        st.stop()

@st.cache_data
def load_geospatial_data():
    url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world.geojson"
    try:
        return gpd.read_file(url)
    except Exception as e:
        st.error("Erreur lors du chargement des données géospatiales.")
        st.stop()

# Configuration de la page
st.set_page_config(page_title="Tableau de bord géospatial", layout="wide")

# Titre de l'application
st.title("Tableau de bord interactif : Population mondiale")

# Chargement des données
population_data = load_population_data()
geospatial_data = load_geospatial_data()

# Vérification des données
if population_data.empty or geospatial_data.empty:
    st.error("Les données chargées sont vides. Veuillez vérifier les sources.")
    st.stop()

# Sélection du pays
countries = population_data['Country/Territory'].dropna().unique()
selected_country = st.selectbox("Sélectionnez un pays :", sorted(countries))

# Filtrage des données pour le pays sélectionné
country_data = population_data[population_data['Country/Territory'] == selected_country]
country_geometry = geospatial_data[geospatial_data['name'] == selected_country]

# Affichage des statistiques clés
if not country_data.empty and not country_geometry.empty:
    st.subheader(f"Statistiques pour {selected_country}")
    try:
        # Superficie en km²
        total_area = country_geometry['geometry'].to_crs(epsg=4326).area.iloc[0] / 10**6
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
        capital_city = country_geometry.get('Capital', 'Capitale inconnue').iloc[0]
        centroid = country_geometry['geometry'].iloc[0].centroid
        capital_coords = (centroid.y, centroid.x)

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
    except Exception as e:
        st.error("Erreur lors du traitement des données. Veuillez vérifier les formats et les contenus.")
else:
    st.warning("Données non disponibles pour ce pays.")
