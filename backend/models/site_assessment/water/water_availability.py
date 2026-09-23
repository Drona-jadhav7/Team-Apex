"""
India AI Grid
Water Availability & Quality Intelligence Model

Input:
    latitude
    longitude

Purpose:
    Collect water-related information for a specific Indian location
    from official Indian government / ISRO data sources.

Primary sources:
    - Central Ground Water Board (CGWB)
    - India-WRIS / NWIC
    - ISRO Bhuvan

Important:
    Indian official water data is distributed across APIs, OGC services,
    downloadable datasets and portals. This module therefore uses an
    adapter architecture rather than assuming one universal REST API.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional
import math
import requests


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_TIMEOUT = 20

# Official Indian sources
CGWB_URL = "https://cgwb.gov.in/"
INDIA_WRIS_URL = "https://indiawris.gov.in/"
BHUVAN_WMS_URL = "https://bhuvan-vec2.nrsc.gov.in/bhuvan/wms"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class Location:
    latitude: float
    longitude: float


@dataclass
class GroundwaterQuality:
    """
    Groundwater chemistry.

    All values are optional because official monitoring stations
    are not necessarily located exactly at the requested coordinate.
    """

    ph: Optional[float] = None

    electrical_conductivity_us_cm: Optional[float] = None
    tds_mg_l: Optional[float] = None

    total_hardness_mg_l: Optional[float] = None
    calcium_hardness_mg_l: Optional[float] = None
    alkalinity_mg_l: Optional[float] = None

    chloride_mg_l: Optional[float] = None
    sulfate_mg_l: Optional[float] = None
    silica_mg_l: Optional[float] = None

    iron_mg_l: Optional[float] = None
    manganese_mg_l: Optional[float] = None

    nitrate_mg_l: Optional[float] = None
    fluoride_mg_l: Optional[float] = None
    arsenic_mg_l: Optional[float] = None

    turbidity_ntu: Optional[float] = None
    tss_mg_l: Optional[float] = None

    temperature_c: Optional[float] = None


@dataclass
class WaterQuantity:
    """
    Water availability information.

    Units are intentionally explicit.
    """

    annual_groundwater_recharge_mcm: Optional[float] = None
    extractable_groundwater_resource_mcm: Optional[float] = None
    groundwater_extraction_mcm: Optional[float] = None

    groundwater_level_m: Optional[float] = None

    nearby_surface_water: Optional[bool] = None
    nearby_river: Optional[bool] = None
    nearby_reservoir: Optional[bool] = None
    nearby_waterbody: Optional[bool] = None


@dataclass
class WaterReliability:
    """
    Long-term reliability indicators.
    """

    seasonal_variability: Optional[str] = None
    drought_risk: Optional[str] = None
    flood_risk: Optional[str] = None

    data_year: Optional[int] = None


@dataclass
class DataSource:
    name: str
    organization: str
    official: bool
    url: str
    status: str
    notes: Optional[str] = None


@dataclass
class WaterAssessment:
    """
    Final normalized result returned by the model.
    """

    location: Dict[str, Any]

    groundwater_quality: Dict[str, Any]
    water_quantity: Dict[str, Any]
    reliability: Dict[str, Any]

    cooling_parameters: Dict[str, Any]

    treatment_required: Dict[str, Any]

    data_sources: List[Dict[str, Any]]

    data_quality: Dict[str, Any]

    water_score: Optional[float] = None


# ============================================================
# VALIDATION
# ============================================================

def validate_coordinates(latitude: float, longitude: float) -> None:
    """
    Validate latitude/longitude and ensure the point is broadly
    within India's geographic bounds.

    This is a geographic sanity check, not a political boundary
    determination.
    """

    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90.")

    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180.")

    # Broad bounding box covering India and surrounding territories.
    # We intentionally do not use this as an exact administrative
    # boundary check.
    if not 6 <= latitude <= 38:
        raise ValueError("Latitude is outside the supported India region.")

    if not 68 <= longitude <= 98:
        raise ValueError("Longitude is outside the supported India region.")


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance between two geographic coordinates.
    """

    radius = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    return 2 * radius * math.asin(math.sqrt(a))


def safe_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = DEFAULT_TIMEOUT
) -> Optional[requests.Response]:
    """
    Perform an HTTP GET without allowing one failed external
    source to crash the entire model.
    """

    try:
        response = requests.get(
            url,
            params=params,
            timeout=timeout
        )

        response.raise_for_status()

        return response

    except requests.RequestException:
        return None


# ============================================================
# SOURCE ADAPTERS
# ============================================================

class CGWBAdapter:
    """
    Adapter for Central Ground Water Board data.

    CGWB provides groundwater quality monitoring and groundwater
    resource assessments. Much of the current public data is
    distributed through datasets/reports and India-WRIS rather
    than one universal coordinate REST endpoint.

    Therefore this adapter currently acts as the integration
    boundary. Dataset-specific parsers can be plugged in here.
    """

    SOURCE = DataSource(
        name="Central Ground Water Board",
        organization="Ministry of Jal Shakti, Government of India",
        official=True,
        url=CGWB_URL,
        status="available",
        notes=(
            "Groundwater quality and groundwater resource datasets "
            "are available through CGWB publications and India-WRIS."
        )
    )

    def __init__(self):
        self.data = {}

    def get_groundwater_data(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:

        # Placeholder for the official CGWB dataset adapter.
        #
        # IMPORTANT:
        # Do not invent coordinate-level values when a monitoring
        # station is unavailable.
        #
        # Once the CGWB/India-WRIS machine-readable dataset is
        # downloaded, this function will:
        #
        # 1. load monitoring stations
        # 2. calculate distance from requested coordinate
        # 3. select nearest valid observations
        # 4. attach observation year
        # 5. return measured values

        return {
            "status": "dataset_adapter_required",
            "latitude": latitude,
            "longitude": longitude,
            "data": {}
        }


class IndiaWRISAdapter:
    """
    Adapter boundary for India-WRIS / NWIC.

    India-WRIS is the main integrated Indian water-resource
    information platform.
    """

    SOURCE = DataSource(
        name="India-WRIS",
        organization="National Water Informatics Centre",
        official=True,
        url=INDIA_WRIS_URL,
        status="available",
        notes=(
            "Integrated water-resources information platform. "
            "Specific machine-readable services should be configured "
            "through the appropriate India-WRIS dataset/service."
        )
    )

    def get_water_data(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:

        return {
            "status": "dataset_adapter_required",
            "latitude": latitude,
            "longitude": longitude,
            "data": {}
        }


class BhuvanAdapter:
    """
    ISRO Bhuvan geospatial adapter.

    Bhuvan exposes OGC geospatial services including WMS/WMTS.
    Water-body and other thematic layers can therefore be queried
    or spatially processed around a location.
    """

    SOURCE = DataSource(
        name="ISRO Bhuvan",
        organization="National Remote Sensing Centre / ISRO",
        official=True,
        url="https://bhuvan.nrsc.gov.in/",
        status="available",
        notes=(
            "Bhuvan provides OGC geospatial services and water-body "
            "information products."
        )
    )

    def get_location_data(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:

        # We don't fabricate water-body presence.
        #
        # A production implementation will query the appropriate
        # Bhuvan layer using GetFeatureInfo / WFS / downloadable
        # geospatial data depending on the selected layer.

        return {
            "status": "gis_layer_adapter_required",
            "latitude": latitude,
            "longitude": longitude,
            "data": {}
        }


# ============================================================
# COOLING REQUIREMENTS
# ============================================================

def cooling_requirements() -> Dict[str, Dict[str, Any]]:
    """
    Engineering requirement templates.

    IMPORTANT:
    These are not universal legal limits.
    Actual limits must be checked against the cooling-equipment
    manufacturer's specifications and system design.
    """

    return {

        "cooling_tower": {
            "parameters": [
                "ph",
                "conductivity",
                "tds",
                "hardness",
                "alkalinity",
                "chloride",
                "sulfate",
                "silica",
                "turbidity",
                "tss",
                "microbiological_control"
            ]
        },

        "chilled_water": {
            "parameters": [
                "ph",
                "conductivity",
                "tds",
                "hardness",
                "chloride",
                "sulfate",
                "silica",
                "iron",
                "copper",
                "turbidity",
                "microbiological_control"
            ]
        },

        "direct_to_chip": {
            "parameters": [
                "ph",
                "conductivity",
                "tds",
                "hardness",
                "chloride",
                "sulfate",
                "silica",
                "iron",
                "manganese",
                "turbidity",
                "tss",
                "microbiological_control"
            ]
        },

        "immersion": {
            "parameters": [
                "ph",
                "conductivity",
                "tds",
                "hardness",
                "chloride",
                "sulfate",
                "silica",
                "iron",
                "turbidity",
                "microbiological_control"
            ]
        }
    }


# ============================================================
# WATER QUALITY ANALYSIS
# ============================================================

def determine_missing_parameters(
    quality: Dict[str, Any],
    cooling_system: str
) -> List[str]:

    requirements = cooling_requirements()

    required = requirements.get(
        cooling_system,
        requirements["direct_to_chip"]
    )["parameters"]

    missing = []

    for parameter in required:

        value = quality.get(parameter)

        if value is None:
            missing.append(parameter)

    return missing


def estimate_treatment_need(
    quality: Dict[str, Any],
    cooling_system: str
) -> Dict[str, Any]:
    """
    Preliminary treatment classification.

    This deliberately does NOT invent engineering thresholds.
    The final implementation will compare actual measurements
    against equipment-specific limits.
    """

    if not quality:
        return {
            "status": "unknown",
            "required_processes": [],
            "reason": "No measured water-quality data available."
        }

    required_processes = []

    if quality.get("turbidity_ntu") is not None:
        if quality["turbidity_ntu"] > 5:
            required_processes.append("filtration")

    if quality.get("total_hardness_mg_l") is not None:
        if quality["total_hardness_mg_l"] > 200:
            required_processes.append("softening_or_membrane_treatment")

    if quality.get("tds_mg_l") is not None:
        if quality["tds_mg_l"] > 1000:
            required_processes.append("advanced_dissolved_solids_treatment")

    if quality.get("iron_mg_l") is not None:
        if quality["iron_mg_l"] > 1:
            required_processes.append("iron_removal")

    if quality.get("manganese_mg_l") is not None:
        if quality["manganese_mg_l"] > 0.3:
            required_processes.append("manganese_removal")

    if quality.get("chloride_mg_l") is not None:
        if quality["chloride_mg_l"] > 200:
            required_processes.append("corrosion_control_or_membrane")

    if quality.get("silica_mg_l") is not None:
        if quality["silica_mg_l"] > 50:
            required_processes.append("silica_control")

    if quality.get("ph") is not None:
        if quality["ph"] < 6.5 or quality["ph"] > 9:
            required_processes.append("ph_adjustment")

    if required_processes:
        status = "treatment_likely_required"
    else:
        status = "preliminary_acceptable"

    return {
        "status": status,
        "required_processes": sorted(set(required_processes))
    }


# ============================================================
# DATA QUALITY
# ============================================================

def assess_data_quality(
    sources: List[DataSource],
    quality: Dict[str, Any]
) -> Dict[str, Any]:

    measured = sum(
        value is not None
        for value in quality.values()
    )

    total = len(quality)

    completeness = (
        measured / total
        if total > 0
        else 0
    )

    return {
        "completeness": round(completeness, 3),
        "measured_parameters": measured,
        "total_parameters": total,
        "official_sources_available": sum(
            source.official
            for source in sources
        ),
        "warning": (
            "A missing value means data was not available; "
            "it must not be interpreted as zero."
        )
    }


# ============================================================
# MAIN ENGINE
# ============================================================

class WaterAvailabilityModel:

    def __init__(
        self,
        latitude: float,
        longitude: float,
        cooling_system: str = "direct_to_chip"
    ):

        validate_coordinates(
            latitude,
            longitude
        )

        self.location = Location(
            latitude=latitude,
            longitude=longitude
        )

        self.cooling_system = cooling_system

        self.cgwb = CGWBAdapter()
        self.india_wris = IndiaWRISAdapter()
        self.bhuvan = BhuvanAdapter()

    def run(self) -> WaterAssessment:

        # ----------------------------------------------------
        # 1. Collect source information
        # ----------------------------------------------------

        cgwb_result = self.cgwb.get_groundwater_data(
            self.location.latitude,
            self.location.longitude
        )

        wris_result = self.india_wris.get_water_data(
            self.location.latitude,
            self.location.longitude
        )

        bhuvan_result = self.bhuvan.get_location_data(
            self.location.latitude,
            self.location.longitude
        )

        # ----------------------------------------------------
        # 2. Normalize groundwater quality
        # ----------------------------------------------------

        groundwater_quality = (
            cgwb_result.get("data", {})
            if cgwb_result
            else {}
        )

        # ----------------------------------------------------
        # 3. Normalize quantity
        # ----------------------------------------------------

        water_quantity = (
            wris_result.get("data", {})
            if wris_result
            else {}
        )

        # ----------------------------------------------------
        # 4. Add GIS information
        # ----------------------------------------------------

        if bhuvan_result:
            water_quantity.update(
                bhuvan_result.get("data", {})
            )

        # ----------------------------------------------------
        # 5. Determine required parameters
        # ----------------------------------------------------

        missing = determine_missing_parameters(
            groundwater_quality,
            self.cooling_system
        )

        # ----------------------------------------------------
        # 6. Treatment analysis
        # ----------------------------------------------------

        treatment = estimate_treatment_need(
            groundwater_quality,
            self.cooling_system
        )

        # ----------------------------------------------------
        # 7. Data quality
        # ----------------------------------------------------

        sources = [
            self.cgwb.SOURCE,
            self.india_wris.SOURCE,
            self.bhuvan.SOURCE
        ]

        quality_report = assess_data_quality(
            sources,
            groundwater_quality
        )

        quality_report["missing_for_cooling"] = missing

        # ----------------------------------------------------
        # 8. Return final normalized result
        # ----------------------------------------------------

        return WaterAssessment(

            location=asdict(self.location),

            groundwater_quality=groundwater_quality,

            water_quantity=water_quantity,

            reliability={
                "status": "pending_dataset_integration"
            },

            cooling_parameters={
                "cooling_system": self.cooling_system,
                "required_parameters": (
                    cooling_requirements()
                    .get(
                        self.cooling_system,
                        {}
                    )
                    .get("parameters", [])
                )
            },

            treatment_required=treatment,

            data_sources=[
                asdict(source)
                for source in sources
            ],

            data_quality=quality_report,

            water_score=None
        )


# ============================================================
# SIMPLE API FUNCTION
# ============================================================

def analyze_location(
    latitude: float,
    longitude: float,
    cooling_system: str = "direct_to_chip"
) -> Dict[str, Any]:

    model = WaterAvailabilityModel(
        latitude=latitude,
        longitude=longitude,
        cooling_system=cooling_system
    )

    result = model.run()

    return asdict(result)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    # Example coordinate.
    # Replace this with any Indian latitude/longitude.

    result = analyze_location(
        latitude=20.0059,
        longitude=73.7797,
        cooling_system="direct_to_chip"
    )

    import json

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )