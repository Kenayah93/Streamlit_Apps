import streamlit as st
import pandas as pd
import geopandas as gpd
import folium as fl
from streamlit_folium import st_folium
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Tableau de bord géospatial", layout="wide")

# Chargement des données
@st.cache_data
def load_geospatial_data():
    url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/main/13_final_project_data/world.geojson"
    return gpd.read_file(url)

@st.cache_data
def load_population_data():
    url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/main/13_final_project_data/world_population.csv"
    return pd.read_csv(url)

geospatial_data = load_geospatial_data()
population_data = load_population_data()

# Titre de l'application
st.title("Tableau de bord interactif : Population mondiale")

# Sélection du pays
countries = population_data['Country/Territory'].unique()
selected_country = st.selectbox("Sélectionnez un pays :", sorted(countries))

# Filtrage des données pour le pays sélectionné
country_data = population_data[population_data['Country/Territory'] == selected_country]
country_geometry = geospatial_data[geospatial_data['name'] == selected_country]

# Vérification des données pour le pays sélectionné
if not country_data.empty and not country_geometry.empty:
    st.subheader(f"Statistiques pour {selected_country}")

    # Calcul des statistiques
    try:
        # Superficie (en km²)
        total_area = country_geometry['geometry'].iloc[0].to_crs(epsg=4326).area / 10**6

        # Population 2022
        population_2022 = country_data['2022 Population'].values[0]

        # Densité de population
        density = population_2022 / total_area

        # Pourcentage de la population mondiale
        total_world_population = population_data['2022 Population'].sum()
        world_population_percentage = (population_2022 / total_world_population) * 100

        # Affichage des statistiques
        stats = {
            "Superficie (km²)": round(total_area, 2),
            "Densité de population (hab/km²)": round(density, 2),
            "Pourcentage de la population mondiale": f"{world_population_percentage:.2f}%",
        }
        st.write(stats)
    except Exception as e:
        st.error(f"Erreur lors du calcul des statistiques : {e}")

    # Visualisation de la carte interactive
    st.subheader("Carte interactive")
    try:
        # Extraction des coordonnées de la capitale
        if 'Capital' in country_geometry.columns:
            capital_city = country_geometry['Capital'].iloc[0]
            capital_coords = list(country_geometry['geometry'].iloc[0].representative_point().coords)[0]
        else:
            capital_city = "Capitale inconnue"
            capital_coords = list(country_geometry['geometry'].iloc[0].centroid.coords)[0]

        # Création de la carte
        folium_map = fl.Map(location=capital_coords, zoom_start=5)
        fl.Marker(location=capital_coords, popup=f"Capitale : {capital_city}").add_to(folium_map)
        fl.GeoJson(data=country_geometry).add_to(folium_map)
        st_folium(folium_map, width=700, height=500)
    except Exception as e:
        st.error(f"Erreur lors de la génération de la carte : {e}")

    # Visualisation des données démographiques
    st.subheader("Démographie")
    try:
        # Colonnes contenant les populations
        year_columns = [col for col in population_data.columns if "Population" in col and col.split()[0].isdigit()]
        selected_years = st.multiselect("Sélectionnez les années :", year_columns, default=["2020 Population", "2022 Population"])

        if selected_years:
            filtered_data = country_data.melt(
                id_vars=['Country/Territory'],
                value_vars=selected_years,
                var_name="Année",
                value_name="Population"
            )
            filtered_data['Année'] = filtered_data['Année'].str.extract(r"(\d+)").astype(int)

            # Visualisation
            fig = px.bar(
                filtered_data,
                x="Année",
                y="Population",
                title=f"Évolution de la population de {selected_country}",
                labels={"Population": "Population"},
                text="Population"
            )
            st.plotly_chart(fig)
        else:
            st.warning("Aucune année sélectionnée.")
    except Exception as e:
        st.error(f"Erreur lors de la visualisation des données démographiques : {e}")
else:
    st.warning("Les données pour ce pays ne sont pas disponibles.")
