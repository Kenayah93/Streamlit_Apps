import streamlit as st
import pandas as pd
import geopandas as gpd
import folium as fl
from streamlit_folium import st_folium
import plotly.express as px
import requests


# data loading
geo_data = gpd.read_file("https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world.geojson")

pop_data = pd.read_csv("https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/main/13_final_project_data/world_population.csv")


# Page stup 

st.set_page_config(
    layout="wide",
    page_title = "Visualise la population mondiale"
    )

# Application
st.title("Interactive Dashboard : World Population")

# Select country

world=gpd.read_file("https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world.geojson")
pop=pd.read_csv("https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/main/13_final_project_data/world_population.csv")

donnee=pop[pop['Country/Territory'].isin(world['name'])]['Country/Territory'].unique()
col1, col2 = st.columns([1, 1])
with col1:   
    sel_country = st.selectbox('# **Select a country**', sorted(donnee))
    annee=['2022 Population','2020 Population','2015 Population','2010 Population','2000 Population','1990 Population','1980 Population','1970 Population']
    p_pop = pop[pop['Country/Territory'] == sel_country][annee]
    annee_mul=st.multiselect(f"**Population of {sel_country}**",options=annee,default=annee)
    pop_mul=p_pop[annee_mul]
    st.markdown(f"##### **Population of {sel_country} depending on the year(s)**")
    st.bar_chart(pop_mul.T)

with col2:
    pays = world[world['name'] == sel_country]
    total_area=pop[pop['Country/Territory'] == sel_country]['Area (km²)'].values[0]
    density=pop[pop['Country/Territory'] == sel_country]['Density (per km²)'].values[0]
    growth_rate=pop[pop['Country/Territory'] == sel_country]['Growth Rate'].values[0]
    pop_per=pop[pop['Country/Territory'] == sel_country]['World Population Percentage'].values[0]
    st.markdown('#### Country statistics')
    st.text(f'The area of the country is {total_area} km²\nThe density is {density} per km²\nThe growth rate is {growth_rate}\nIts percentage compared to the world is {pop_per} %')
    m = fl.Map(location=[pays.geometry.centroid.y.values[0], pays.geometry.centroid.x.values[0]], zoom_start=5)
    fl.GeoJson(pays).add_to(m)
    st_folium(m, width=700, height=500)