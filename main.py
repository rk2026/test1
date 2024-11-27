import streamlit as st
import pandas as pd

# Streamlit App Title
st.title("CSV File Uploader and Viewer")

# File Upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(uploaded_file)
    
    # Display the DataFrame
    st.write("Uploaded CSV File:")
    st.dataframe(df)
