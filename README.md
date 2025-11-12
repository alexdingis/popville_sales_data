# Popville Sales Data
## DC Real Estate Geocoded Dataset

**Last Updated:** November 2025

## About

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vel luctus tortor. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Fusce tristique lorem non justo eleifend faucibus. Phasellus porttitor metus ut turpis suscipit, vitae aliquam odio pretium.

This dataset contains **110,976** residential property sale records across Washington, DC, geocoded to 2020 Census tracts and enriched with inflation-adjusted sale prices, mortgage rate context, and basic property characteristics. Data have been standardized, time-aligned, and spatially validated to support small-area housing market analysis and longitudinal studies.

---

## Data Dictionary

| Field                       | Type      | Description                                                                                                                                                                                         |
| --------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **INPUT_ADDRESS**           | `object`  | Raw address text as provided from the source, may include apartment/unit info (e.g., “2250 11TH ST NW #103, Washington, DC, 20001”).                                                                |
| **MATCHED_ADDRESS**         | `object`  | Address returned by the Census Geocoder after standardization.                                                                                                                                      |
| **MATCH_STATUS**            | `object`  | Indicates whether the address was successfully geocoded (`Match`, `No_Match`, `Tie`, etc.).                                                                                                         |
| **MATCH_TYPE**              | `object`  | Type of geocoding match (e.g., `Exact`, `Non_Exact`).                                                                                                                                               |
| **ZIP**                     | `object`  | Five-digit ZIP code for the property.                                                                                                                                                               |
| **COORDINATES**             | `object`  | Latitude and longitude pair returned by the geocoder, formatted as “lon,lat”.                                                                                                                       |
| **FULL_TRACT**              | `object`  | 11-digit Census Tract GEOID (state + county + tract).                                                                                                                                               |
| **POST_YEAR**               | `object`  | Year when the sale was posted to Popville. Records were typically posted in the month after the month of sales (e.g., September was reported in October).                                           |
| **POST_MONTH**              | `object`  | Month when the sale was posted to Popville.                                                                                                                                                         |
| **SELL_YEAR**               | `int64`   | Year corresponding to the sale or estimated sale date, one month prior to posting.                                                                                                                  |
| **SELL_MONTH**              | `object`  | Month corresponding to the sale or estimated sale date.                                                                                                                                             |
| **CLOSE_DATE**              | `object`  | Exact recorded closing date when available (YYYY-MM-DD). Some records are missing this date.                                                                                                        |
| **LIST_PRICE**              | `float64` | Listing price in nominal dollars.                                                                                                                                                                   |
| **CLOSE_PRICE**             | `float64` | Closing price in nominal dollars.                                                                                                                                                                   |
| **SUBSIDY**                 | `object`  | Any recorded seller or government subsidy applied at closing.                                                                                                                                       |
| **BEDROOMS**                | `object`  | Number of bedrooms.                                                                                                                                                                                 |
| **FULL_BATH**               | `object`  | Number of full bathrooms.                                                                                                                                                                           |
| **HALF_BATH**               | `object`  | Number of half bathrooms.                                                                                                                                                                           |
| **CPI_SELL**                | `float64` | Consumer Price Index (CPI-U) value for the sale month, from Bureau of Labor Statistics (BLS).                                                                                                       |
| **INFLATION_FACTOR**        | `float64` | Ratio used to convert nominal prices to **September 2025 dollars**.                                                                                                                                 |
| **CLOSE_PRICE_ADJ_2025_09** | `float64` | Inflation-adjusted closing price expressed in September 2025 dollars.                                                                                                                               |
| **AVG_RATE**                | `float64` | Freddie Mac 30-year fixed mortgage rate associated with the sale around the **closing** date (weekly or monthly average). When available, the closing date was used otherwise it's the average of the closing month.                                                                          |
| **APT**                     | `bool`    | Boolean flag indicating whether the address likely corresponds to an apartment or multi-unit dwelling, based on regex text pattern detection (e.g., presence of `#`, `Unit`, `Apt`, `Suite`, etc.). |

---

## Usage

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi dapibus cursus odio non dignissim. This dataset can be joined with spatial shapefiles, analyzed for housing price trends, or used to model the effects of inflation and mortgage rates over time.

Analysts can integrate it with tract-level demographic or housing data from the U.S. Census Bureau, enabling research into affordability, neighborhood change, or policy impacts.

---

## License

This dataset is provided **“as is”** with **no warranties or guarantees** of completeness or accuracy. You are free to use, share, and adapt the data for research or non-commercial purposes, provided attribution is given. See the [MIT License](https://opensource.org/licenses/MIT) for permissive reuse terms.
