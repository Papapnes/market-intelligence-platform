"""Data cleaning utilities."""

from __future__ import annotations

from datetime import datetime
import re

import pandas as pd

EXPECTED_COLUMNS = [
    "Nom_Magasin",
    "Ville",
    "Région",
    "Adresse",
    "Latitude",
    "Longitude",
    "Téléphone",
    "Site_Web",
    "Email",
    "Note_Google",
    "Nombre_Avis",
    "Services",
    "Présence_Web",
    "Source",
    "Date_Collecte",
]


def _extract_city_from_address(address: str | None) -> str | None:
    if not address or not isinstance(address, str):
        return None
    parts = [p.strip() for p in address.split(",") if p.strip()]
    return parts[-3] if len(parts) >= 3 else None


def _normalize_phone(phone: str | None) -> str | None:
    if not phone or not isinstance(phone, str):
        return None
    return re.sub(r"\s+", " ", phone).strip()


def clean_and_merge(resultats: list[dict], domaine: str = "", localisation: str = "") -> pd.DataFrame:
    df = pd.DataFrame(resultats)

    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    df["Nom_Magasin"] = df["Nom_Magasin"].astype("string").str.strip()
    df["Adresse"] = df["Adresse"].astype("string").str.strip()
    df["Téléphone"] = df["Téléphone"].apply(_normalize_phone)

    if df["Ville"].isna().all() and "Adresse" in df:
        df["Ville"] = df["Adresse"].apply(_extract_city_from_address)

    df["Région"] = df["Région"].fillna(localisation)
    df["Date_Collecte"] = datetime.now().strftime("%Y-%m-%d")

    for numeric_col in ["Latitude", "Longitude", "Note_Google", "Nombre_Avis"]:
        df[numeric_col] = pd.to_numeric(df[numeric_col], errors="coerce")

    df = df.dropna(subset=["Nom_Magasin"], how="all")
    df = df.drop_duplicates(subset=["Nom_Magasin", "Adresse", "Téléphone"], keep="first")

    return df[EXPECTED_COLUMNS]
