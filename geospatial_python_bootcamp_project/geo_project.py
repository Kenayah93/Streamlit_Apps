import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# Chargement des données
@st.cache_data
def load_population_data():
    url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/main/13_final_project_data/world_population.csv"
    try:
        data = pd.read_csv(url)
        return data
    except Exception as e:
        st.error("Erreur lors du chargement des données de population.")
        return pd.DataFrame()

@st.cache_data
def load_geospatial_data():
    url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/main/13_final_project_data/world.geojson"
    try:
        data = gpd.read_file(url)
        return data
    except Exception as e:
        st.error("Erreur lors du chargement des données géospatiales.")
        return gpd.GeoDataFrame()

# Configuration de la page
st.set_page_config(page_title="Tableau de bord géospatial", layout="wide")

# Titre de l'application
st.title("Tableau de bord interactif : Population mondiale")

# Chargement des données
population_data = load_population_data()
geospatial_data = load_geospatial_data()

if population_data.empty or geospatial_data.empty:
    st.error("Impossible de charger les données. Vérifiez les sources et réessayez.")
else:
    # Sélection du pays
    countries = population_data['Country/Territory'].unique()
    selected_country = st.selectbox("Sélectionnez un pays :", sorted(countries))

    # Filtrage des données pour le pays sélectionné
    country_data = population_data[population_data['Country/Territory'] == selected_country]
    country_geometry = geospatial_data[geospatial_data['name'] == selected_country]

    # Affichage des statistiques clés
    if not country_data.empty and not country_geometry.empty:
        st.subheader(f"Statistiques pour {selected_country}")
        
        # Calculs des statistiques
        try:
            total_area = country_geometry['geometry'].area.iloc[0] / 10**6  # Convertir m² en km²
            population_2022 = country_data[country_data['Year'] == "2022 Population"]['Population'].values[0]
            density = population_2022 / total_area
            world_population_percentage = (
                (population_2022 / population_data[population_data['Year'] == "2022 Population"]['Population'].sum()) * 100
            )

            stats = {
                "Superficie (km²)": round(total_area, 2),
                "Densité de population (hab/km²)": round(density, 2),
                "Pourcentage de la population mondiale": f"{world_population_percentage:.2f}%"
            }
            st.write(stats)
        except Exception as e:
            st.warning("Impossible de calculer certaines statistiques. Vérifiez les données.")

        # Visualisation de la carte
        st.subheader("Carte interactive")
        try:
            capital_coords = country_geometry['geometry'].iloc[0].centroid.coords[0]

            folium_map = folium.Map(location=capital_coords, zoom_start=5)
            folium.GeoJson(data=country_geometry).add_to(folium_map)
            st_folium(folium_map, width=700, height=500)
        except Exception as e:
            st.warning("Impossible de générer la carte. Vérifiez les données géospatiales.")

        # Visualisation des données démographiques
        st.subheader("Démographie")
        years = st.multiselect(
            "Sélectionnez les années :", 
            [col for col in population_data.columns if "Population" in col],
            default=["2020 Population", "2022 Population"]
        )
        try:
            filtered_data = country_data[years]
            filtered_data = filtered_data.melt(
                var_name="Année", value_name="Population", ignore_index=False
            )
            filtered_data["Année"] = filtered_data["Année"].str.extract(r"(\d+)")
            fig = px.bar(
                filtered_data,
                x="Année",
                y="Population",
                title=f"Population de {selected_country} au fil des années",
                labels={"Population": "Population"}
            )
            st.plotly_chart(fig)
        except Exception as e:
            st.warning("Impossible d'afficher les données démographiques.")
    else:
        st.warning("Données non disponibles pour ce pays.")
