import streamlit as st
import pandas as pd

st.title("📋 Pilotage Atelier - Déclaration OF")

uploaded_file = st.file_uploader("📤 Charger le fichier des OFs (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("Liste des Ordres de Fabrication")
    st.dataframe(df)
