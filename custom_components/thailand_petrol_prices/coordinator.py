"""DataUpdateCoordinator for Thailand Petrol Prices."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, FUEL_GRADES, PETROL_URL, STATIONS, USER_AGENT

_LOGGER = logging.getLogger(__name__)

# Known stable column order: grade name is index 0, stations start at index 1
_STATION_ORDER = list(STATIONS.keys())


class ThailandPetrolCoordinator(
    DataUpdateCoordinator[dict[str, dict[str, float | None]]]
):
    """Fetches and parses Thailand fuel prices from motorist.co.th."""

    def __init__(self, hass: HomeAssistant, update_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, dict[str, float | None]]:
        try:
            async with self._session.get(
                PETROL_URL,
                headers={"User-Agent": USER_AGENT},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                resp.raise_for_status()
                html = await resp.text()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching petrol prices: {err}") from err

        try:
            return self._parse(html)
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Error parsing petrol price data: {err}") from err

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    def _parse(self, html: str) -> dict[str, dict[str, float | None]]:
        soup = BeautifulSoup(html, "html.parser")

        table = soup.select_one("div.th-fuel-table table")
        if not table:
            raise UpdateFailed("Fuel price table not found on the page")

        station_map = self._detect_station_columns(table)

        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]

        data: dict[str, dict[str, float | None]] = {}
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue

            grade_raw = cells[0].get_text(strip=True)
            fuel_key = _match_fuel_grade(grade_raw)
            if fuel_key is None:
                _LOGGER.debug("Unrecognised fuel grade row: %r", grade_raw)
                continue

            row_prices: dict[str, float | None] = {}
            for station_key, col_idx in station_map.items():
                cell_text = cells[col_idx].get_text(strip=True) if col_idx < len(cells) else ""
                row_prices[station_key] = _parse_price(cell_text)

            data[fuel_key] = row_prices

        if not data:
            raise UpdateFailed("No fuel price rows could be parsed from the page")

        _LOGGER.debug("Parsed %d fuel grades", len(data))
        return data

    def _detect_station_columns(self, table) -> dict[str, int]:
        """Try to map station keys to column indices from the header row."""
        header_row = table.select_one("thead tr") or table.find("tr")
        detected: dict[str, int] = {}

        if header_row:
            cells = header_row.find_all(["th", "td"])
            for idx, cell in enumerate(cells):
                if idx == 0:
                    continue  # grade name column
                text = ""
                img = cell.find("img")
                if img:
                    text = img.get("alt", "") or img.get("title", "")
                if not text:
                    text = cell.get_text(strip=True)
                text_lower = text.lower().strip()

                for station_key, station_name in STATIONS.items():
                    if station_name.lower() in text_lower:
                        detected[station_key] = idx
                        break

        if len(detected) >= len(STATIONS) // 2:
            _LOGGER.debug("Station columns detected from header: %s", detected)
            return detected

        # Fallback: use known fixed column order (matches motorist.co.th layout)
        _LOGGER.info(
            "Could not reliably detect station columns from header; using fixed order"
        )
        return {key: idx for idx, key in enumerate(_STATION_ORDER, start=1)}


# ------------------------------------------------------------------
# Pure functions (no self dependency)
# ------------------------------------------------------------------

def _match_fuel_grade(name: str) -> str | None:
    """Map a display name from the website to an internal fuel key."""
    n = name.lower()
    # Check most-specific patterns first to avoid false matches
    if "premium" in n:
        if "diesel" in n or "b7" in n:
            return "diesel_b7_premium"
        return "gasohol_95_premium"
    if "e85" in n:
        return "gasohol_e85"
    if "e20" in n:
        return "gasohol_e20"
    if "benzin" in n:
        return "benzin_95"
    if "diesel" in n or "b7" in n:
        return "diesel_b7"
    if "91" in n:
        return "gasohol_91"
    if "95" in n:
        return "gasohol_95"
    return None


def _parse_price(text: str) -> float | None:
    """Convert a price string like '฿38.05' or '-' to a float."""
    cleaned = text.replace("฿", "").replace(",", "").strip()
    if not cleaned or cleaned == "-":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None
