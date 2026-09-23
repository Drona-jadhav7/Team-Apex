"""
India AI Grid
Groundwater Assessment Model

Path:
    backend/models/site_assessment/water/groundwater.py

Purpose:
    Evaluate groundwater conditions around a proposed
    data-center location using normalized observations
    from CGWB / India-WRIS.

This model evaluates:

    - groundwater level
    - distance from monitoring station
    - observation recency
    - temporal coverage
    - groundwater accessibility indicators
    - spatial confidence
    - groundwater data completeness

This model does NOT:

    - determine legal groundwater extraction permissions
    - estimate an exact sustainable extraction rate
    - replace hydrogeological investigation
    - calculate the final data-center site score
    - assume groundwater can legally be used by the data center

Important:
    Groundwater level is NOT the same thing as groundwater
    availability.

A deeper water level can indicate greater pumping depth,
but does not by itself prove that sufficient sustainable
yield exists.

A proper feasibility study eventually needs aquifer,
recharge, abstraction, seasonal and regulatory information.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Any, Dict, List, Optional


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class GroundwaterLevelAssessment:
    """
    Assessment of a groundwater-level observation.
    """

    available: bool

    water_level_m: Optional[float]

    interpretation: str

    concern_level: str

    notes: str


@dataclass
class ObservationRecency:
    """
    Determines how recent the groundwater observation is.
    """

    available: bool

    observation_date: Optional[str]

    age_days: Optional[int]

    recency_category: str

    confidence: str


@dataclass
class GroundwaterAssessment:
    """
    Complete groundwater assessment.
    """

    available: bool

    station_id: Optional[str]

    state: Optional[str]

    district: Optional[str]

    distance_km: Optional[float]

    spatial_confidence: Optional[str]

    water_level: GroundwaterLevelAssessment

    recency: ObservationRecency

    temporal_coverage: str

    data_completeness: str

    extraction_sustainability: str

    regulatory_status: str

    concerns: List[str]

    warnings: List[str]

    summary: str


# ============================================================
# CONFIGURATION
# ============================================================

class GroundwaterThresholds:
    """
    Screening configuration.

    These are NOT universal hydrogeological limits.

    They are used to classify the quality of the available
    information and the relative depth of groundwater.

    Actual groundwater feasibility must use local aquifer
    characteristics and government hydrogeological data.
    """

    VERY_SHALLOW_M = 5

    SHALLOW_M = 15

    MODERATE_M = 30

    DEEP_M = 50

    VERY_DEEP_M = 100

    # Observation age

    RECENT_DAYS = 365

    AGING_DAYS = 3 * 365

    OLD_DAYS = 5 * 365

    # Spatial confidence

    VERY_HIGH_DISTANCE_KM = 5

    HIGH_DISTANCE_KM = 15

    MEDIUM_DISTANCE_KM = 30

    LOW_DISTANCE_KM = 60


# ============================================================
# MODEL
# ============================================================

class GroundwaterModel:

    def __init__(
        self,
        thresholds: Optional[
            GroundwaterThresholds
        ] = None
    ):

        self.thresholds = (
            thresholds
            or GroundwaterThresholds()
        )

    # ========================================================
    # SPATIAL CONFIDENCE
    # ========================================================

    def spatial_confidence(
        self,
        distance_km: Optional[float]
    ) -> str:

        if distance_km is None:
            return "unknown"

        if (
            distance_km
            <= self.thresholds.VERY_HIGH_DISTANCE_KM
        ):
            return "very_high"

        if (
            distance_km
            <= self.thresholds.HIGH_DISTANCE_KM
        ):
            return "high"

        if (
            distance_km
            <= self.thresholds.MEDIUM_DISTANCE_KM
        ):
            return "medium"

        if (
            distance_km
            <= self.thresholds.LOW_DISTANCE_KM
        ):
            return "low"

        return "very_low"

    # ========================================================
    # GROUNDWATER LEVEL
    # ========================================================

    def assess_water_level(
        self,
        water_level_m: Optional[float]
    ) -> GroundwaterLevelAssessment:

        if water_level_m is None:

            return GroundwaterLevelAssessment(

                available=False,

                water_level_m=None,

                interpretation="unknown",

                concern_level="unknown",

                notes=(
                    "Groundwater-level observation "
                    "is unavailable."
                )
            )

        if water_level_m < 0:

            return GroundwaterLevelAssessment(

                available=True,

                water_level_m=water_level_m,

                interpretation="invalid",

                concern_level="unknown",

                notes=(
                    "Negative groundwater depth is "
                    "outside the expected depth-to-water "
                    "representation. Verify source units."
                )
            )

        if (
            water_level_m
            <= self.thresholds.VERY_SHALLOW_M
        ):

            return GroundwaterLevelAssessment(

                available=True,

                water_level_m=water_level_m,

                interpretation="very_shallow",

                concern_level="medium",

                notes=(
                    "Groundwater is relatively shallow. "
                    "This may reduce pumping depth but "
                    "does not establish sustainable yield."
                )
            )

        if (
            water_level_m
            <= self.thresholds.SHALLOW_M
        ):

            return GroundwaterLevelAssessment(

                available=True,

                water_level_m=water_level_m,

                interpretation="shallow",

                concern_level="low",

                notes=(
                    "Groundwater depth is relatively shallow. "
                    "Sustainable yield still requires "
                    "aquifer-level assessment."
                )
            )

        if (
            water_level_m
            <= self.thresholds.MODERATE_M
        ):

            return GroundwaterLevelAssessment(

                available=True,

                water_level_m=water_level_m,

                interpretation="moderate",

                concern_level="low",

                notes=(
                    "Moderate groundwater depth. "
                    "Pumping requirements depend on "
                    "aquifer characteristics."
                )
            )

        if (
            water_level_m
            <= self.thresholds.DEEP_M
        ):

            return GroundwaterLevelAssessment(

                available=True,

                water_level_m=water_level_m,

                interpretation="deep",

                concern_level="medium",

                notes=(
                    "Deep groundwater may require greater "
                    "pumping head and infrastructure."
                )
            )

        if (
            water_level_m
            <= self.thresholds.VERY_DEEP_M
        ):

            return GroundwaterLevelAssessment(

                available=True,

                water_level_m=water_level_m,

                interpretation="very_deep",

                concern_level="high",

                notes=(
                    "Very deep groundwater can increase "
                    "pumping requirements. Sustainable yield "
                    "must be independently verified."
                )
            )

        return GroundwaterLevelAssessment(

            available=True,

            water_level_m=water_level_m,

            interpretation="extremely_deep",

            concern_level="high",

            notes=(
                "Extremely deep groundwater observation. "
                "Detailed hydrogeological investigation "
                "is strongly recommended."
            )
        )

    # ========================================================
    # DATE PARSING
    # ========================================================

    @staticmethod
    def parse_date(
        value: Optional[str]
    ) -> Optional[date]:

        if not value:
            return None

        value = str(value).strip()

        formats = [

            "%Y-%m-%d",

            "%d-%m-%Y",

            "%d/%m/%Y",

            "%Y/%m/%d",

            "%d-%b-%Y",

            "%d %b %Y",

        ]

        for fmt in formats:

            try:

                return datetime.strptime(
                    value,
                    fmt
                ).date()

            except ValueError:

                continue

        try:

            return datetime.fromisoformat(
                value
            ).date()

        except ValueError:

            return None

    # ========================================================
    # RECENCY
    # ========================================================

    def assess_recency(
        self,
        observation_date: Optional[str],
        reference_date: Optional[date] = None
    ) -> ObservationRecency:

        if not observation_date:

            return ObservationRecency(

                available=False,

                observation_date=None,

                age_days=None,

                recency_category="unknown",

                confidence="unknown"
            )

        parsed_date = self.parse_date(
            observation_date
        )

        if parsed_date is None:

            return ObservationRecency(

                available=False,

                observation_date=observation_date,

                age_days=None,

                recency_category="invalid",

                confidence="unknown"
            )

        reference_date = (
            reference_date
            or datetime.utcnow().date()
        )

        age_days = (
            reference_date
            - parsed_date
        ).days

        # Future observation

        if age_days < 0:

            return ObservationRecency(

                available=True,

                observation_date=observation_date,

                age_days=age_days,

                recency_category="future",

                confidence="unknown"
            )

        if (
            age_days
            <= self.thresholds.RECENT_DAYS
        ):

            return ObservationRecency(

                available=True,

                observation_date=observation_date,

                age_days=age_days,

                recency_category="recent",

                confidence="high"
            )

        if (
            age_days
            <= self.thresholds.AGING_DAYS
        ):

            return ObservationRecency(

                available=True,

                observation_date=observation_date,

                age_days=age_days,

                recency_category="aging",

                confidence="medium"
            )

        if (
            age_days
            <= self.thresholds.OLD_DAYS
        ):

            return ObservationRecency(

                available=True,

                observation_date=observation_date,

                age_days=age_days,

                recency_category="old",

                confidence="low"
            )

        return ObservationRecency(

            available=True,

            observation_date=observation_date,

            age_days=age_days,

            recency_category="very_old",

            confidence="very_low"
        )

    # ========================================================
    # TEMPORAL COVERAGE
    # ========================================================

    @staticmethod
    def determine_temporal_coverage(
        observations: List[Any]
    ) -> str:

        dates = []

        for observation in observations:

            value = getattr(
                observation,
                "observation_date",
                None
            )

            parsed = GroundwaterModel.parse_date(
                value
            )

            if parsed:

                dates.append(parsed)

        if not dates:

            return "none"

        dates.sort()

        if len(dates) == 1:

            return "single_observation"

        span_days = (
            dates[-1]
            - dates[0]
        ).days

        if span_days >= 10 * 365:

            return "very_long_term"

        if span_days >= 5 * 365:

            return "long_term"

        if span_days >= 3 * 365:

            return "medium_term"

        if span_days >= 365:

            return "short_term"

        return "limited"

    # ========================================================
    # DATA COMPLETENESS
    # ========================================================

    @staticmethod
    def determine_data_completeness(
        observation: Any
    ) -> str:

        fields = [

            "water_level_m",

            "observation_date",

            "latitude",

            "longitude",

        ]

        available = 0

        for field in fields:

            if getattr(
                observation,
                field,
                None
            ) is not None:

                available += 1

        ratio = (
            available / len(fields)
        )

        if ratio == 1:

            return "high"

        if ratio >= 0.75:

            return "medium"

        if ratio > 0:

            return "low"

        return "unavailable"

    # ========================================================
    # SUSTAINABILITY STATUS
    # ========================================================

    @staticmethod
    def determine_sustainability(
        observation: Any,
        temporal_coverage: str
    ) -> str:

        """
        IMPORTANT:

        We cannot determine sustainable groundwater
        abstraction from a single water-level observation.

        Therefore this function deliberately returns
        'unknown' unless actual aquifer/yield information
        is supplied later.
        """

        aquifer_data = getattr(
            observation,
            "aquifer_yield_m3_day",
            None
        )

        recharge_data = getattr(
            observation,
            "annual_recharge_m3",
            None
        )

        abstraction_data = getattr(
            observation,
            "annual_abstraction_m3",
            None
        )

        if (
            aquifer_data is None
            and recharge_data is None
            and abstraction_data is None
        ):

            if temporal_coverage in {
                "very_long_term",
                "long_term"
            }:

                return "requires_hydrogeological_analysis"

            return "unknown"

        # Future implementation:
        #
        # sustainable yield =
        # recharge - existing abstraction
        #
        # subject to regulatory constraints.

        return "requires_hydrogeological_analysis"

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze_observation(
        self,
        observation: Any,
        distance_km: Optional[float] = None,
        related_observations: Optional[
            List[Any]
        ] = None
    ) -> GroundwaterAssessment:

        if observation is None:

            return GroundwaterAssessment(

                available=False,

                station_id=None,

                state=None,

                district=None,

                distance_km=distance_km,

                spatial_confidence=None,

                water_level=self.assess_water_level(
                    None
                ),

                recency=self.assess_recency(
                    None
                ),

                temporal_coverage="none",

                data_completeness="unavailable",

                extraction_sustainability="unknown",

                regulatory_status="unknown",

                concerns=[],

                warnings=[
                    "No groundwater observation available."
                ],

                summary=(
                    "Groundwater availability cannot be "
                    "assessed because no observation was supplied."
                )
            )

        related_observations = (
            related_observations
            or [observation]
        )

        water_level = self.assess_water_level(

            getattr(
                observation,
                "water_level_m",
                None
            )
        )

        recency = self.assess_recency(

            getattr(
                observation,
                "observation_date",
                None
            )
        )

        temporal_coverage = (
            self.determine_temporal_coverage(
                related_observations
            )
        )

        data_completeness = (
            self.determine_data_completeness(
                observation
            )
        )

        sustainability = (
            self.determine_sustainability(
                observation,
                temporal_coverage
            )
        )

        spatial_confidence = (
            self.spatial_confidence(
                distance_km
            )
        )

        concerns = []

        warnings = []

        # ----------------------------------------------------
        # WATER LEVEL
        # ----------------------------------------------------

        if water_level.concern_level == "high":

            concerns.append(
                "deep_groundwater"
            )

        elif water_level.concern_level == "medium":

            concerns.append(
                "groundwater_depth_requires_review"
            )

        # ----------------------------------------------------
        # RECENCY
        # ----------------------------------------------------

        if recency.confidence in {
            "low",
            "very_low"
        }:

            warnings.append(
                "Groundwater observation is old. "
                "Current conditions may differ."
            )

        # ----------------------------------------------------
        # SPATIAL
        # ----------------------------------------------------

        if spatial_confidence in {
            "low",
            "very_low"
        }:

            warnings.append(
                "Monitoring station is relatively far "
                "from the requested site."
            )

        # ----------------------------------------------------
        # TEMPORAL
        # ----------------------------------------------------

        if temporal_coverage in {
            "none",
            "single_observation",
            "limited"
        }:

            warnings.append(
                "Limited temporal coverage prevents "
                "strong seasonal groundwater conclusions."
            )

        # ----------------------------------------------------
        # SUSTAINABILITY
        # ----------------------------------------------------

        if sustainability in {
            "unknown",
            "requires_hydrogeological_analysis"
        }:

            warnings.append(
                "Sustainable groundwater abstraction "
                "cannot be established from the available "
                "monitoring observation alone."
            )

        # ----------------------------------------------------
        # REGULATION
        # ----------------------------------------------------

        warnings.append(
            "Groundwater extraction must be checked "
            "against applicable Indian groundwater "
            "regulatory requirements before development."
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary = self._summary(
            water_level=water_level,
            recency=recency,
            temporal_coverage=temporal_coverage,
            spatial_confidence=spatial_confidence,
            sustainability=sustainability
        )

        return GroundwaterAssessment(

            available=True,

            station_id=getattr(
                observation,
                "station_id",
                None
            ),

            state=getattr(
                observation,
                "state",
                None
            ),

            district=getattr(
                observation,
                "district",
                None
            ),

            distance_km=distance_km,

            spatial_confidence=spatial_confidence,

            water_level=water_level,

            recency=recency,

            temporal_coverage=temporal_coverage,

            data_completeness=data_completeness,

            extraction_sustainability=sustainability,

            regulatory_status="requires_verification",

            concerns=concerns,

            warnings=warnings,

            summary=summary
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def _summary(
        water_level: GroundwaterLevelAssessment,
        recency: ObservationRecency,
        temporal_coverage: str,
        spatial_confidence: str,
        sustainability: str
    ) -> str:

        if not water_level.available:

            return (
                "Groundwater-level data is unavailable."
            )

        if sustainability == "unknown":

            sustainability_text = (
                "Sustainable abstraction cannot be "
                "determined from the available data."
            )

        else:

            sustainability_text = (
                "Additional hydrogeological analysis "
                "is required before abstraction planning."
            )

        return (
            f"Groundwater level is classified as "
            f"'{water_level.interpretation}'. "
            f"Observation recency is "
            f"'{recency.recency_category}' and spatial "
            f"confidence is '{spatial_confidence}'. "
            f"Temporal coverage is "
            f"'{temporal_coverage}'. "
            f"{sustainability_text}"
        )

    # ========================================================
    # NEARBY OBSERVATION ADAPTER
    # ========================================================

    def analyze_nearby_observation(
        self,
        nearby_observation: Any,
        related_observations: Optional[
            List[Any]
        ] = None
    ) -> GroundwaterAssessment:

        if nearby_observation is None:

            return self.analyze_observation(
                None
            )

        observation = getattr(
            nearby_observation,
            "observation",
            nearby_observation
        )

        distance_km = getattr(
            nearby_observation,
            "distance_km",
            None
        )

        return self.analyze_observation(

            observation=observation,

            distance_km=distance_km,

            related_observations=(
                related_observations
                or [observation]
            )
        )


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def analyze_groundwater(
    observation: Any,
    distance_km: Optional[float] = None,
    related_observations: Optional[
        List[Any]
    ] = None
) -> Dict[str, Any]:

    model = GroundwaterModel()

    result = model.analyze_observation(

        observation=observation,

        distance_km=distance_km,

        related_observations=related_observations
    )

    return asdict(result)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from types import SimpleNamespace

    sample = SimpleNamespace(

        station_id="CGWB-TEST-001",

        state="Maharashtra",

        district="Nashik",

        latitude=20.0059,

        longitude=73.7797,

        observation_date="2025-06-15",

        water_level_m=18.4,

        source="CGWB"
    )

    result = analyze_groundwater(

        observation=sample,

        distance_km=8.2,

        related_observations=[
            sample
        ]
    )

    import json

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
            default=str
        )
    )