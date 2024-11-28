import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# Chargement des données avec gestion des erreurs
@st.cache_data
def load_population_data():
    url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/main/13_final_project_data/world_population.csv"
    try:
        data = pd.read_csv(url)
        if 'Country/Territory' not in data.columns:
            raise ValueError("La colonne 'Country/Territory' est manquante.")
        return data
    except Exception as e:
        st.error(f"Erreur lors du chargement des données de population : {e}")
        return pd.DataFrame()

@st.cache_data
def load_geospatial_data():
    url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/main/13_final_project_data/world.geojson"
    try:
        data = gpd.read_file(url)
        if 'name' not in data.columns:
            raise ValueError("La colonne 'name' est manquante.")
        return data
    except Exception as e:
        st.error(f"Erreur lors du chargement des données géospatiales : {e}")
        return gpd.GeoDataFrame()

# Configuration de la page
st.set_page_config(page_title="Tableau de bord géospatial", layout="wide")

# Titre de l'application
st.title("Tableau de bord interactif : Population mondiale")

# Chargement des données
population_data = load_population_data()
geospatial_data = load_geospatial_data()

# Vérification de la disponibilité des données
if population_data.empty or geospatial_data.empty:
    st.error("Les données nécessaires n'ont pas pu être chargées. Vérifiez les sources.")
else:
    # Sélection du pays
    countries = population_data['Country/Territory'].unique()
    selected_country = st.selectbox("Sélectionnez un pays :", sorted(countries))

    # Filtrage des données pour le pays sélectionné
    country_data = population_data[population_data['Country/Territory'] == selected_country]
    country_geometry = geospatial_data[geospatial_data['name'] == selected_country]

    # Vérification des données spécifiques au pays
    if country_data.empty or country_geometry.empty:
        st.warning(f"Les données pour le pays '{selected_country}' sont indisponibles.")
    else:
        # Calcul des statistiques clés
        st.subheader(f"Statistiques pour {selected_country}")
        try:
            # Superficie (conversion m² en km²)
            total_area = country_geometry['geometry'].iloc[0].to_crs(epsg=3395).area / 10**6

            # Population 2022
            population_2022 = country_data.loc[:, '2022 Population'].values[0]
            
            # Densité de population
            density = population_2022 / total_area
            
            # Pourcentage de la population mondiale
            total_population_2022 = population_data['2022 Population'].sum()
            world_population_percentage = (population_2022 / total_population_2022) * 100

            # Affichage des statistiques
            stats = {
                "Superficie (km²)": round(total_area, 2),
                "Population (2022)": f"{int(population_2022):,}",
                "Densité de population (hab/km²)": round(density, 2),
                "Pourcentage de la population mondiale": f"{world_population_percentage:.2f}%"
            }
            st.write(stats)
        except Exception as e:
            st.error(f"Erreur dans le calcul des statistiques : {e}")

        # Visualisation de la carte interactive
        st.subheader("Carte interactive")
        try:
            # Centroid pour les coordonnées
            centroid = country_geometry['geometry'].iloc[0].centroid
            folium_map = folium.Map(location=[centroid.y, centroid.x], zoom_start=5)
            folium.GeoJson(data=country_geometry).add_to(folium_map)
            st_folium(folium_map, width=700, height=500)
        except Exception as e:
            st.warning(f"Erreur lors de la génération de la carte : {e}")

        # Visualisation des données démographiques
        st.subheader("Démographie")
        try:
            # Colonnes des années
            year_columns = [col for col in population_data.columns if "Population" in col]
            selected_years = st.multiselect("Sélectionnez les années :", year_columns, default=["2020 Population", "2022 Population"])
            
            if selected_years:
                demographic_data = country_data.melt(
                    id_vars=["Country/Territory"],
                    value_vars=selected_years,
                    var_name="Année",
                    value_name="Population"
                )
                demographic_data['Année'] = demographic_data['Année'].str.extract(r"(\d+)")
                
                # Visualisation graphique
                fig = px.bar(
                    demographic_data,
                    x="Année",
                    y="Population",
                    title=f"Évolution de la population de {selected_country}",
                    labels={"Population": "Population"},
                    text="Population"
                )
                st.plotly_chart(fig)
            else:
                st.warning("Aucune année sélectionnée pour l'affichage.")
        except Exception as e:
            st.warning(f"Erreur dans la visualisation des données démographiques : {e}")
