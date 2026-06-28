# Thailand Petrol Prices

[![HACS Default][hacs-shield]][hacs-link]
[![GitHub Release][release-shield]][release-link]
[![License][license-shield]](LICENSE)

A custom Home Assistant integration that monitors **live fuel prices in Thailand** by scraping [motorist.co.th](https://www.motorist.co.th/en/petrol-prices).

Prices cover **Bangkok, Nonthaburi, Pathum Thani and Samut Prakan** and are updated once per hour by default.

---

## Features

- **72 sensors** out of the box — 64 per-station prices + 8 lowest-price sensors
- Covers **8 fuel grades** and **8 major station brands**
- Lowest-price sensors expose a `cheapest_station` attribute and a full `all_prices` breakdown
- Config Flow setup — no YAML editing required
- Configurable update interval (5 min – 24 h)
- Full HACS support and automatic GitHub releases on version bump

---

## Supported Fuel Grades

| Key | Display Name |
|---|---|
| `gasohol_95` | Gasohol 95 |
| `gasohol_e20` | Gasohol E20 |
| `gasohol_e85` | Gasohol E85 |
| `gasohol_91` | Gasohol 91 |
| `gasohol_95_premium` | Gasohol 95 Premium |
| `benzin_95` | Benzin 95 |
| `diesel_b7` | Diesel B7 |
| `diesel_b7_premium` | Diesel B7 Premium |

## Supported Stations

PTT · BCP · Shell · Caltex · IRPC · PT · Susco · Pure

---

## Sensors

### Station price sensors (64)

Each sensor has the form **`sensor.thailand_petrol_<fuel_grade>_<station>`**.

| Entity ID example | State | Unit |
|---|---|---|
| `sensor.thailand_petrol_gasohol_91_ptt` | `34.36` | THB/L |
| `sensor.thailand_petrol_diesel_b7_shell` | `33.54` | THB/L |

Attributes: `fuel_grade`, `station`

### Lowest price sensors (8)

One sensor per fuel grade: **`sensor.thailand_petrol_<fuel_grade>_lowest`**

| Entity ID example | State | Notable attributes |
|---|---|---|
| `sensor.thailand_petrol_gasohol_91_lowest` | `34.36` | `cheapest_station`, `all_prices` |
| `sensor.thailand_petrol_diesel_b7_lowest` | `33.54` | `cheapest_station`, `all_prices` |

The `all_prices` attribute contains a dictionary of all available station prices sorted cheapest first.

---

## Installation

### Via HACS (recommended)

1. Open **HACS** in Home Assistant.
2. Click the three-dot menu → **Custom repositories**.
3. Add `https://github.com/simplemice/ha_petrol_prices` as an **Integration**.
4. Search for **Thailand Petrol Prices** and click **Download**.
5. Restart Home Assistant.

### Manual installation

1. Download the latest release zip from the [Releases](https://github.com/simplemice/ha_petrol_prices/releases) page.
2. Extract the `thailand_petrol_prices` folder into your `<config>/custom_components/` directory.
3. Restart Home Assistant.

---

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Thailand Petrol Prices**.
3. Click **Submit** — the integration fetches prices immediately.

### Options

After setup, click **Configure** on the integration card to change the update interval.

| Option | Default | Range |
|---|---|---|
| Update interval (seconds) | `3600` (1 h) | 300 – 86400 |

---

## Automation Examples

### Notify when Gasohol 91 drops below a target price

```yaml
automation:
  - alias: "Notify cheap Gasohol 91"
    trigger:
      - platform: numeric_state
        entity_id: sensor.thailand_petrol_gasohol_91_lowest
        below: 34.00
    action:
      - service: notify.mobile_app_my_phone
        data:
          title: "Cheap fuel alert"
          message: >
            Gasohol 91 is now {{ states('sensor.thailand_petrol_gasohol_91_lowest') }} THB/L
            at {{ state_attr('sensor.thailand_petrol_gasohol_91_lowest', 'cheapest_station') }}.
```

### Weekly fuel cost summary

```yaml
automation:
  - alias: "Weekly fuel summary"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: time
        weekday:
          - mon
    action:
      - service: notify.mobile_app_my_phone
        data:
          title: "This week's fuel prices"
          message: >
            Gasohol 91 cheapest: {{ states('sensor.thailand_petrol_gasohol_91_lowest') }} THB/L
            ({{ state_attr('sensor.thailand_petrol_gasohol_91_lowest', 'cheapest_station') }})
            Diesel B7 cheapest: {{ states('sensor.thailand_petrol_diesel_b7_lowest') }} THB/L
            ({{ state_attr('sensor.thailand_petrol_diesel_b7_lowest', 'cheapest_station') }})
```

### Dashboard card — all Gasohol 91 prices

```yaml
type: entities
title: Gasohol 91 Prices
entities:
  - entity: sensor.thailand_petrol_gasohol_91_ptt
  - entity: sensor.thailand_petrol_gasohol_91_bcp
  - entity: sensor.thailand_petrol_gasohol_91_shell
  - entity: sensor.thailand_petrol_gasohol_91_caltex
  - entity: sensor.thailand_petrol_gasohol_91_irpc
  - entity: sensor.thailand_petrol_gasohol_91_pt
  - entity: sensor.thailand_petrol_gasohol_91_susco
  - entity: sensor.thailand_petrol_gasohol_91_pure
  - entity: sensor.thailand_petrol_gasohol_91_lowest
    name: "Lowest (any station)"
```

### Template sensor — show cheapest station name alongside price

```yaml
template:
  - sensor:
      - name: "Best Gasohol 91 deal"
        state: >
          {{ states('sensor.thailand_petrol_gasohol_91_lowest') }} THB/L
          at {{ state_attr('sensor.thailand_petrol_gasohol_91_lowest', 'cheapest_station') }}
        icon: mdi:gas-station
```

---

## Migrating from the multiscrape sensors.yaml

If you were using the `multiscrape` + `template` approach from `sensors.yaml`, the new entity IDs map like this:

| Old entity ID | New entity ID |
|---|---|
| `sensor.gasohol_91_price_ptt` | `sensor.thailand_petrol_gasohol_91_ptt` |
| `sensor.gasohol_91_price_bcp` | `sensor.thailand_petrol_gasohol_91_bcp` |
| `sensor.gasohol_91_price_shell` | `sensor.thailand_petrol_gasohol_91_shell` |
| `sensor.gasohol_95_price_ptt` | `sensor.thailand_petrol_gasohol_95_ptt` |
| Lowest 91 template sensor | `sensor.thailand_petrol_gasohol_91_lowest` |
| Lowest 95 template sensor | `sensor.thailand_petrol_gasohol_95_lowest` |

The new sensors return numeric values (e.g. `34.36`) instead of formatted strings (e.g. `฿34.36 at PTT Station`), making them easier to use in conditions and statistics.

---

## Troubleshooting

**Sensors show "Unavailable"**  
The integration could not reach `motorist.co.th`. Check your internet connection and HA logs (`Settings → System → Logs`).

**A specific station sensor is always unavailable**  
That station does not carry that fuel grade (shown as "–" on the website). This is expected.

**Prices seem outdated**  
Reduce the update interval in the integration options. Fuel prices in Thailand typically change once per week (usually Thursday evening).

**Downloading diagnostics**  
Go to **Settings → Devices & Services → Thailand Petrol Prices → three-dot menu → Download diagnostics** and attach the file to any bug report.

---

## Development

```bash
# Clone and set up
git clone https://github.com/simplemice/ha_petrol_prices.git
cd ha_petrol_prices

# Copy into a dev HA instance
cp -r custom_components/thailand_petrol_prices \
      /path/to/homeassistant/config/custom_components/
```

Releases are created automatically when the `version` field in `manifest.json` is bumped and pushed to `main`.

---

## License

This project is licensed under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for details.

Data source: [Motorist Thailand](https://www.motorist.co.th/en/petrol-prices) — prices reflect Bangkok and surrounding provinces.

[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs-link]: https://hacs.xyz
[release-shield]: https://img.shields.io/github/v/release/simplemice/ha_petrol_prices
[release-link]: https://github.com/simplemice/ha_petrol_prices/releases
[license-shield]: https://img.shields.io/github/license/simplemice/ha_petrol_prices
