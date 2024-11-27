import streamlit as st
import pandas as pd

# Streamlit App Title
st.title("CSV File Uploader and Viewer")

# User Input for EPSG
EPSG = st.text_input("Enter the EPSG Code (e.g., 4326):", value="")

# User Input for Grid Spacing
grid_spacing = st.number_input("Enter Grid Spacing (numeric value):", value=0.0)

# File Upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(uploaded_file)
    
    # Display the DataFrame
    st.write("Uploaded CSV File:")
    st.dataframe(df)

# Display Entered Inputs
if EPSG:
    st.write(f"EPSG Code Entered: {EPSG}")

if grid_spacing:
    st.write(f"Grid Spacing Entered: {grid_spacing}")

