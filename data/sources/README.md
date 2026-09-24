# Data Source Registry

Every production dataset should be registered here.

---

## 1. CGWB Ground Water Quality Data - 2024

- **Dataset name:** Ground Water Quality Data - 2024
- **Provider:** Central Ground Water Board (CGWB), Government of India
- **URL:** https://cgwb.gov.in/en/ground-water-quality
- **Date accessed:** 2026-09-24
- **Geographic coverage:** India
- **Update frequency:** Annual groundwater-quality monitoring/reporting
- **License / usage terms:** Refer to CGWB's published dataset/source terms
- **Fields used:**
  - Latitude
  - Longitude
  - Sampling/observation location
  - State
  - District
  - Groundwater quality parameters
  - Sampling period/year
  - Relevant chemical/physical parameters
- **Limitations:**
  - Observations represent monitoring locations rather than continuous measurements at every coordinate.
  - A requested site may not have an observation at the exact coordinates.
  - Spatial matching therefore uses nearby observations.
  - Temporal coverage depends on the available sampling period.
- **Primary use in India AI Grid:**
  - Groundwater quality assessment
  - Water availability/site screening
  - Water-risk analysis

---

## 2. Nominatim / OpenStreetMap Geocoding

- **Dataset/API name:** Nominatim Geocoding API
- **Provider:** OpenStreetMap Foundation / Nominatim
- **URL:** https://nominatim.openstreetmap.org/
- **Date accessed:** 2026-09-24
- **Geographic coverage:** Global
- **Update frequency:** Continuously updated OpenStreetMap-derived data
- **License / usage terms:** Follow Nominatim usage policy and OpenStreetMap attribution/licensing requirements
- **Fields used:**
  - Latitude
  - Longitude
  - City
  - District
  - State
  - Country
  - Postal code
  - Display name
- **Limitations:**
  - Geocoding results depend on OpenStreetMap coverage.
  - Public Nominatim service has usage/rate limitations.
  - Results should be cached where appropriate.
- **Primary use in India AI Grid:**
  - Convert user-entered locations into coordinates
  - Reverse geocoding
  - Provide the canonical location object for downstream infrastructure models