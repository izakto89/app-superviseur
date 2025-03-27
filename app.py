import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("🧑‍💼 Superviseur - Pilotage Atelier")

# ==== Upload fichier OFs ====
st.header("📥 Charger le fichier des OFs")
uploaded_file = st.file_uploader("Importer le fichier Excel des OFs", type=["xlsx"])

# ==== Calendrier d'ouverture ====
st.header("🗓️ Définir les heures d'ouverture (par jour)")
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
calendrier = {}
cols = st.columns(len(jours))
for i, jour in enumerate(jours):
    calendrier[jour] = cols[i].number_input(f"{jour}", min_value=0.0, max_value=24.0, value=8.0, step=0.5, format="%.1f")

# ==== Planification prévisionnelle ====
if uploaded_file:
    st.header("📅 Planning prévisionnel (avec respect du calendrier)")

    df_ofs = pd.read_excel(uploaded_file)
    df_gantt = df_ofs.copy()
    date_debut = datetime.today().replace(hour=8, minute=0, second=0, microsecond=0)
    heures_par_jour = [calendrier[j] for j in jours]
    planifie = []

    date_actuelle = date_debut
    quota_restant_du_jour = heures_par_jour[date_actuelle.weekday()] * 60  # en minutes

    for _, row in df_gantt.iterrows():
        temps_rest = row["Temps théorique (min)"]

        while temps_rest > 0:
            jour_index = date_actuelle.weekday()
            quota_jour = heures_par_jour[jour_index] * 60

            if quota_restant_du_jour <= 0 or quota_jour == 0:
                # Passer au jour ouvré suivant
                date_actuelle += timedelta(days=1)
                jour_index = date_actuelle.weekday()
                quota_restant_du_jour = heures_par_jour[jour_index] * 60
                date_actuelle = date_actuelle.replace(hour=8, minute=0)
                continue

            # Segment planifié
            temps_segment = min(temps_rest, quota_restant_du_jour)
            heure_debut = date_actuelle
            heure_fin = heure_debut + timedelta(minutes=temps_segment)

            planifie.append({
                "N°OF": row["N°OF"],
                "Début": heure_debut,
                "Fin": heure_fin,
                "Produit": row["Produit"]
            })

            date_actuelle = heure_fin
            quota_restant_du_jour -= temps_segment
            temps_rest -= temps_segment

    df_plan = pd.DataFrame(planifie)

    st.markdown("### 🟦 Gantt prévisionnel (ajusté au quota journalier)")
    fig = px.timeline(df_plan, x_start="Début", x_end="Fin", y="N°OF", color="Produit", title="Planning Prévisionnel")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(legend_title_text="Produit", height=500)
    st.plotly_chart(fig, use_container_width=True)

# ==== Planning réel depuis fichier CSV ====
st.header("📡 Planning réel des opérateurs (déclarations terrain)")

try:
    df_decl = pd.read_csv("declarations.csv", parse_dates=["debut", "fin"])
    st.dataframe(df_decl)

    fig2 = px.timeline(df_decl, x_start="debut", x_end="fin", y="n_of", color="operateur", title="Planning Réel")
    fig2.update_yaxes(autorange="reversed")
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)

except FileNotFoundError:
    st.warning("Aucun fichier de déclaration réelle trouvé (`declarations.csv`).")
