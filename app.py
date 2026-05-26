"""
Market Intelligence Tool — Application principale Streamlit
Version corrigée pour GitHub / Streamlit.
"""

from __future__ import annotations

from datetime import datetime
import time

import pandas as pd
import streamlit as st

from scrapers.google_maps import scrape_google_maps
from scrapers.pages_jaunes import scrape_pages_jaunes
from scrapers.facebook import scrape_facebook_pages
from scrapers.web_search import scrape_web_generic
from utils.data_cleaner import clean_and_merge
from utils.export import export_csv, export_excel, export_json


st.set_page_config(
    page_title="Market Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    [data-testid="stSidebar"] { background: #0f0f1a; }
    [data-testid="stSidebar"] * { color: #e0e0f0 !important; }
    .stTextInput > div > div > input { border-radius: 8px; }
    h1 { font-size: 1.8rem !important; }
</style>
""",
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("## ⚙️ Paramètres")
    st.markdown("---")

    domaine = st.text_input(
        "🏷️ Domaine / Secteur",
        placeholder="ex: magasin informatique, réparation cellulaire...",
        help="Le type d'établissement à rechercher",
    )

    st.markdown("**📍 Localisation**")
    col_pays, col_ville = st.columns(2)
    with col_pays:
        pays = st.text_input("Pays", value="Canada")
    with col_ville:
        ville = st.text_input("Ville", placeholder="Montréal")

    region = st.text_input("Région / Province", value="Québec")
    rayon_km = st.slider("Rayon de recherche (km)", 5, 500, 50)

    st.markdown("---")
    st.markdown("**🌐 Sources de données**")

    src_gmaps = st.checkbox("🗺️ Google Maps API", value=True)
    src_pj = st.checkbox("📖 Pages Jaunes", value=False)
    src_facebook = st.checkbox("📘 Facebook Pages", value=False)
    src_web = st.checkbox("🔎 Web général", value=False)

    st.markdown("---")
    st.markdown("**🔧 Options avancées**")
    max_results = st.number_input("Résultats max", 10, 2000, 100, step=10)
    langue = st.selectbox("Langue résultats", ["fr", "en"])
    google_api_key = st.text_input(
        "Clé API Google Maps",
        type="password",
        placeholder="AIza...",
        help="Requis pour la source Google Maps API.",
    )

    lancer = st.button("🚀 Lancer l'extraction", use_container_width=True, type="primary")


st.title("🔍 Market Intelligence — Extracteur de données")
st.caption("Collectez et nettoyez des données d'établissements selon un secteur et une localisation.")

tab_resultats, tab_carte, tab_export, tab_guide = st.tabs(
    ["📊 Résultats", "🗺️ Carte", "⬇️ Export", "📖 Guide"]
)


def build_query(domain: str, city: str, country: str, province: str) -> tuple[str, str]:
    parts = [domain, city, province, country]
    query = " ".join([p.strip() for p in parts if p and p.strip()])
    location_parts = [city, province, country]
    location = ", ".join([p.strip() for p in location_parts if p and p.strip()])
    return query, location


if lancer:
    if not domaine.strip():
        st.error("⚠️ Veuillez renseigner un domaine/secteur.")
        st.stop()
    if not any([pays.strip(), ville.strip(), region.strip()]):
        st.error("⚠️ Veuillez renseigner au moins une localisation.")
        st.stop()

    query, localisation = build_query(domaine, ville, pays, region)

    sources_actives = []
    if src_gmaps:
        sources_actives.append(
            (
                "Google Maps API",
                scrape_google_maps,
                dict(
                    query=query,
                    location=localisation,
                    rayon_km=rayon_km,
                    api_key=google_api_key,
                    max_results=int(max_results),
                    langue=langue,
                ),
            )
        )
    if src_pj:
        sources_actives.append(
            (
                "Pages Jaunes",
                scrape_pages_jaunes,
                dict(query=domaine, ville=ville, pays=pays, max_results=int(max_results)),
            )
        )
    if src_facebook:
        sources_actives.append(
            (
                "Facebook",
                scrape_facebook_pages,
                dict(query=query, location=localisation, max_results=int(max_results)),
            )
        )
    if src_web:
        sources_actives.append(
            (
                "Web général",
                scrape_web_generic,
                dict(query=query, location=localisation, max_results=int(max_results)),
            )
        )

    if not sources_actives:
        st.error("⚠️ Veuillez activer au moins une source de données.")
        st.stop()

    resultats = []
    with st.spinner("🔄 Extraction en cours..."):
        progress = st.progress(0)
        status = st.empty()

        for i, (nom_source, fn_scraper, kwargs) in enumerate(sources_actives):
            status.info(f"🔎 Collecte depuis **{nom_source}**...")
            try:
                data = fn_scraper(**kwargs)
                if data:
                    resultats.extend(data)
                status.success(f"✅ {nom_source} : {len(data) if data else 0} résultats")
            except Exception as exc:
                status.warning(f"⚠️ {nom_source} : {exc}")

            progress.progress((i + 1) / len(sources_actives))
            time.sleep(0.2)

        progress.empty()
        status.empty()

    if resultats:
        df = clean_and_merge(resultats, domaine=domaine, localisation=localisation)
        st.session_state["df"] = df
        st.session_state["meta"] = {
            "domaine": domaine,
            "localisation": localisation,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        st.success(f"✅ {len(df)} établissements extraits avec succès !")
    else:
        st.error("Aucun résultat. Vérifiez vos paramètres, votre clé API ou activez une autre source.")


with tab_resultats:
    if "df" not in st.session_state:
        st.info("👈 Configurez votre recherche dans la barre latérale et cliquez sur **Lancer l'extraction**.")
        cols = [
            "Nom_Magasin", "Ville", "Région", "Adresse", "Latitude", "Longitude", "Téléphone",
            "Site_Web", "Email", "Note_Google", "Nombre_Avis", "Services", "Présence_Web", "Source", "Date_Collecte",
        ]
        st.dataframe(pd.DataFrame({"Colonnes prévues": cols}), use_container_width=True, hide_index=True)
    else:
        df = st.session_state["df"]
        meta = st.session_state["meta"]
        st.caption(f"Domaine : **{meta['domaine']}** | Zone : **{meta['localisation']}** | Extrait le : {meta['date']}")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total", len(df))
        c2.metric("Avec site web", f"{int(df['Site_Web'].notna().mean() * 100)}%" if "Site_Web" in df else "—")
        c3.metric("Note moyenne", f"{df['Note_Google'].dropna().mean():.1f}/5" if "Note_Google" in df and df['Note_Google'].notna().any() else "—")
        c4.metric("Avec téléphone", f"{int(df['Téléphone'].notna().mean() * 100)}%" if "Téléphone" in df else "—")
        c5.metric("Villes couvertes", df["Ville"].nunique() if "Ville" in df else "—")

        st.markdown("---")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtre_ville = st.multiselect("Filtrer par ville", sorted(df["Ville"].dropna().unique()) if "Ville" in df else [])
        with col_f2:
            note_min = st.slider("Note min", 0.0, 5.0, 0.0, 0.5)
        with col_f3:
            filtre_web = st.checkbox("Avec site web seulement")

        df_affiche = df.copy()
        if filtre_ville and "Ville" in df_affiche:
            df_affiche = df_affiche[df_affiche["Ville"].isin(filtre_ville)]
        if note_min > 0 and "Note_Google" in df_affiche:
            df_affiche = df_affiche[df_affiche["Note_Google"].fillna(0) >= note_min]
        if filtre_web and "Site_Web" in df_affiche:
            df_affiche = df_affiche[df_affiche["Site_Web"].notna()]

        st.dataframe(df_affiche, use_container_width=True, hide_index=True)
        st.caption(f"{len(df_affiche)} lignes affichées")


with tab_carte:
    if "df" not in st.session_state:
        st.info("Lancez d'abord une extraction.")
    else:
        df = st.session_state["df"]
        if {"Latitude", "Longitude"}.issubset(df.columns):
            df_map = df.dropna(subset=["Latitude", "Longitude"]).copy()
            if not df_map.empty:
                df_map = df_map.rename(columns={"Latitude": "lat", "Longitude": "lon"})
                st.map(df_map[["lat", "lon"]])
                st.caption(f"{len(df_map)} établissements géolocalisés affichés")
            else:
                st.warning("Aucune coordonnée GPS disponible.")
        else:
            st.warning("Pas de coordonnées GPS disponibles pour cette extraction.")


with tab_export:
    if "df" not in st.session_state:
        st.info("Lancez d'abord une extraction.")
    else:
        df = st.session_state["df"]
        meta = st.session_state["meta"]
        slug = f"{meta['domaine']}_{meta['localisation']}_{datetime.now().strftime('%Y%m%d')}"
        slug = slug.replace(" ", "_").replace(",", "").replace("/", "-")

        st.markdown("### ⬇️ Télécharger vos données")
        col_e1, col_e2, col_e3 = st.columns(3)

        with col_e1:
            st.download_button("📄 Télécharger CSV", export_csv(df), f"{slug}.csv", "text/csv", use_container_width=True)
        with col_e2:
            st.download_button(
                "📊 Télécharger Excel",
                export_excel(df, meta),
                f"{slug}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col_e3:
            st.download_button("📦 Télécharger JSON", export_json(df, meta), f"{slug}.json", "application/json", use_container_width=True)

        st.markdown("---")
        st.markdown("### 👁️ Aperçu des données")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)


with tab_guide:
    st.markdown(
        """
## 📖 Guide d'utilisation

### Structure GitHub recommandée
```text
market-intelligence-app/
├── app.py
├── requirements.txt
├── README.md
├── scrapers/
│   ├── __init__.py
│   ├── google_maps.py
│   ├── pages_jaunes.py
│   ├── facebook.py
│   └── web_search.py
└── utils/
    ├── __init__.py
    ├── data_cleaner.py
    └── export.py
```

### Google Maps API
- Activez **Places API** dans Google Cloud.
- Créez une clé API.
- Collez la clé dans la barre latérale.

### Note importante
Respectez les conditions d'utilisation des sites. Pour un projet stable, privilégiez les API officielles.
"""
    )
