# Changelog

## [1.0.2] - 2026-06-28

## What's Changed
- add brand icon (e509e40)


## [1.0.1] - 2026-06-28

## What's Changed
- update workflow (dbf0f46)
- add brand logo (970a592)
- update workflow (ba719ae)
- update README.md (95e65d1)
- add screenshots, brand and change README.md (aa7586b)


## [1.0.0] - 2026-06-28

### Added
- Initial release of the Thailand Petrol Prices integration
- Scrapes live fuel prices from [motorist.co.th](https://www.motorist.co.th/en/petrol-prices)
- Supports 8 fuel grades: Gasohol 91, Gasohol 95, Gasohol E20, Gasohol E85, Gasohol 95 Premium, Benzin 95, Diesel B7, Diesel B7 Premium
- Supports 8 stations: PTT, BCP, Shell, Caltex, IRPC, PT, Susco, Pure
- 64 individual station price sensors (THB/L)
- 8 lowest-price sensors per fuel grade with `cheapest_station` and `all_prices` attributes
- Config flow UI setup (no YAML required)
- Configurable update interval (default 1 hour, minimum 5 minutes)
- Options flow to change update interval without re-adding the integration
- Diagnostics support for troubleshooting
- HACS compatibility
- GitHub Actions workflow for automatic versioned releases
