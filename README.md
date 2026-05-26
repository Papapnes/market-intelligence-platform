# Market Intelligence App

Application Streamlit pour collecter, nettoyer et exporter des données d'établissements selon un secteur et une localisation.

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Structure

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

## Notes

- La source Google Maps fonctionne avec une clé API Google Places.
- Les modules Pages Jaunes, Facebook et Web général sont des placeholders pour garder l'application stable.
- Pour la production, utilisez des API officielles et respectez les conditions d'utilisation des sources.
