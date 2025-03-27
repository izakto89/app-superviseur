import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📊 Superviseur - Pilotage Atelier")

# ---- Upload OFs
st.header("📥 Chargement des OFs")
uploaded_file = st.file_uploader("Importer le fichier OFs (Excel)", type=["xlsx"])
if uploaded_file:
    df_ofs = pd.read_excel(uploaded_file)
    st.success("✅ OFs chargés avec succès")
    st.dataframe(df_ofs)

# ---- Calendrier d'ouverture poste
st.header("🗓️ Calendrier d'ouverture poste (ex. MONTFB)")
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
calendrier = {}
cols = st.columns(len(jours))
for i, jour in enumerate(jours):
    calendrier[jour] = cols[i].number_input(f"{jour}", min_value=0.0, max_value=24.0, value=8.0, step=0.5, format="%.1f")

# ---- Simuler un planning prévisionnel simple
if uploaded_file:
    st.header("📅 Planning prévisionnel (simulation)")

    df_gantt = df_ofs.copy()
    date_debut = datetime.today().replace(hour=8, minute=0, second=0, microsecond=0)

    heures_par_jour = [calendrier[jour] for jour in jours]
    date_actuelle = date_debut
    planifie = []

    for _, row in df_gantt.iterrows():
        temps_rest = row["Temps théorique (min)"]
        while temps_rest > 0:
            jour_index = date_actuelle.weekday()
            dispo = heures_par_jour[jour_index] * 60
            if dispo == 0:
                date_actuelle += timedelta(days=1)
                continue

            temps_of = min(temps_rest, dispo)
            planifie.append({
                "N°OF": row["N°OF"],
                "Début": date_actuelle,
                "Fin": date_actuelle + timedelta(minutes=temps_of),
                "Produit": row["Produit"]
            })
            date_actuelle += timedelta(minutes=temps_of)
            temps_rest -= temps_of

    df_plan = pd.DataFrame(planifie)

    fig = px.timeline(df_plan, x_start="Début", x_end="Fin", y="N°OF", color="Produit")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

# ---- Affichage planning réel (déclarations opérateurs simulées)
st.header("📡 Planning réel (exemple)")
try:
    df_decl = pd.read_csv("declarations.csv", parse_dates=["debut", "fin"])
    st.dataframe(df_decl)
    fig2 = px.timeline(df_decl, x_start="debut", x_end="fin", y="n_of", color="operateur")
    fig2.update_yaxes(autorange="reversed")
    st.plotly_chart(fig2, use_container_width=True)
except FileNotFoundError:
    st.warning("Aucune déclaration réelle trouvée (manque declarations.csv)")
