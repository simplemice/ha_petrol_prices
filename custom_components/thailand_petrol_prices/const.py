"""Constants for the Thailand Petrol Prices integration."""
from __future__ import annotations

DOMAIN = "thailand_petrol_prices"

CONF_UPDATE_INTERVAL = "update_interval"
DEFAULT_UPDATE_INTERVAL = 3600  # 1 hour
MIN_UPDATE_INTERVAL = 300       # 5 minutes
MAX_UPDATE_INTERVAL = 86400     # 24 hours

PETROL_URL = "https://www.motorist.co.th/en/petrol-prices"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Ordered to match the website table row order
FUEL_GRADES: dict[str, str] = {
    "gasohol_95": "Gasohol 95",
    "gasohol_e20": "Gasohol E20",
    "gasohol_e85": "Gasohol E85",
    "gasohol_91": "Gasohol 91",
    "gasohol_95_premium": "Gasohol 95 Premium",
    "benzin_95": "Benzin 95",
    "diesel_b7": "Diesel B7",
    "diesel_b7_premium": "Diesel B7 Premium",
}

# Ordered to match the website table column order
STATIONS: dict[str, str] = {
    "ptt": "PTT",
    "bcp": "BCP",
    "shell": "Shell",
    "caltex": "Caltex",
    "irpc": "IRPC",
    "pt": "PT",
    "susco": "Susco",
    "pure": "Pure",
}

FUEL_GRADE_ICONS: dict[str, str] = {
    "gasohol_95": "mdi:gas-station",
    "gasohol_e20": "mdi:leaf",
    "gasohol_e85": "mdi:leaf",
    "gasohol_91": "mdi:gas-station",
    "gasohol_95_premium": "mdi:gas-station-outline",
    "benzin_95": "mdi:fuel",
    "diesel_b7": "mdi:barrel",
    "diesel_b7_premium": "mdi:barrel-outline",
}

ATTRIBUTION = "Data provided by Motorist Thailand (motorist.co.th)"
