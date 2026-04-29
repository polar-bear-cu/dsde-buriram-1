import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="My Streamlit App", layout="wide")

# Sidebar for inputs
with st.sidebar:
    st.title("Settings")
    name = st.text_input("Enter your name")
    option = st.selectbox("Choose a category", ["A", "B", "C"])

# Main content
st.title("Welcome to My App!")
if name:
    st.success(f"Hello, {name}!")

st.write("Current selection:", option)

# Data Display
data = pd.DataFrame({"Column 1": [1, 2, 3], "Column 2": [10, 20, 30]})
st.dataframe(data)
