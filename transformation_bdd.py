import polars as pl
import os
from typing import Generator

def get_parquet(directory: str) -> Generator[str, None, None]:
    return (file for file in os.listdir(directory) if file.endswith(".parquet") and "BDD" not in file)

def commune_title(lf_bdd: pl.LazyFrame) -> list[str]:
    cols = []
    for col in lf_bdd.collect_schema():
        if "com" in col.lower() or "lib" in col.lower():
            print(f"Colonne potentielle : {col}")
            cols.append(col)
    if not cols:
        print("Pas de colonne de type commune trouvée.")
        print(f"Nom des colonnes de {lf_bdd}: {lf_bdd.collect_schema()}")
    return cols

def reduce_bdd(lf_pvd: pl.LazyFrame, lf_bdd: pl.LazyFrame, col_com: str, lf_bdd_name: str) -> None:
    df_reduit = (
        lf_bdd.join(lf_pvd, left_on=col_com, right_on="lib_com", how="inner")
        .collect()
    )
    name_file = lf_bdd_name.replace(".parquet", "_BDD.parquet")
    df_reduit.write_parquet(name_file)
    
def transform_lf(directory: str, lf_pvd_path: str):
    lf_pvd: pl.LazyFrame = pl.scan_parquet(lf_pvd_path)

    for parquet in get_parquet(directory):
        lf_bdd: pl.LazyFrame = pl.scan_parquet(parquet)
        cols_com: list[str] = commune_title(lf_bdd)

        if cols_com:
            for col in cols_com:
                try:
                    reduce_bdd(lf_pvd=lf_pvd, lf_bdd=lf_bdd, col_com=col, lf_bdd_name=parquet)
                    print(f"{col} est la bonne !!")
                    break 
                except Exception as e:
                    print(f"{col} n'est pas la bonne colonne : {e}")
        else:
            print(f"Aucune colonne commune trouvée dans {parquet}")
            
if __name__ == "__main__":
    directory = os.getcwd()
    pvd_path = "programme-petites-villes-de-demain-liste-des-villes-beneficiaires.parquet"
    transform_lf(directory, pvd_path)

