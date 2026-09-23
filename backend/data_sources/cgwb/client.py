"""
India AI Grid
CGWB Groundwater Data Client

Path:
    backend/data_sources/cgwb/client.py

Architecture:

    CGWB official dataset
            |
            v
      CGWBClient
            |
            v
    normalize observations
            |
            v
      spatial search
            |
            v
      nearest stations
            |
            v
      Water Assessment Model

The client does NOT calculate data-center suitability.
It only retrieves, normalizes and spatially selects official
groundwater observations.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv
import json
import math


# ============================================================
# SOURCE INFORMATION
# ============================================================

CGWB_NAME = "Central Ground Water Board"

CGWB_URL = "https://cgwb.gov.in/"

INDIA_WRIS_URL = "https://indiawris.gov.in/"


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MAX_DISTANCE_KM = 100.0
DEFAULT_RESULT_LIMIT = 5


# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class GroundwaterObservation:

    station_id: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    state: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None

    observation_date: Optional[str] = None

    water_level_m: Optional[float] = None

    ph: Optional[float] = None

    electrical_conductivity_us_cm: Optional[float] = None

    tds_mg_l: Optional[float] = None

    total_hardness_mg_l: Optional[float] = None

    calcium_mg_l: Optional[float] = None
    magnesium_mg_l: Optional[float] = None

    alkalinity_mg_l: Optional[float] = None

    chloride_mg_l: Optional[float] = None

    sulfate_mg_l: Optional[float] = None

    silica_mg_l: Optional[float] = None

    iron_mg_l: Optional[float] = None

    manganese_mg_l: Optional[float] = None

    nitrate_mg_l: Optional[float] = None

    fluoride_mg_l: Optional[float] = None

    arsenic_mg_l: Optional[float] = None

    uranium_mg_l: Optional[float] = None

    turbidity_ntu: Optional[float] = None

    temperature_c: Optional[float] = None

    source: str = CGWB_NAME

    source_url: str = CGWB_URL


@dataclass
class NearbyObservation:

    observation: GroundwaterObservation

    distance_km: float

    spatial_confidence: str


@dataclass
class CGWBResult:

    success: bool

    requested_latitude: float
    requested_longitude: float

    observations: List[NearbyObservation]

    latest_observation: Optional[NearbyObservation]

    source: str
    source_url: str

    retrieved_at: str

    warnings: List[str]


# ============================================================
# EXCEPTIONS
# ============================================================

class CGWBError(Exception):
    pass


class CGWBDataError(CGWBError):
    pass


# ============================================================
# GEO FUNCTIONS
# ============================================================

def validate_coordinates(
    latitude: float,
    longitude: float
) -> None:

    if not -90 <= latitude <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180."
        )


def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:

    earth_radius_km = 6371.0088

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        +
        math.cos(phi1)
        * math.cos(phi2)
        * math.sin(dlambda / 2) ** 2
    )

    return (
        2
        * earth_radius_km
        * math.asin(math.sqrt(a))
    )


# ============================================================
# VALUE NORMALIZATION
# ============================================================

def to_float(
    value: Any
) -> Optional[float]:

    if value is None:
        return None

    if isinstance(value, float):
        return value

    if isinstance(value, int):
        return float(value)

    value = str(value).strip()

    if not value:
        return None

    # Handle common missing-value representations
    if value.lower() in {
        "na",
        "n/a",
        "null",
        "none",
        "-",
        "--",
        "nan"
    }:
        return None

    value = value.replace(",", "")

    try:
        return float(value)

    except ValueError:
        return None


def first_value(
    record: Dict[str, Any],
    *names: str
) -> Any:

    normalized = {
        str(k).strip().lower(): v
        for k, v in record.items()
    }

    for name in names:

        value = normalized.get(
            name.lower()
        )

        if value is not None:
            return value

    return None


# ============================================================
# CGWB CLIENT
# ============================================================

class CGWBClient:

    def __init__(
        self,
        dataset_path: Optional[str] = None
    ):

        self.dataset_path = (
            Path(dataset_path)
            if dataset_path
            else None
        )

    # --------------------------------------------------------
    # SOURCE
    # --------------------------------------------------------

    def source_information(self):

        return {
            "name": CGWB_NAME,
            "organization": (
                "Central Ground Water Board"
            ),
            "ministry": (
                "Ministry of Jal Shakti, "
                "Government of India"
            ),
            "official": True,
            "source_url": CGWB_URL,
            "india_wris_url": INDIA_WRIS_URL
        }

    # --------------------------------------------------------
    # DATASET LOADING
    # --------------------------------------------------------

    def load_dataset(
        self
    ) -> List[GroundwaterObservation]:

        if self.dataset_path is None:

            raise CGWBDataError(
                "No CGWB dataset configured."
            )

        if not self.dataset_path.exists():

            raise CGWBDataError(
                f"CGWB dataset not found: "
                f"{self.dataset_path}"
            )

        suffix = (
            self.dataset_path
            .suffix
            .lower()
        )

        if suffix == ".csv":

            return self._load_csv()

        if suffix == ".json":

            return self._load_json()

        raise CGWBDataError(
            "Unsupported dataset format. "
            "Currently supported: CSV and JSON."
        )

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    def _load_csv(
        self
    ) -> List[GroundwaterObservation]:

        observations = []

        with open(
            self.dataset_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                observation = (
                    self.normalize_record(
                        row
                    )
                )

                if (
                    observation.latitude is not None
                    and
                    observation.longitude is not None
                ):

                    observations.append(
                        observation
                    )

        return observations

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    def _load_json(
        self
    ) -> List[GroundwaterObservation]:

        with open(
            self.dataset_path,
            "r",
            encoding="utf-8"
        ) as file:

            payload = json.load(file)

        if isinstance(payload, dict):

            records = (
                payload.get("data")
                or payload.get("records")
                or payload.get("results")
                or []
            )

        elif isinstance(payload, list):

            records = payload

        else:

            raise CGWBDataError(
                "Invalid JSON dataset structure."
            )

        observations = []

        for record in records:

            observation = (
                self.normalize_record(
                    record
                )
            )

            if (
                observation.latitude is not None
                and
                observation.longitude is not None
            ):

                observations.append(
                    observation
                )

        return observations

    # ========================================================
    # NORMALIZATION
    # ========================================================

    def normalize_record(
        self,
        record: Dict[str, Any]
    ) -> GroundwaterObservation:

        return GroundwaterObservation(

            station_id=first_value(
                record,
                "station_id",
                "station id",
                "station",
                "station_code",
                "well_id",
                "well code"
            ),

            latitude=to_float(
                first_value(
                    record,
                    "latitude",
                    "lat"
                )
            ),

            longitude=to_float(
                first_value(
                    record,
                    "longitude",
                    "lon",
                    "lng"
                )
            ),

            state=first_value(
                record,
                "state",
                "state_name"
            ),

            district=first_value(
                record,
                "district",
                "district_name"
            ),

            block=first_value(
                record,
                "block",
                "block_name"
            ),

            observation_date=first_value(
                record,
                "observation_date",
                "sample_date",
                "date"
            ),

            water_level_m=to_float(
                first_value(
                    record,
                    "water_level_m",
                    "water level",
                    "depth_to_water"
                )
            ),

            ph=to_float(
                first_value(
                    record,
                    "ph",
                    "pH"
                )
            ),

            electrical_conductivity_us_cm=to_float(
                first_value(
                    record,
                    "electrical_conductivity_us_cm",
                    "electrical conductivity",
                    "ec",
                    "EC"
                )
            ),

            tds_mg_l=to_float(
                first_value(
                    record,
                    "tds_mg_l",
                    "total dissolved solids",
                    "tds",
                    "TDS"
                )
            ),

            total_hardness_mg_l=to_float(
                first_value(
                    record,
                    "total_hardness_mg_l",
                    "total hardness",
                    "hardness"
                )
            ),

            calcium_mg_l=to_float(
                first_value(
                    record,
                    "calcium_mg_l",
                    "calcium",
                    "ca"
                )
            ),

            magnesium_mg_l=to_float(
                first_value(
                    record,
                    "magnesium_mg_l",
                    "magnesium",
                    "mg"
                )
            ),

            alkalinity_mg_l=to_float(
                first_value(
                    record,
                    "alkalinity_mg_l",
                    "alkalinity"
                )
            ),

            chloride_mg_l=to_float(
                first_value(
                    record,
                    "chloride_mg_l",
                    "chloride",
                    "cl"
                )
            ),

            sulfate_mg_l=to_float(
                first_value(
                    record,
                    "sulfate_mg_l",
                    "sulphate",
                    "sulfate"
                )
            ),

            silica_mg_l=to_float(
                first_value(
                    record,
                    "silica_mg_l",
                    "silica"
                )
            ),

            iron_mg_l=to_float(
                first_value(
                    record,
                    "iron_mg_l",
                    "iron",
                    "fe"
                )
            ),

            manganese_mg_l=to_float(
                first_value(
                    record,
                    "manganese_mg_l",
                    "manganese",
                    "mn"
                )
            ),

            nitrate_mg_l=to_float(
                first_value(
                    record,
                    "nitrate_mg_l",
                    "nitrate",
                    "no3"
                )
            ),

            fluoride_mg_l=to_float(
                first_value(
                    record,
                    "fluoride_mg_l",
                    "fluoride",
                    "f"
                )
            ),

            arsenic_mg_l=to_float(
                first_value(
                    record,
                    "arsenic_mg_l",
                    "arsenic",
                    "as"
                )
            ),

            uranium_mg_l=to_float(
                first_value(
                    record,
                    "uranium_mg_l",
                    "uranium",
                    "u"
                )
            ),

            turbidity_ntu=to_float(
                first_value(
                    record,
                    "turbidity_ntu",
                    "turbidity"
                )
            ),

            temperature_c=to_float(
                first_value(
                    record,
                    "temperature_c",
                    "temperature"
                )
            )
        )

    # ========================================================
    # SPATIAL SEARCH
    # ========================================================

    def find_nearest(
        self,
        latitude: float,
        longitude: float,
        observations: List[GroundwaterObservation],
        max_distance_km: float = DEFAULT_MAX_DISTANCE_KM,
        limit: int = DEFAULT_RESULT_LIMIT
    ) -> List[NearbyObservation]:

        validate_coordinates(
            latitude,
            longitude
        )

        results = []

        for observation in observations:

            if (
                observation.latitude is None
                or
                observation.longitude is None
            ):
                continue

            distance = haversine_distance_km(
                latitude,
                longitude,
                observation.latitude,
                observation.longitude
            )

            if distance > max_distance_km:
                continue

            results.append(
                NearbyObservation(
                    observation=observation,
                    distance_km=round(
                        distance,
                        3
                    ),
                    spatial_confidence=(
                        self.spatial_confidence(
                            distance
                        )
                    )
                )
            )

        results.sort(
            key=lambda item:
            item.distance_km
        )

        return results[:limit]

    # ========================================================
    # CONFIDENCE
    # ========================================================

    @staticmethod
    def spatial_confidence(
        distance_km: float
    ) -> str:

        if distance_km <= 5:
            return "very_high"

        if distance_km <= 15:
            return "high"

        if distance_km <= 30:
            return "medium"

        if distance_km <= 60:
            return "low"

        return "very_low"

    # ========================================================
    # LATEST
    # ========================================================

    @staticmethod
    def latest(
        observations: List[NearbyObservation]
    ) -> Optional[NearbyObservation]:

        if not observations:
            return None

        valid_dates = []

        for item in observations:

            date_string = (
                item.observation.observation_date
            )

            if not date_string:
                continue

            try:

                parsed = (
                    datetime.fromisoformat(
                        date_string
                    )
                )

                valid_dates.append(
                    (parsed, item)
                )

            except ValueError:

                continue

        if not valid_dates:

            return observations[0]

        valid_dates.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return valid_dates[0][1]

    # ========================================================
    # MAIN
    # ========================================================

    def analyze(
        self,
        latitude: float,
        longitude: float,
        max_distance_km: float = DEFAULT_MAX_DISTANCE_KM,
        limit: int = DEFAULT_RESULT_LIMIT
    ) -> CGWBResult:

        validate_coordinates(
            latitude,
            longitude
        )

        observations = (
            self.load_dataset()
        )

        nearby = self.find_nearest(
            latitude=latitude,
            longitude=longitude,
            observations=observations,
            max_distance_km=max_distance_km,
            limit=limit
        )

        latest = self.latest(
            nearby
        )

        warnings = []

        if not nearby:

            warnings.append(
                "No CGWB monitoring observation "
                "was found within the configured "
                "search radius."
            )

        if nearby:

            if nearby[0].distance_km > 30:

                warnings.append(
                    "Nearest observation is more than "
                    "30 km away. Treat coordinate-level "
                    "inference with caution."
                )

        return CGWBResult(

            success=True,

            requested_latitude=latitude,

            requested_longitude=longitude,

            observations=nearby,

            latest_observation=latest,

            source=CGWB_NAME,

            source_url=CGWB_URL,

            retrieved_at=(
                datetime.utcnow().isoformat()
            ),

            warnings=warnings
        )


# ============================================================
# PUBLIC API
# ============================================================

def get_groundwater_data(
    latitude: float,
    longitude: float,
    dataset_path: str,
    max_distance_km: float = 100,
    limit: int = 5
) -> Dict[str, Any]:

    client = CGWBClient(
        dataset_path=dataset_path
    )

    result = client.analyze(
        latitude=latitude,
        longitude=longitude,
        max_distance_km=max_distance_km,
        limit=limit
    )

    return asdict(result)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = get_groundwater_data(
        latitude=20.0059,
        longitude=73.7797,

        # Put the downloaded official CGWB dataset here.
        dataset_path=(
            "data/cgwb/"
            "groundwater_quality_2024.csv"
        ),

        max_distance_km=100,

        limit=5
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )