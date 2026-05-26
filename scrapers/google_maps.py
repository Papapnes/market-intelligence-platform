"""Google Maps Places API scraper."""

from __future__ import annotations

import time
from typing import Any

import requests

PLACES_TEXTSEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def _place_details(place_id: str, api_key: str, language: str) -> dict[str, Any]:
    params = {
        "place_id": place_id,
        "key": api_key,
        "language": language,
        "fields": "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,geometry,types",
    }
    response = requests.get(PLACES_DETAILS_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json().get("result", {})


def scrape_google_maps(
    query: str,
    location: str = "",
    rayon_km: int = 50,
    api_key: str | None = None,
    max_results: int = 100,
    langue: str = "fr",
) -> list[dict[str, Any]]:
    """Collect businesses from Google Places Text Search.

    Notes:
        - Requires a Google Maps API key with Places API enabled.
        - Google Text Search pagination returns up to 20 results per page.
    """
    if not api_key:
        raise ValueError("Clé API Google Maps manquante.")

    results: list[dict[str, Any]] = []
    params: dict[str, Any] = {
        "query": query,
        "key": api_key,
        "language": langue,
        "radius": int(rayon_km) * 1000,
    }

    next_page_token = None
    while len(results) < max_results:
        if next_page_token:
            time.sleep(2.2)
            params = {"pagetoken": next_page_token, "key": api_key, "language": langue}

        response = requests.get(PLACES_TEXTSEARCH_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()

        status = payload.get("status")
        if status not in {"OK", "ZERO_RESULTS"}:
            raise RuntimeError(payload.get("error_message") or f"Google Places status: {status}")
        if status == "ZERO_RESULTS":
            break

        for place in payload.get("results", []):
            if len(results) >= max_results:
                break

            details = {}
            place_id = place.get("place_id")
            if place_id:
                try:
                    details = _place_details(place_id, api_key, langue)
                except Exception:
                    details = {}

            source = details or place
            geometry = source.get("geometry", {}).get("location", {})
            results.append(
                {
                    "Nom_Magasin": source.get("name"),
                    "Adresse": source.get("formatted_address"),
                    "Latitude": geometry.get("lat"),
                    "Longitude": geometry.get("lng"),
                    "Téléphone": source.get("formatted_phone_number"),
                    "Site_Web": source.get("website"),
                    "Note_Google": source.get("rating"),
                    "Nombre_Avis": source.get("user_ratings_total"),
                    "Services": ", ".join(source.get("types", []) or []),
                    "Source": "Google Maps API",
                }
            )

        next_page_token = payload.get("next_page_token")
        if not next_page_token:
            break

    return results
