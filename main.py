import streamlit as st 
import pandas as pd
import geopandas as gpd
import numpy as np
import pydeck as pdk
import matplotlib
from shapely.geometry import Point, Polygon

# Streamlit App Title
st.title("Standing tree volume calculation")

# User Input for EPSG
EPSG = st.text_input("Enter 32644 (UTM44) or 32645 (UTM45)", value="32645")

# User Input for Grid Spacing
grid_spacing = st.number_input("Mother tree to mother tree distance in meter", value=20)

# File Upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# Create the data dictionary
data = {
    'SN': range(1, 26),
    'scientific_name': ['Abies spp', 'Acacia catechu', 'Adina cardifolia', 'Albizia spp', 'Alnus nepalensis',
                       'Anogeissus latifolia', 'Bombax ceiba', 'Cedrela toona', 'Dalbergia sissoo',
                       'Eugenia Jambolana', 'Hymenodictyon excelsum', 'Lagerstroemia parviflora',
                       'Michelia champaca', 'Pinus roxburghii', 'Pinus wallichiana', 'Quercus spp',
                       'Schima wallichii', 'Shorea robusta', 'Terminalia alata', 'Trewia nudiflora',
                       'Tsuga spp', 'Terai spp', 'Hill spp', 'Coniferious', 'Broadleaved'],
    'a': [-2.4453, -2.3256, -2.5626, -2.4284, -2.7761, -2.272, -2.3856, -2.1832, -2.1959, -2.5693,
          -2.585, -2.3411, -2.0152, -2.977, -2.8195, -2.36, -2.7385, -2.4554, -2.4616, -2.4585,
          -2.5293, -2.3993, -2.3204, np.nan, np.nan],
    'b': [1.722, 1.6476, 1.8598, 1.7609, 1.9006, 1.7499, 1.7414, 1.8679, 1.6567, 1.8816,
          1.9437, 1.7246, 1.8555, 1.9235, 1.725, 1.968, 1.8155, 1.9026, 1.8497, 1.8043,
          1.7815, 1.7836, 1.8507, np.nan, np.nan],
    'c': [1.0757, 1.0552, 0.8783, 0.9662, 0.9428, 0.9174, 1.0063, 0.7569, 0.9899, 0.8498,
          0.7902, 0.9702, 0.763, 1.0019, 1.1623, 0.7496, 1.0072, 0.8352, 0.88, 0.922,
          1.0369, 0.9546, 0.8223, np.nan, np.nan],
    'a1': [5.4433, 5.4401, 5.4681, 4.4031, 6.019, 4.9502, 4.5554, 4.9705, 4.358, 5.1749,
           5.5572, 5.3349, 3.3499, 6.2696, 5.7216, 4.8511, 7.4617, 5.2026, 4.5968, 5.3475,
           5.2774, 4.8991, 5.5323, np.nan, np.nan],
    'b1': [-2.6902, -2.491, -2.491, -2.2094, -2.7271, -2.3353, -2.3009, -2.3436, -2.1559, -2.3636,
           -2.496, -2.4428, -2.0161, -2.8252, -2.6788, -2.4494, -3.0676, -2.4788, -2.2305, -2.4774,
           -2.6483, -2.3406, -2.4815, np.nan, np.nan],
    's': [0.436, 0.443, 0.443, 0.443, 0.803, 0.443, 0.443, 0.443, 0.684, 0.443,
          0.443, 0.443, 0.443, 0.189, 0.683, 0.747, 0.52, 0.055, 0.443, 0.443,
          0.443, 0.443, 0.443, 0.436, 0.443],
    'm': [0.372, 0.511, 0.511, 0.511, 1.226, 0.511, 0.511, 0.511, 0.684, 0.511,
          0.511, 0.511, 0.511, 0.256, 0.488, 0.96, 0.186, 0.341, 0.511, 0.511,
          0.511, 0.511, 0.511, 0.372, 0.511],
    'bg': [0.355, 0.71, 0.71, 0.71, 1.51, 0.71, 0.71, 0.71, 0.684, 0.71,
           0.71, 0.71, 0.71, 0.3, 0.41, 1.06, 0.168, 0.357, 0.71, 0.71,
           0.71, 0.71, 0.71, 0.355, 0.71],
    'Local_Name': ['Thingre Salla', 'Khayar', 'Karma', 'Siris', 'Uttis', 'Banjhi', 'Simal', 'Tooni',
                   'Sissoo', 'Jamun', 'Bhudkul', 'Botdhayero', 'Chanp', 'Khote Salla', 'Gobre Salla',
                   'Kharsu', 'Chilaune', 'Sal', 'Saj', 'Gamhari', 'Dhupi Salla', 'Terai Spp',
                   'Hill spp', '', '']
}
sppVal = pd.DataFrame(data)

# Initialize layer and view_state before the conditional block
layer = None  # Ensure layer is defined
view_state = pdk.ViewState(latitude=0, longitude=0, zoom=2, pitch=0)  # Default view state

# Function to calculate additional fields
def add_calculated_columns(df):  
    df['stem_volume'] = np.exp(df['a'] + df['b'] * np.log(df['dia_cm']) + df['c'] * np.log(df['height_m'])) / 1000

    # Branch ratio calculation based on dia_cm
    conditions = [
        df['dia_cm'] < 10,
        (df['dia_cm'] >= 10) & (df['dia_cm'] < 40),
        (df['dia_cm'] >= 40) & (df['dia_cm'] < 70),
        df['dia_cm'] >= 70
    ]

    choices = [
        df['s'],  # For dia_cm < 10
        ((df["dia_cm"] - 10) * df["bg"] + (40 - df["dia_cm"]) * df["m"]) / 30,
        ((df["dia_cm"] - 40) * df["bg"] + (70 - df["dia_cm"]) * df["m"]) / 30,
        df['bg']   # For dia_cm >= 70
    ]

    df['branch_ratio'] = np.select(conditions, choices)
    df['branch_volume'] = df['stem_volume'] * df['branch_ratio']
    df['tree_volume'] = df['stem_volume'] + df['branch_volume']
    df['cm10diaratio'] = np.exp(df['a1'] + df['b1'] * np.log(df['dia_cm']))
    df['cm10topvolume'] = df['stem_volume'] * df['cm10diaratio']
    df['gross_volume'] = df['stem_volume'] - df['cm10topvolume']
    df['net_volume'] = df.apply(lambda row: row['gross_volume'] * 0.9 if row['class'] == 'A' else row['gross_volume'] * 0.8, axis=1)
    df['net_volum_cft'] = df['net_volume'] * 35.3147
    df['firewood_m3'] = df['tree_volume'] - df['net_volume']
    df['firewood_chatta'] = df['firewood_m3'] * 0.105944

    return df

# Function to create a square grid
def create_square_grid(input_gdf, spacing=20):
    # Ensure the GeoDataFrame has the correct CRS
    if input_gdf.crs.to_epsg() != 32645:
        input_gdf = input_gdf.to_crs(epsg=32645)
    # Get the bounding box of the GeoDataFrame
    minx, miny, maxx, maxy = input_gdf.total_bounds
    # Create arrays of coordinates based on the spacing
    x_coords = np.arange(minx, maxx, spacing)
    y_coords = np.arange(miny, maxy, spacing)
    # Create the square polygons
    polygons = []
    for x in x_coords:
        for y in y_coords:
            polygon = Polygon([(x, y), (x + spacing, y), (x + spacing, y + spacing), (x, y + spacing)])
            polygons.append(polygon)
    # Create a GeoDataFrame with the square polygons
    grid_gdf = gpd.GeoDataFrame(geometry=polygons, crs=input_gdf.crs)
    return grid_gdf

if uploaded_file is not None:
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(uploaded_file)
    # Display the DataFrame
    #st.write("Uploaded CSV File:")
    #st.dataframe(df)
    
    # Merge dataframes
    joined_df = df.merge(sppVal, left_on='species', right_on='scientific_name')
    joined_df['geometry'] = joined_df.apply(lambda row: Point(row['LONGITUDE'], row['LATITUDE']), axis=1)
    joined_gdf = gpd.GeoDataFrame(joined_df, geometry='geometry')
    joined_gdf = joined_gdf.set_crs(epsg=4326)
    joined_gdf = add_calculated_columns(df=joined_gdf)
    result_gdf = joined_gdf.to_crs(epsg=EPSG)
    
    # Create grid
    grid_gdf = create_square_grid(input_gdf=result_gdf, spacing=grid_spacing)
    grid_gdf['gid'] = grid_gdf.index + 1
    # Spatial join to assign 'gid' to points based on intersection
    result_gdf = gpd.sjoin(result_gdf, grid_gdf, how='inner', predicate='intersects')
    result_gdf = result_gdf.sort_values(by='gid', ascending=True)
    # Create a boolean mask to identify the first unique 'gid' value
    first_unique_mask = result_gdf['gid'].duplicated(keep='first')
    # Create the 'remark' column and populate it based on the mask
    result_gdf['remark'] = 'Felling Tree'
    result_gdf.loc[~first_unique_mask, 'remark'] = 'Mother Tree'
    result_gdf['color'] = result_gdf['remark'].apply(lambda x: 'red' if x == 'Mother Tree' else 'green')
    # Assuming your color column contains color names like 'red', 'green', etc.
    result_gdf['color'] = result_gdf['color'].apply(lambda x: matplotlib.colors.to_rgba(x))
    # If colors are stored as strings, e.g., '1,0,0,1'
    #result_gdf['color'] = result_gdf['color'].apply(lambda x: list(map(float, x.split(','))))
    # If color is already in tuple format (e.g., (1, 0, 0, 1)), no need to split.
    result_gdf['color'] = result_gdf['color'].apply(lambda x: list(x))
    result_gdf['color'] = result_gdf['color'].apply(lambda x: [int(val * 255) for val in x])


    # Additional calculations and Pydeck layer creation
    joined_gdf["LONGITUDE"] = joined_gdf.geometry.centroid.x
    joined_gdf["LATITUDE"] = joined_gdf.geometry.centroid.y

    # Ensure joined_gdf and result_gdf are in EPSG:4326
    joined_gdf = joined_gdf.to_crs(epsg=4326)
    result_gdf = result_gdf.to_crs(epsg=4326)
    
    # Add longitude and latitude columns for centroids
    joined_gdf["LONGITUDE"] = joined_gdf.geometry.centroid.x
    joined_gdf["LATITUDE"] = joined_gdf.geometry.centroid.y
    
    # Define Pydeck layers
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        result_gdf,
        get_position=["LONGITUDE", "LATITUDE"],
        get_radius=2,
        get_color="color",
        pickable=True,
        auto_highlight=True,
        tooltip={
            "html": """
            <b>TID:</b> {TID}<br>
            <b>Species:</b> {species}<br>
            """,
        },
    )
    
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        grid_gdf,
        get_polygon="geometry",
        get_fill_color=[155, 50, 50, 140],
        get_line_color=[0, 100, 100, 200],
        pickable=True,
    )
    
    # View state for the map
    view_state = pdk.ViewState(
        latitude=result_gdf["LATITUDE"].mean(),
        longitude=result_gdf["LONGITUDE"].mean(),
        zoom=15,
        pitch=0,
    )
    
    # Combine layers into a Pydeck Deck
    deck = pdk.Deck(
        layers=[point_layer, polygon_layer],
        initial_view_state=view_state,
    )
    
    # Display the map
    st.write("View the Mother Tree and Felling Tree Location")
    st.pydeck_chart(deck)
    
    # Dynamic Scale Bar Using HTML/CSS and JavaScript
    st.markdown("""
    <div id="map-container" style="position: relative; width: 50%; height: 50px;">
        <div id="scale-bar" style="
            position: relative; 
            bottom: 60px; 
            left: 60px; 
            background: rgba(0, 0, 255, 0.5); 
            padding: 15px; 
            border: 2px solid black; 
            font-size: 14px; 
            z-index: 1000;
        ">
            Scale: <span id="scale-value">500m</span>
        </div>
    </div>
    
    <script>
        const scaleBar = document.getElementById("scale-bar");
        const scaleValue = document.getElementById("scale-value");
    
        function updateScaleBar(zoomLevel) {
            // Adjust scale dynamically based on zoom
            const scales = {15: "100m", 14: "200m", 13: "500m", 12: "1km", 11: "2km"};
            scaleValue.textContent = scales[zoomLevel] || "Unknown scale";
        }
    
        const map = document.querySelector("iframe");  // Pydeck iframe
        if (map) {
            map.contentWindow.addEventListener("wheel", (event) => {
                const zoomLevel = Math.round(event.deltaY);
                updateScaleBar(zoomLevel);
            });
        }
    </script>
    """, unsafe_allow_html=True)
    # Optionally display dataframes
    st.write("Download Detailed Analysis table. Click the download button just right top of the table:")
    st.dataframe(result_gdf)
    
    

