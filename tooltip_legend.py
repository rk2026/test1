import streamlit as st
import pydeck as pdk
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Sample Data
data = pd.DataFrame({
    "TID": [1, 2],
    "species": ["Oak", "Pine"],
    "dia_cm": [50, 30],
    "geometry": [Point(85.324, 27.717), Point(85.321, 27.719)],
    "color": [[255, 0, 0], [0, 255, 0]],
})
gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
gdf["LONGITUDE"] = gdf.geometry.x
gdf["LATITUDE"] = gdf.geometry.y

# Define Pydeck Layer with Tooltip
point_layer = pdk.Layer(
    "ScatterplotLayer",
    gdf,
    get_position=["LONGITUDE", "LATITUDE"],
    get_radius=50,
    get_color="color",
    pickable=True,  # Must be True for tooltips
    tooltip={
        "html": "<b>TID:</b> {TID}<br><b>Species:</b> {species}<br><b>Diameter:</b> {dia_cm} cm",
        "style": {"color": "white", "backgroundColor": "black", "padding": "10px"},
    },
)

# View State
view_state = pdk.ViewState(
    latitude=gdf["LATITUDE"].mean(),
    longitude=gdf["LONGITUDE"].mean(),
    zoom=13,
    pitch=0,
)

# Pydeck Map
deck = pdk.Deck(
    layers=[point_layer],
    initial_view_state=view_state,
)

# Display the Map
st.pydeck_chart(deck)

# Add Legend
st.markdown("""
<div style="position: absolute; top: 10px; right: 10px; background: white; padding: 10px; border: 1px solid black; z-index: 1000;">
   <b>Legend</b>
   <ul style="list-style: none; padding: 0;">
       <li style="color: rgb(255, 0, 0);">Red: Oak</li>
       <li style="color: rgb(0, 255, 0);">Green: Pine</li>
   </ul>
</div>
""", unsafe_allow_html=True)
