import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import random

# ----------------- Data Loading -----------------
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return {
        "continu": df[df["GROUPE DE COTATION"] == "11 - Continu"].copy(),
        "fixing": df[df["GROUPE DE COTATION"] == "12 - Fixing"].copy(),
        "tunindex20": df[df["TUNINDEX20"] == True].copy(),
        "shaaria": df[df["SHAARIA"] == True].copy(),
        "full": df
    }

@st.cache_data
def load_opcvm_data(file_path):
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        df["Type"] = df["DENOMINATION"].apply(lambda x: "SICAV" if "SICAV" in str(x).upper() else "FCP")
        return df
    return None

# ----------------- Utility Functions -----------------
def get_top_performers(df, type_filter, column):
    return df[df["Type"] == type_filter].nlargest(3, column)[["DENOMINATION", column]]

# ----------------- Main App -----------------
def main():
    st.set_page_config(page_title="Analyse des Marchés Financiers", layout="wide")

    # Load datasets
    market_data = load_data("class-s/CSV/end.csv")
    opcvm_data = load_opcvm_data("obligataire/cleaned_opcvm.xlsx")
    
    tunindex_mnemos = set(market_data["tunindex20"]["VALEUR"].tolist())
    sharia_mnemos = set(market_data["shaaria"]["VALEUR"].tolist())
    
    # Sidebar Options
    with st.sidebar:
        st.title("🔎 Navigation")
        choix = st.radio("Choisissez votre horizon d'investissement :", ["Court Terme", "Moyen/Long Terme"])
        st.markdown("---")
        st.subheader("📌 Options supplémentaires")
        show_sector_pie = st.checkbox("Afficher la répartition des secteurs")
        
        # Sector filter
        st.subheader("🔍 Filtrer par secteur")
        sector_options = ["Tous"] + list(market_data["full"]["SECTOR"].dropna().unique())
        selected_sector = st.selectbox("Choisissez un secteur", sector_options)
        
        # New Filtering Options
        show_sharia = st.checkbox("Afficher uniquement les valeurs Sharia")
        show_tunindex = st.checkbox("Afficher uniquement les valeurs Tunindex")
    
    st.title("📈 Analyse des Marchés Financiers")
    
    # Apply sector filter
    if selected_sector != "Tous":
        for key in market_data:
            market_data[key] = market_data[key][market_data[key]["SECTOR"] == selected_sector].reset_index(drop=True)
    
    # Apply Sharia and Tunindex filters
    if show_sharia and show_tunindex:
        for key in market_data:
            market_data[key] = market_data[key][market_data[key]["VALEUR"].isin(sharia_mnemos & tunindex_mnemos)].reset_index(drop=True)
    elif show_sharia:
        for key in market_data:
            market_data[key] = market_data[key][market_data[key]["VALEUR"].isin(sharia_mnemos)].reset_index(drop=True)
    elif show_tunindex:
        for key in market_data:
            market_data[key] = market_data[key][market_data[key]["VALEUR"].isin(tunindex_mnemos)].reset_index(drop=True)
    
    # Display Data Based on Selection
    if choix == "Court Terme":
        st.subheader("📊 Marché Court Terme")
        st.dataframe(market_data["tunindex20"][["VALEUR", "SECTOR"]].reset_index(drop=True))
    else:
        st.subheader("📊 Marché Moyen/Long Terme")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Liste des Valeurs Fixing")
            st.dataframe(market_data["fixing"][["VALEUR", "SECTOR"]].reset_index(drop=True))
        with col2:
            st.subheader("Liste des Valeurs Continu")
            st.dataframe(market_data["continu"][["VALEUR", "SECTOR"]].reset_index(drop=True))
    
    # Sector Distribution Pie Chart
    if show_sector_pie:
        st.subheader("📌 Répartition des Secteurs")
        sector_counts = market_data["full"]["SECTOR"].value_counts().reset_index()
        sector_counts.columns = ["SECTOR", "count"]  # Rename columns for plotly compatibility
        fig = px.pie(sector_counts, values="count", names="SECTOR", title="Distribution des Secteurs")
        st.plotly_chart(fig)
            


    
    # OPCVM Investments Data
    if opcvm_data is not None:
        st.subheader("🏆 Meilleurs investissements 2024")
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("🏅 Top 3 **FCP**")
            st.dataframe(get_top_performers(opcvm_data, "FCP", "Taux_1"))
        with col4:
            st.subheader("🏅 Top 3 **SICAV**")
            st.dataframe(get_top_performers(opcvm_data, "SICAV", "Taux_1"))
        
        date_du_jour = datetime.today().strftime("%d %B %Y")
        st.subheader(f"🚀 Meilleurs investissements pour 2025 (Estimation)\n📅 **Nous sommes le {date_du_jour}**")
        
        col5, col6 = st.columns(2)
        with col5:
            st.subheader("🔮 Top 3 **FCP**")
            st.dataframe(get_top_performers(opcvm_data, "FCP", "Taux_3"))
        with col6:
            st.subheader("🔮 Top 3 **SICAV**")
            st.dataframe(get_top_performers(opcvm_data, "SICAV", "Taux_3"))
    else:
        st.warning("Fichier OPCVM introuvable. Vérifiez le chemin.")

if __name__ == "__main__":
    main()
