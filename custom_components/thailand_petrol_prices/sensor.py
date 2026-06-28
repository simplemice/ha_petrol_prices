"""Sensor platform for Thailand Petrol Prices."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, FUEL_GRADE_ICONS, FUEL_GRADES, STATIONS
from .coordinator import ThailandPetrolCoordinator

_UNIT = "THB/L"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ThailandPetrolCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []
    for fuel_key in FUEL_GRADES:
        for station_key in STATIONS:
            entities.append(
                PetrolStationSensor(coordinator, entry.entry_id, fuel_key, station_key)
            )
        entities.append(PetrolLowestSensor(coordinator, entry.entry_id, fuel_key))

    async_add_entities(entities)


class _PetrolBase(CoordinatorEntity[ThailandPetrolCoordinator], SensorEntity):
    """Shared base for all petrol price sensors."""

    _attr_attribution = ATTRIBUTION
    _attr_native_unit_of_measurement = _UNIT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_has_entity_name = True

    def __init__(self, coordinator: ThailandPetrolCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="Thailand Petrol Prices",
            manufacturer="Motorist Thailand",
            model="Price Monitor",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.motorist.co.th/en/petrol-prices",
        )


class PetrolStationSensor(_PetrolBase):
    """Price of a specific fuel grade at a specific station."""

    def __init__(
        self,
        coordinator: ThailandPetrolCoordinator,
        entry_id: str,
        fuel_key: str,
        station_key: str,
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._fuel_key = fuel_key
        self._station_key = station_key
        self._attr_unique_id = f"{entry_id}_{fuel_key}_{station_key}"
        self._attr_name = f"{FUEL_GRADES[fuel_key]} {STATIONS[station_key]}"
        self._attr_icon = FUEL_GRADE_ICONS.get(fuel_key, "mdi:gas-station")

    @property
    def native_value(self) -> float | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._fuel_key, {}).get(self._station_key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "fuel_grade": FUEL_GRADES[self._fuel_key],
            "station": STATIONS[self._station_key],
        }


class PetrolLowestSensor(_PetrolBase):
    """Lowest available price for a fuel grade across all stations."""

    def __init__(
        self,
        coordinator: ThailandPetrolCoordinator,
        entry_id: str,
        fuel_key: str,
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._fuel_key = fuel_key
        self._attr_unique_id = f"{entry_id}_{fuel_key}_lowest"
        self._attr_name = f"{FUEL_GRADES[fuel_key]} Lowest"
        self._attr_icon = FUEL_GRADE_ICONS.get(fuel_key, "mdi:gas-station")

    def _available_prices(self) -> dict[str, float]:
        if not self.coordinator.data:
            return {}
        return {
            k: v
            for k, v in self.coordinator.data.get(self._fuel_key, {}).items()
            if v is not None
        }

    @property
    def native_value(self) -> float | None:
        prices = self._available_prices()
        return min(prices.values()) if prices else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        prices = self._available_prices()
        if not prices:
            return {}
        cheapest_key = min(prices, key=prices.__getitem__)
        return {
            "cheapest_station": STATIONS.get(cheapest_key, cheapest_key),
            "fuel_grade": FUEL_GRADES[self._fuel_key],
            "all_prices": {
                STATIONS.get(k, k): v
                for k, v in sorted(prices.items(), key=lambda x: x[1])
            },
        }
