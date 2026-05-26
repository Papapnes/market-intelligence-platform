import streamlit as st
import pandas as pd
import requests
import hashlib
from datetime import datetime
from io import BytesIO

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Market Intelligence Platform",
    page_icon="🌐",
    layout="wide"
)

# =========================
# STYLE
# =========================
st.markdown("""
<style>
.main-title {font-size: 34px; font-weight: 800; color: #2b2d42;}
.subtitle {color: #6c757d; font-size: 15px;}
.profile-name {font-size: 24px; font-weight: 800; color: #2b2d42;}
.profile-role {font-size: 15px; color: #6c757d;}
.stButton > button {border-radius: 10px; height: 45px; font-weight: 600;}
div[data-testid="stMetric"] {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e9ecef;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LANGUAGE DICTIONARY
# =========================
TEXTS = {
    "Français": {
        "title": "🌐 Market Intelligence — Plateforme d’intelligence commerciale",
        "subtitle": "Extraction, enrichissement, scoring et export pour analyse Power BI.",
        "sector": "DOMAINE / SECTEUR D’ACTIVITÉ",
        "country": "PAYS",
        "city": "VILLE / RÉGION",
        "radius": "RAYON (KM)",
        "max_results": "NB. RÉSULTATS MAX",
        "sources": "SOURCES DE DONNÉES",
        "objective": "OBJECTIF ANALYTIQUE",
        "run": "🚀 Lancer l’extraction intelligente",
        "data": "📊 Données enrichies pour Power BI",
        "download_csv": "⬇️ Télécharger CSV Power BI",
        "download_excel": "⬇️ Télécharger Excel avec KPI",
    },
    "English": {
        "title": "🌐 Market Intelligence — Commercial Intelligence Platform",
        "subtitle": "Extraction, enrichment, scoring and export for Power BI analysis.",
        "sector": "BUSINESS SECTOR",
        "country": "COUNTRY",
        "city": "CITY / REGION",
        "radius": "RADIUS (KM)",
        "max_results": "MAX RESULTS",
        "sources": "DATA SOURCES",
        "objective": "ANALYSIS OBJECTIVE",
        "run": "🚀 Run smart extraction",
        "data": "📊 Enriched data for Power BI",
        "download_csv": "⬇️ Download Power BI CSV",
        "download_excel": "⬇️ Download Excel with KPI",
    },
    "العربية": {
        "title": "🌐 منصة ذكاء السوق والتحليل التجاري",
        "subtitle": "استخراج البيانات، إثراؤها، تقييمها وتصديرها لتحليل Power BI.",
        "sector": "قطاع النشاط",
        "country": "البلد",
        "city": "المدينة / المنطقة",
        "radius": "نطاق البحث بالكيلومتر",
        "max_results": "الحد الأقصى للنتائج",
        "sources": "مصادر البيانات",
        "objective": "هدف التحليل",
        "run": "🚀 بدء الاستخراج الذكي",
        "data": "📊 بيانات جاهزة لتحليل Power BI",
        "download_csv": "⬇️ تحميل CSV",
        "download_excel": "⬇️ تحميل Excel مع KPI",
    }
}

# =========================
# SECTOR DICTIONARY
# =========================
SECTOR_DICTIONARY = {
    "informatique": ["computer", "electronics", "mobile_phone", "computer_repair", "it", "software"],
    "computer": ["computer", "electronics", "mobile_phone", "computer_repair", "it", "software"],
    "téléphone": ["mobile_phone", "electronics", "phone", "repair"],
    "mobile": ["mobile_phone", "electronics", "phone", "repair"],
    "pharmacie": ["pharmacy", "chemist"],
    "pharmacy": ["pharmacy", "chemist"],
    "restaurant": ["restaurant", "fast_food", "cafe"],
    "café": ["cafe", "restaurant"],
    "coiffure": ["hairdresser", "beauty"],
    "beauty": ["hairdresser", "beauty", "cosmetics"],
    "automobile": ["car", "car_repair", "auto_parts", "vehicle"],
    "auto": ["car", "car_repair", "auto_parts", "vehicle"],
    "immobilier": ["real_estate", "estate_agent"],
    "real estate": ["real_estate", "estate_agent"],
    "clinique": ["clinic", "doctors", "dentist"],
    "clinic": ["clinic", "doctors", "dentist"],
    "épicerie": ["supermarket", "convenience", "grocery"],
    "grocery": ["supermarket", "convenience", "grocery"],
    "vêtement": ["clothes", "fashion", "shoes"],
    "clothes": ["clothes", "fashion", "shoes"],
    "banque": ["bank", "financial", "atm"],
    "bank": ["bank", "financial", "atm"],
}

# =========================
# HEADER PROFILE
# =========================
col_img, col_info = st.columns([1, 5])

with col_img:
    try:
        st.image("assets/profile.jpg", width=110)
    except Exception:
        st.write("")

with col_info:
    st.markdown('<div class="profile-name">Abdelkader Bouzourine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="profile-role">Data Analyst | Business Intelligence | Python | Power BI</div>',
        unsafe_allow_html=True
    )
    st.markdown("[Portfolio](https://papapnes.github.io/Portfolio_Abdel/)")

st.divider()

# =========================
# LANGUAGE SELECTION
# =========================
app_language = st.selectbox(
    "Langue / Language / اللغة",
    ["Français", "English", "العربية"]
)

T = TEXTS[app_language]

st.markdown(f'<div class="main-title">{T["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">{T["subtitle"]}</div>', unsafe_allow_html=True)
st.write("")

# =========================
# USER INTERFACE
# =========================
with st.container(border=True):
    secteur_options = [
        "informatique",
        "computer",
        "téléphone",
        "mobile",
        "pharmacie",
        "restaurant",
        "café",
        "coiffure",
        "automobile",
        "immobilier",
        "clinique",
        "épicerie",
        "vêtement",
        "banque",
        "Autre / Custom"
    ]

    selected_sector = st.selectbox(T["sector"], secteur_options)

    if selected_sector == "Autre / Custom":
        domaine = st.text_input(T["sector"], placeholder="ex: electronics, bakery, gym...")
    else:
        domaine = selected_sector

    col1, col2 = st.columns(2)

    with col1:
        pays = st.text_input(T["country"], placeholder="ex: Canada")

    with col2:
        ville = st.text_input(T["city"], placeholder="ex: Montréal")

    col3, col4 = st.columns(2)

    with col3:
        rayon = st.number_input(T["radius"], min_value=1, max_value=500, value=25)

    with col4:
        max_results = st.number_input(T["max_results"], min_value=10, max_value=3000, value=500)

    st.markdown(f"### {T['sources']}")
    source_osm = st.checkbox("OpenStreetMap", value=True)
    source_sites = st.checkbox("Sites web / Websites", value=False)

    st.info(
        "OpenStreetMap est utilisé pour l’extraction principale. "
        "L’option Sites web est préparée pour une prochaine étape d’enrichissement."
    )

    st.markdown(f"### {T['objective']}")
    objectif = st.selectbox(
        T["objective"],
        [
            "Analyse de marché",
            "Prospection B2B",
            "Analyse concurrence",
            "Détection des commerces winners",
            "Cartographie commerciale"
        ]
    )

    lancer = st.button(T["run"], use_container_width=True)

# =========================
# FUNCTIONS
# =========================
def generate_business_id(name, city, address, lat, lon):
    raw = f"{name}_{city}_{address}_{lat}_{lon}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()


def expand_keywords(domain):
    domain_lower = domain.lower().strip()
    base_keywords = domain_lower.split()

    expanded = []
    for keyword in base_keywords:
        expanded.append(keyword)
        if keyword in SECTOR_DICTIONARY:
            expanded.extend(SECTOR_DICTIONARY[keyword])

    if domain_lower in SECTOR_DICTIONARY:
        expanded.extend(SECTOR_DICTIONARY[domain_lower])

    return list(set(expanded))


def geocode_location(city, country):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"{city}, {country}", "format": "json", "limit": 1}
    headers = {"User-Agent": "market-intelligence-app"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        data = response.json()
    except Exception:
        st.error("Erreur lors du géocodage de la localisation.")
        return None, None

    if not data:
        return None, None

    return float(data[0]["lat"]), float(data[0]["lon"])


def calculate_business_score(row):
    score = 0

    if row["Telephone"]:
        score += 20
    if row["Website"]:
        score += 25
    if row["Email"]:
        score += 20
    if row["Address"]:
        score += 15
    if row["Latitude"] and row["Longitude"]:
        score += 20

    return score


def classify_business(score):
    if score >= 75:
        return "Winner"
    elif score >= 45:
        return "Moyen"
    else:
        return "Faible"


def classify_digital_maturity(row):
    if row["Website"] and row["Email"] and row["Telephone"]:
        return "Élevée"
    elif row["Website"] or row["Email"]:
        return "Moyenne"
    else:
        return "Faible"


def extract_from_osm(
    domain,
    lat,
    lon,
    radius_km,
    max_results,
    city,
    country,
    objectif,
    source_sites=False
):
    radius_m = radius_km * 1000
    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json][timeout:90];
    (
      node["shop"](around:{radius_m},{lat},{lon});
      way["shop"](around:{radius_m},{lat},{lon});
      relation["shop"](around:{radius_m},{lat},{lon});

      node["office"](around:{radius_m},{lat},{lon});
      way["office"](around:{radius_m},{lat},{lon});

      node["amenity"](around:{radius_m},{lat},{lon});
      way["amenity"](around:{radius_m},{lat},{lon});
    );
    out center;
    """

    try:
        response = requests.post(
            overpass_url,
            data={"data": query},
            timeout=120,
            headers={"User-Agent": "market-intelligence-app"}
        )
    except Exception:
        st.error("Erreur de connexion avec Overpass API.")
        return pd.DataFrame()

    if response.status_code != 200:
        st.error(f"Erreur API Overpass : {response.status_code}")
        return pd.DataFrame()

    if not response.text.strip():
        st.error("Réponse vide de Overpass API.")
        return pd.DataFrame()

    try:
        data = response.json()
    except Exception:
        st.error("Impossible de lire la réponse JSON.")
        st.code(response.text[:1000])
        return pd.DataFrame()

    rows = []
    keywords = expand_keywords(domain)
    now = datetime.today()

    for element in data.get("elements", []):
        tags = element.get("tags", {})

        name = tags.get("name", "")
        category_text = " ".join(str(v).lower() for v in tags.values())

        if not name:
            continue

        if not any(keyword in category_text or keyword in name.lower() for keyword in keywords):
            continue

        lat_value = element.get("lat") or element.get("center", {}).get("lat")
        lon_value = element.get("lon") or element.get("center", {}).get("lon")

        full_address = " ".join([
            tags.get("addr:housenumber", ""),
            tags.get("addr:street", "")
        ]).strip()

        phone = tags.get("phone", tags.get("contact:phone", ""))
        website = tags.get("website", tags.get("contact:website", ""))
        email = tags.get("email", tags.get("contact:email", ""))

        category = tags.get("shop", tags.get("amenity", tags.get("office", "")))
        opening_hours = tags.get("opening_hours", "")

        row = {
            "Business_ID": generate_business_id(name, city, full_address, lat_value, lon_value),

            "Business_Name": name,
            "Category": category,
            "Sub_Category": tags.get("brand", ""),
            "Description": category_text[:250],
            "Services": category,

            "Address": full_address,
            "City": tags.get("addr:city", city),
            "Region": tags.get("addr:region", ""),
            "Province": tags.get("addr:province", ""),
            "Country": country,
            "Postal_Code": tags.get("addr:postcode", ""),
            "Latitude": lat_value,
            "Longitude": lon_value,

            "Telephone": phone,
            "Email": email,
            "Website": website,

            "Opening_Hours": opening_hours,

            "Facebook_URL": "",
            "Instagram_URL": "",
            "TikTok_URL": "",
            "LinkedIn_URL": "",

            "Presence_Web": "Oui" if website else "Non",
            "Presence_Email": "Oui" if email else "Non",
            "Presence_Telephone": "Oui" if phone else "Non",
            "Presence_Address": "Oui" if full_address else "Non",
            "Presence_Opening_Hours": "Oui" if opening_hours else "Non",
            "Contact_Complete": "Oui" if phone and website and email else "Non",

            "Google_Rating": None,
            "Review_Count": None,
            "Reputation_Score": None,

            "Search_Domain": domain,
            "Expanded_Search_Keywords": ", ".join(keywords),
            "Source_Data": "OpenStreetMap",
            "Source_Extraction": "OpenStreetMap",
            "Website_Enrichment_Selected": "Oui" if source_sites else "Non",
            "Analysis_Objective": objectif,

            "Date_Collecte": now.strftime("%Y-%m-%d")
        }

        rows.append(row)

        if len(rows) >= max_results:
            break

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df["Business_Score"] = df.apply(calculate_business_score, axis=1)
    df["Business_Status"] = df["Business_Score"].apply(classify_business)
    df["Digital_Maturity"] = df.apply(classify_digital_maturity, axis=1)

    df["Social_Network_Count"] = (
        df[["Facebook_URL", "Instagram_URL", "TikTok_URL", "LinkedIn_URL"]]
        .astype(bool)
        .sum(axis=1)
    )

    df["AI_Potential_Level"] = df["Business_Score"].apply(
        lambda x: "Fort potentiel" if x >= 75
        else "Potentiel moyen" if x >= 45
        else "Faible potentiel"
    )

    df["AI_Recommendation"] = df["Business_Status"].apply(
        lambda x: "Priorité prospection" if x == "Winner"
        else "À surveiller" if x == "Moyen"
        else "Faible priorité"
    )

    df["Possible_Duplicate"] = df.duplicated(
        subset=["Business_Name", "Telephone"],
        keep=False
    ).map({True: "Oui", False: "Non"})

    df["Multi_Location"] = df.duplicated(
        subset=["Business_Name"],
        keep=False
    ).map({True: "Oui", False: "Non"})

    df["Franchise_Group"] = df["Business_Name"]

    return df


def to_excel(df):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data_Commerces")

        summary = pd.DataFrame({
            "KPI": [
                "Total commerces",
                "Avec téléphone",
                "Avec email",
                "Avec site web",
                "Avec adresse",
                "Avec heures ouverture",
                "Contact complet",
                "Business score moyen",
                "Commerces Winner",
                "Commerces moyens",
                "Commerces faibles",
                "Possibles doublons",
                "Multi-location",
                "Présence web %",
                "Présence horaires %"
            ],
            "Valeur": [
                len(df),
                int((df["Presence_Telephone"] == "Oui").sum()),
                int((df["Presence_Email"] == "Oui").sum()),
                int((df["Presence_Web"] == "Oui").sum()),
                int((df["Presence_Address"] == "Oui").sum()),
                int((df["Presence_Opening_Hours"] == "Oui").sum()),
                int((df["Contact_Complete"] == "Oui").sum()),
                round(df["Business_Score"].mean(), 2),
                int((df["Business_Status"] == "Winner").sum()),
                int((df["Business_Status"] == "Moyen").sum()),
                int((df["Business_Status"] == "Faible").sum()),
                int((df["Possible_Duplicate"] == "Oui").sum()),
                int((df["Multi_Location"] == "Oui").sum()),
                round((df["Presence_Web"] == "Oui").mean() * 100, 2),
                round((df["Presence_Opening_Hours"] == "Oui").mean() * 100, 2)
            ]
        })

        summary.to_excel(writer, index=False, sheet_name="Résumé_KPI")

    return output.getvalue()


# =========================
# EXECUTION
# =========================
if lancer:
    if not domaine or not pays or not ville:
        st.error("Veuillez remplir le domaine, le pays et la ville.")
    elif not source_osm:
        st.error("Veuillez sélectionner OpenStreetMap comme source principale.")
    else:
        with st.spinner("Extraction et enrichissement en cours..."):
            lat, lon = geocode_location(ville, pays)

            if lat is None:
                st.error("Localisation introuvable.")
            else:
                df = extract_from_osm(
                    domain=domaine,
                    lat=lat,
                    lon=lon,
                    radius_km=rayon,
                    max_results=max_results,
                    city=ville,
                    country=pays,
                    objectif=objectif,
                    source_sites=source_sites
                )

                if df.empty:
                    st.warning(
                        "Aucun résultat trouvé. Essayez un mot-clé plus général : "
                        "computer, electronics, mobile, repair."
                    )
                else:
                    st.success(f"{len(df)} commerces enrichis trouvés.")

                    col_a, col_b, col_c, col_d, col_e = st.columns(5)

                    with col_a:
                        st.metric("Total commerces", len(df))
                    with col_b:
                        st.metric("Avec téléphone", int((df["Presence_Telephone"] == "Oui").sum()))
                    with col_c:
                        st.metric("Avec site web", int((df["Presence_Web"] == "Oui").sum()))
                    with col_d:
                        st.metric("Avec email", int((df["Presence_Email"] == "Oui").sum()))
                    with col_e:
                        st.metric("Avec horaires", int((df["Presence_Opening_Hours"] == "Oui").sum()))

                    st.markdown("### 📈 KPI Business Intelligence")

                    k1, k2, k3, k4 = st.columns(4)

                    with k1:
                        st.metric("Présence Web %", round((df["Presence_Web"] == "Oui").mean() * 100, 1))
                    with k2:
                        st.metric("Présence horaires %", round((df["Presence_Opening_Hours"] == "Oui").mean() * 100, 1))
                    with k3:
                        st.metric("Franchises détectées", int((df["Multi_Location"] == "Oui").sum()))
                    with k4:
                        st.metric("Doublons potentiels", int((df["Possible_Duplicate"] == "Oui").sum()))

                    st.markdown("### 🏆 Répartition des commerces")

                    c1, c2, c3, c4 = st.columns(4)

                    with c1:
                        st.metric("Winner", int((df["Business_Status"] == "Winner").sum()))
                    with c2:
                        st.metric("Moyen", int((df["Business_Status"] == "Moyen").sum()))
                    with c3:
                        st.metric("Faible", int((df["Business_Status"] == "Faible").sum()))
                    with c4:
                        st.metric("Business Score moyen", round(df["Business_Score"].mean(), 1))

                    st.markdown(f"### {T['data']}")
                    st.dataframe(df, use_container_width=True)

                    csv = df.to_csv(index=False).encode("utf-8-sig")
                    excel = to_excel(df)

                    col_csv, col_excel = st.columns(2)

                    with col_csv:
                        st.download_button(
                            T["download_csv"],
                            data=csv,
                            file_name="market_intelligence_powerbi.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                    with col_excel:
                        st.download_button(
                            T["download_excel"],
                            data=excel,
                            file_name="market_intelligence_powerbi.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )