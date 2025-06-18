
import streamlit as st
import pandas as pd
from normalize.normalizer import normalize_text

st.title("Enhanced Text Normalization")

user_input = st.text_input("Enter informal social media text:")
if user_input:
    st.write("**Normalized Output:**")
    st.success(normalize_text(user_input))
    
if st.button("Show Examples"):
    df = pd.read_csv("examples/example_inputs.csv")
    df["Normalized"] = df["Informal"].apply(normalize_text)
    st.dataframe(df)
