import streamlit as st
import polars as pl
import os

st.set_page_config(page_title="Dashboard de Santé", layout="wide")

current_dir: str = os.getcwd()
data: str = os.path.join(current_dir, "data")
data_path: str = os.path.join(data, "BPE23.parquet")

df: pl.LazyFrame = pl.scan_parquet(data_path)

df_filtered = df.filter(
    (pl.col("DOM") == "D"), 
    (pl.col("TYPEQU").str.contains("D")),
    (pl.col("LATITUDE").is_not_null() & pl.col("LONGITUDE").is_not_null()) &
    (pl.col("LATITUDE") > 41) & (pl.col("LATITUDE") < 52) &
    (pl.col("LONGITUDE") > -5) & (pl.col("LONGITUDE") < 9),
    (pl.col("SDOM").is_in(["D1", "D2", "D3"]))
).select([
    "DOM", "SDOM", "TYPEQU", "DENS3", "DENS7",
    "AAV2020", "QP", "QP2015", "LATITUDE", "LONGITUDE",
    "CODPOS", "LIBCOM"
]).collect()


# Afficher le titre du tableau de bord
st.title("Tableau de Bord de la Revitalisation des Petites Villes - Santé")

# Ajouter des filtres interactifs
st.sidebar.header("Filtres")

# Filtre par type d'équipement
type_options = df_filtered["TYPEQU"].unique().to_list()
selected_type = st.sidebar.multiselect("Type d'Équipement", type_options, default=type_options)

# Filtre par densité
dens3_options = df_filtered["DENS3"].unique().to_list()
selected_dens3 = st.sidebar.multiselect("Densité (DENS3)", dens3_options, default=dens3_options)

# Appliquer les filtres sélectionnés
filtered_data: pl.DataFrame = df_filtered.filter(
    (pl.col("TYPEQU").is_in(selected_type)) &
    (pl.col("DENS3").is_in(selected_dens3))
)

# Ajouter une carte (si nécessaire)
st.write("### Carte des Équipements")
st.map(filtered_data[["LATITUDE", "LONGITUDE"]])
