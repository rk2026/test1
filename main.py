import streamlit as st
import pandas as pd
import io

# Title
st.title("CSV File Upload and User Input")

# File Upload
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded CSV file:")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error reading the file: {e}")

# User Input for grid spacing
grid_spacing = st.number_input("Enter grid spacing:", min_value=0.0, step=0.1)
st.write(f"Grid spacing: {grid_spacing}")

# User input for text
user_text = st.text_input("Enter text (e.g., EPSG:4326):")
st.write(f"User text: {user_text}")
