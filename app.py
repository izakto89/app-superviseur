import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

st.set_page_config(layout="wide")

st.title("🛠️ Pilotage Atelier - Suivi OFs")

# Stockage des données locales (temporaire - pas base partagée encore)
if "of_en_cours" not in st.session_state:
    st.session_state.of_en_cours = None
if "declarations" not in st.session_state:
    st.session_state.declarations = []

# Onglets : Opérateur / Superviseur
onglet = st.sidebar.radio("👥 Choisir le mode :", ["Opérateur", "Superviseur"])

# ------------------------------
# 🟥 ONGLET OPÉRATEUR
# ------------------------------
if onglet == "Opérateur":
    st.subheader("👷 Interface Opérateur")

    nom_operateur = st.text_input("👤 Ton prénom :", "")
    
    if nom_operateur:
        st.markdown(f"📅 Date : **{datetime.today().strftime('%A %d %B %Y')}**")
        uploaded_file = st.file_uploader("📤 Charger le fichier des OFs", type="xlsx")

        if uploaded_file:
            df_of = pd.read_excel(uploaded_file)
            df_of = df_of.sort_values("Priorité", ascending=False)
            st.dataframe(df_of, use_container_width=True)

            selected_of = st.selectbox("📌 Sélectionne un OF à lancer :", df_of["N°OF"].unique())

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Début OF"):
                    st.session_state.of_en_cours = {
                        "n_of": selected_of,
                        "debut": datetime.now(),
                        "operateur": nom_operateur,
                        "arrets": []
                    }
            with col2:
                if st.button("🏁 Fin OF") and st.session_state.of_en_cours:
                    fin = datetime.now()
                    of_data = st.session_state.of_en_cours
                    duree = round((fin - of_data["debut"]).total_seconds() / 60, 2)
                    of_data["fin"] = fin
                    of_data["duree_totale_min"] = duree
                    st.session_state.declarations.append(of_data)
                    st.success(f"✅ OF {of_data['n_of']} terminé en {duree} minutes.")
                    st.session_state.of_en_cours = None

        if st.session_state.of_en_cours:
            of_data = st.session_state.of_en_cours
            st.markdown(f"### ▶️ OF en cours : `{of_data['n_of']}` lancé à `{of_data['debut'].strftime('%H:%M:%S')}`")
            st.markdown(f"👷 Opérateur : **{of_data['operateur']}**")

            st.markdown("### 🛑 Déclaration d’arrêts")
            col1, col2, col3, col4, col5 = st.columns(5)
            arrets = ["Pause", "Qualité", "Manque de charge", "Formation", "Absence personnel"]

            for i, nom in enumerate(arrets):
                if st.button(f"🚨 {nom}"):
                    horodatage = datetime.now().strftime('%H:%M:%S')
                    commentaire = st.text_input(f"📝 Commentaire pour l’arrêt : {nom}", key=f"cmt_{i}")
                    st.session_state.of_en_cours["arrets"].append({
                        "type": nom,
                        "heure": horodatage,
                        "commentaire": commentaire
                    })
                    st.warning(f"🛑 Arrêt '{nom}' déclaré à {horodatage}")

# ------------------------------
# 🟦 ONGLET SUPERVISEUR
# ------------------------------
if onglet == "Superviseur":
    st.subheader("🧑‍💼 Interface Superviseur")

    if st.session_state.declarations:
        df_resultats = pd.DataFrame(st.session_state.declarations)

        # Détailler les arrêts
        arret_data = []
        for of in st.session_state.declarations:
            for a in of["arrets"]:
                arret_data.append({
                    "OF": of["n_of"],
                    "Type d'arrêt": a["type"],
                    "Heure": a["heure"],
                    "Commentaire": a["commentaire"]
                })

        df_arrets = pd.DataFrame(arret_data)

        st.markdown("### 📊 Résumé des OFs déclarés")
        st.dataframe(df_resultats[["n_of", "operateur", "debut", "fin", "duree_totale_min"]], use_container_width=True)

        st.markdown("### 📉 Pareto des arrêts")
        if not df_arrets.empty:
            pareto = df_arrets["Type d'arrêt"].value_counts().reset_index()
            pareto.columns = ["Type d'arrêt", "Occurrences"]
            st.bar_chart(pareto.set_index("Type d'arrêt"))
            st.dataframe(df_arrets, use_container_width=True)
        else:
            st.info("Aucun arrêt déclaré pour le moment.")
    else:
        st.info("Aucune déclaration encore faite par les opérateurs.")
