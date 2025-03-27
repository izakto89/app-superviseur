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

# ---- Simuler un planning prévisionnel avec calendrier
if uploaded_file:
    st.header("📅 Planning prévisionnel (simulation avec calendrier)")

    df_gantt = df_ofs.copy()
    date_debut = datetime.today().replace(hour=8, minute=0, second=0, microsecond=0)
    heures_par_jour = [calendrier[jour] for jour in jours]

    date_actuelle = date_debut
    planifie = []

    for _, row in df_gantt.iterrows():
        temps_rest = row["Temps théorique (min)"]
        segments = []

        while temps_rest > 0:
            jour_index = date_actuelle.weekday()
            dispo = heures_par_jour[jour_index] * 60

            if dispo == 0:
                date_actuelle += timedelta(days=1)
                continue

            # On commence à 08h00 chaque jour ouvré
            heure_debut_jour = date_actuelle.replace(hour=8, minute=0)
            heure_fin_jour = heure_debut_jour + timedelta(minutes=dispo)

            # Calcul de la durée restante disponible sur ce jour
            duree = min(temps_rest, dispo)
            heure_fin_segment = heure_debut_jour + timedelta(minutes=duree)

            planifie.append({
                "N°OF": row["N°OF"],
                "Début": heure_debut_jour,
                "Fin": heure_fin_segment,
                "Produit": row["Produit"]
            })

            temps_rest -= duree
            date_actuelle += timedelta(days=1)

    df_plan = pd.DataFrame(planifie)

    st.markdown("### 🟦 Gantt prévisionnel (avec jours ouvrés)")
    fig = px.timeline(df_plan, x_start="Début", x_end="Fin", y="N°OF", color="Produit", title="Planning Prévisionnel")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(legend_title_text="Produit", height=500)
    st.plotly_chart(fig, use_container_width=True)
