import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("🧑‍💼 Superviseur – Pilotage Atelier")

# ==== 1. Upload fichier OF ====
st.header("📥 Charger le fichier des OFs")
uploaded_file = st.file_uploader("Importer le fichier Excel des OFs", type=["xlsx"])

# ==== 2. Calendrier d'ouverture ====
st.header("🗓️ Définir les heures d'ouverture du poste par jour")
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
calendrier = {}
cols = st.columns(len(jours))
for i, jour in enumerate(jours):
    calendrier[jour] = cols[i].number_input(
        f"{jour}", min_value=0.0, max_value=24.0, value=8.0 if jour in jours[:5] else 0.0, step=0.5, format="%.1f"
    )

# ==== 3. Planification prévisionnelle ====
if uploaded_file:
    st.header("📅 Planning prévisionnel (avec respect du calendrier)")

    df_ofs = pd.read_excel(uploaded_file)
    df_plan = []
    date_depart = datetime.today().replace(hour=8, minute=0, second=0, microsecond=0)
    heure_courante = date_depart
    jour_index = heure_courante.weekday()
    quota_jour = calendrier[jours[jour_index]] * 60  # en minutes
    quota_restant = quota_jour

    for _, row in df_ofs.iterrows():
        temps_restant = row["Temps théorique (min)"]

        while temps_restant > 0:
            jour_index = heure_courante.weekday()
            quota_jour = calendrier[jours[jour_index]] * 60

            # Passer au jour ouvré suivant si quota épuisé ou jour fermé
            if quota_jour == 0 or quota_restant <= 0:
                heure_courante += timedelta(days=1)
                heure_courante = heure_courante.replace(hour=8, minute=0)
                jour_index = heure_courante.weekday()
                quota_jour = calendrier[jours[jour_index]] * 60
                quota_restant = quota_jour
                continue

            # Planification du segment
            segment = min(temps_restant, quota_restant)
            debut = heure_courante
            fin = debut + timedelta(minutes=segment)

            df_plan.append({
                "N°OF": row["N°OF"],
                "Début": debut,
                "Fin": fin,
                "Produit": row["Produit"]
            })

            heure_courante = fin
            quota_restant -= segment
            temps_restant -= segment

    # Affichage Gantt
    df_plan = pd.DataFrame(df_plan)
    st.markdown("### 🟦 Gantt prévisionnel (avec quota journalier)")
    fig = px.timeline(df_plan, x_start="Début", x_end="Fin", y="N°OF", color="Produit", title="Planning Prévisionnel")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(legend_title_text="Produit", height=500, xaxis_title="Date & Heure")
    st.plotly_chart(fig, use_container_width=True)

# ==== 4. Planning réel (déclarations opérateurs) ====
st.header("📡 Planning réel (déclarations des opérateurs)")

try:
    df_decl = pd.read_csv("declarations.csv", parse_dates=["debut", "fin"])
    st.dataframe(df_decl)

    fig2 = px.timeline(df_decl, x_start="debut", x_end="fin", y="n_of", color="operateur", title="Planning Réel")
    fig2.update_yaxes(autorange="reversed")
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)

except FileNotFoundError:
    st.info("ℹ️ Aucun fichier `declarations.csv` trouvé pour le moment.")
