import streamlit as st
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

# Charger le fichier OPCVM nettoyé
file_path = "cleaned_opcvm.xlsx"
df_cleaned = pd.read_excel(file_path)

# Assurer la catégorisation en FCP ou SICAV
df_cleaned["Type"] = df_cleaned["DENOMINATION"].apply(lambda x: "SICAV" if "SICAV" in str(x).upper() else "FCP")

# Sélection des Top 3 FCP et SICAV pour 2024 basés sur "Taux_1" (Rendement 2024)
top_3_fcp_2024 = df_cleaned[df_cleaned["Type"] == "FCP"].nlargest(3, "Taux_1")[["DENOMINATION", "Taux_1"]]
top_3_sicav_2024 = df_cleaned[df_cleaned["Type"] == "SICAV"].nlargest(3, "Taux_1")[["DENOMINATION", "Taux_1"]]

# Sélection des Top 3 FCP et SICAV pour 2025 basés sur "Taux_3" (Estimation)
top_3_fcp_2025 = df_cleaned[df_cleaned["Type"] == "FCP"].nlargest(3, "Taux_3")[["DENOMINATION", "Taux_3"]]
top_3_sicav_2025 = df_cleaned[df_cleaned["Type"] == "SICAV"].nlargest(3, "Taux_3")[["DENOMINATION", "Taux_3"]]

# Appliquer des styles aux tableaux
def surligner_top(df):
    return df.style.applymap(lambda x: "background-color: #FFC300; font-weight: bold;" if isinstance(x, (int, float)) else "")

# Configuration Streamlit
st.set_page_config(page_title="Recommandations d'investissement OPCVM", layout="wide")

st.title("📊 Système de Recommandation d'Investissement OPCVM obligataire")
st.markdown("### 🔎 Découvrez les meilleures opportunités d'investissement pour 2024 & 2025 !")

# Affichage des meilleures opportunités pour 2024
st.markdown("## 🏆 Meilleurs investissements pour 2024")

col1, col2 = st.columns(2)
with col1:
    st.subheader("🏅 Top 3 **FCP**")
    st.dataframe(surligner_top(top_3_fcp_2024))

with col2:
    st.subheader("🏅 Top 3 **SICAV**")
    st.dataframe(surligner_top(top_3_sicav_2024))

date_du_jour = datetime.today().strftime("%d %B %Y")

# Explication pour 2025
st.markdown(f"""
## 🚀 Meilleurs investissements pour 2025 (Estimation)
📅 **Nous sommes le {date_du_jour}** : L'année 2025 n'est pas encore terminée, ces rendements sont donc **des estimations basées sur les tendances actuelles**.
""")

col3, col4 = st.columns(2)
with col3:
    st.subheader("🔮 Top 3 **FCP**")
    st.dataframe(surligner_top(top_3_fcp_2025))

with col4:
    st.subheader("🔮 Top 3 **SICAV**")
    st.dataframe(surligner_top(top_3_sicav_2025))
