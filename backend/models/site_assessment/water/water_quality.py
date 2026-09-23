"""
India AI Grid
Water Quality Assessment Model

Path:
    backend/models/site_assessment/water/water_quality.py

Purpose:
    Analyze raw/normalized water-quality observations and
    determine their relevance to data-center cooling systems.

Important:
    This model does NOT decide whether a location is suitable
    for a data center.

    It only evaluates water-quality characteristics and identifies
    potential treatment/cooling concerns.

Input:
    Normalized groundwater/surface-water observations.

Output:
    Structured WaterQualityAssessment.

Design principle:
    Raw measurement
        ↓
    Parameter interpretation
        ↓
    Cooling relevance
        ↓
    Treatment concern
        ↓
    Assessment

Final site scoring belongs to water_score.py.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


# ============================================================
# DATA QUALITY
# ============================================================

@dataclass
class ParameterAssessment:
    """
    Assessment of one water-quality parameter.
    """

    parameter: str

    value: Optional[float]

    unit: str

    available: bool

    concern_level: str

    cooling_relevance: str

    treatment_concern: str

    notes: str


@dataclass
class WaterQualityAssessment:
    """
    Complete water-quality assessment for one observation.
    """

    available: bool

    source: Optional[str]

    observation_date: Optional[str]

    station_id: Optional[str]

    distance_km: Optional[float]

    parameters: List[ParameterAssessment]

    critical_concerns: List[str]

    treatment_concerns: List[str]

    missing_parameters: List[str]

    data_quality: str

    summary: str


# ============================================================
# THRESHOLD CONFIGURATION
# ============================================================

class WaterQualityThresholds:
    """
    Reference ranges used for engineering screening.

    IMPORTANT:
        These are screening thresholds, NOT universal data-center
        design specifications.

    Actual cooling-water requirements depend on:
        - cooling technology
        - manufacturer requirements
        - cycles of concentration
        - treatment plant design
        - local water chemistry
        - applicable standards

    These values should therefore be treated as configurable.
    """

    PH_MIN = 6.5
    PH_MAX = 8.5

    TDS_LOW = 300
    TDS_HIGH = 1000

    EC_LOW = 500
    EC_HIGH = 1500

    HARDNESS_LOW = 150
    HARDNESS_HIGH = 300

    CHLORIDE_HIGH = 250

    SULFATE_HIGH = 250

    IRON_HIGH = 0.3

    MANGANESE_HIGH = 0.1

    SILICA_HIGH = 25

    FLUORIDE_HIGH = 1.5

    NITRATE_HIGH = 45

    ARSENIC_HIGH = 0.01

    TURBIDITY_HIGH = 5


# ============================================================
# WATER QUALITY MODEL
# ============================================================

class WaterQualityModel:

    def __init__(
        self,
        thresholds: Optional[
            WaterQualityThresholds
        ] = None
    ):

        self.thresholds = (
            thresholds
            or WaterQualityThresholds()
        )

    # ========================================================
    # GENERIC HELPERS
    # ========================================================

    @staticmethod
    def _assessment(
        parameter: str,
        value: Optional[float],
        unit: str,
        concern_level: str,
        cooling_relevance: str,
        treatment_concern: str,
        notes: str
    ) -> ParameterAssessment:

        return ParameterAssessment(

            parameter=parameter,

            value=value,

            unit=unit,

            available=value is not None,

            concern_level=concern_level,

            cooling_relevance=cooling_relevance,

            treatment_concern=treatment_concern,

            notes=notes
        )

    # ========================================================
    # PH
    # ========================================================

    def assess_ph(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "pH",
                None,
                "pH units",
                "unknown",
                "high",
                "unknown",
                "pH measurement unavailable."
            )

        if (
            value < self.thresholds.PH_MIN
            or
            value > self.thresholds.PH_MAX
        ):

            return self._assessment(
                "pH",
                value,
                "pH units",
                "high",
                "high",
                "pH correction may be required.",
                "pH is outside the configured screening range."
            )

        return self._assessment(
            "pH",
            value,
            "pH units",
            "low",
            "high",
            "low",
            "pH is within the configured screening range."
        )

    # ========================================================
    # TDS
    # ========================================================

    def assess_tds(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "TDS",
                None,
                "mg/L",
                "unknown",
                "high",
                "unknown",
                "TDS measurement unavailable."
            )

        if value > self.thresholds.TDS_HIGH:

            return self._assessment(
                "TDS",
                value,
                "mg/L",
                "high",
                "high",
                "High dissolved solids may require treatment.",
                "Elevated TDS can increase concentration and scaling/corrosion concerns."
            )

        if value > self.thresholds.TDS_LOW:

            return self._assessment(
                "TDS",
                value,
                "mg/L",
                "medium",
                "high",
                "Treatment may be beneficial depending on cooling design.",
                "Moderate TDS should be evaluated against the cooling system."
            )

        return self._assessment(
            "TDS",
            value,
            "mg/L",
            "low",
            "high",
            "low",
            "TDS is relatively low for screening purposes."
        )

    # ========================================================
    # ELECTRICAL CONDUCTIVITY
    # ========================================================

    def assess_ec(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "Electrical Conductivity",
                None,
                "µS/cm",
                "unknown",
                "high",
                "unknown",
                "Electrical conductivity unavailable."
            )

        if value > self.thresholds.EC_HIGH:

            return self._assessment(
                "Electrical Conductivity",
                value,
                "µS/cm",
                "high",
                "high",
                "Demineralization/RO treatment may be required.",
                "High conductivity indicates elevated dissolved ionic content."
            )

        if value > self.thresholds.EC_LOW:

            return self._assessment(
                "Electrical Conductivity",
                value,
                "µS/cm",
                "medium",
                "high",
                "Treatment may be required depending on cooling technology.",
                "Moderate conductivity should be evaluated for recirculating systems."
            )

        return self._assessment(
            "Electrical Conductivity",
            value,
            "µS/cm",
            "low",
            "high",
            "low",
            "Conductivity is relatively low."
        )

    # ========================================================
    # HARDNESS
    # ========================================================

    def assess_hardness(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "Total Hardness",
                None,
                "mg/L as CaCO3",
                "unknown",
                "high",
                "unknown",
                "Hardness measurement unavailable."
            )

        if value > self.thresholds.HARDNESS_HIGH:

            return self._assessment(
                "Total Hardness",
                value,
                "mg/L as CaCO3",
                "high",
                "high",
                "Softening or membrane treatment may be required.",
                "High hardness can contribute to scaling."
            )

        if value > self.thresholds.HARDNESS_LOW:

            return self._assessment(
                "Total Hardness",
                value,
                "mg/L as CaCO3",
                "medium",
                "high",
                "Softening may be considered.",
                "Moderate hardness requires cooling-system evaluation."
            )

        return self._assessment(
            "Total Hardness",
            value,
            "mg/L as CaCO3",
            "low",
            "high",
            "low",
            "Hardness is relatively low."
        )

    # ========================================================
    # CHLORIDE
    # ========================================================

    def assess_chloride(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "Chloride",
                None,
                "mg/L",
                "unknown",
                "high",
                "unknown",
                "Chloride measurement unavailable."
            )

        if value > self.thresholds.CHLORIDE_HIGH:

            return self._assessment(
                "Chloride",
                value,
                "mg/L",
                "high",
                "high",
                "Corrosion-control treatment may be required.",
                "Elevated chloride can increase corrosion concerns."
            )

        return self._assessment(
            "Chloride",
            value,
            "mg/L",
            "low",
            "high",
            "low",
            "Chloride is below the configured screening threshold."
        )

    # ========================================================
    # SULFATE
    # ========================================================

    def assess_sulfate(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "Sulfate",
                None,
                "mg/L",
                "unknown",
                "medium",
                "unknown",
                "Sulfate measurement unavailable."
            )

        if value > self.thresholds.SULFATE_HIGH:

            return self._assessment(
                "Sulfate",
                value,
                "mg/L",
                "high",
                "medium",
                "Treatment may be required.",
                "Elevated sulfate can contribute to scaling/corrosion considerations."
            )

        return self._assessment(
            "Sulfate",
            value,
            "mg/L",
            "low",
            "medium",
            "low",
            "Sulfate is below the configured screening threshold."
        )

    # ========================================================
    # SILICA
    # ========================================================

    def assess_silica(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "Silica",
                None,
                "mg/L",
                "unknown",
                "high",
                "unknown",
                "Silica measurement unavailable."
            )

        if value > self.thresholds.SILICA_HIGH:

            return self._assessment(
                "Silica",
                value,
                "mg/L",
                "high",
                "high",
                "Advanced treatment may be required.",
                "Elevated silica can contribute to deposits/scaling in cooling systems."
            )

        return self._assessment(
            "Silica",
            value,
            "mg/L",
            "low",
            "high",
            "low",
            "Silica is below the configured screening threshold."
        )

    # ========================================================
    # IRON
    # ========================================================

    def assess_iron(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "Iron",
                None,
                "mg/L",
                "unknown",
                "medium",
                "unknown",
                "Iron measurement unavailable."
            )

        if value > self.thresholds.IRON_HIGH:

            return self._assessment(
                "Iron",
                value,
                "mg/L",
                "high",
                "medium",
                "Iron removal may be required.",
                "Elevated iron may cause deposits and operational issues."
            )

        return self._assessment(
            "Iron",
            value,
            "mg/L",
            "low",
            "medium",
            "low",
            "Iron is below the configured screening threshold."
        )

    # ========================================================
    # MANGANESE
    # ========================================================

    def assess_manganese(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "Manganese",
                None,
                "mg/L",
                "unknown",
                "medium",
                "unknown",
                "Manganese measurement unavailable."
            )

        if value > self.thresholds.MANGANESE_HIGH:

            return self._assessment(
                "Manganese",
                value,
                "mg/L",
                "high",
                "medium",
                "Manganese removal may be required.",
                "Elevated manganese can create deposits and treatment concerns."
            )

        return self._assessment(
            "Manganese",
            value,
            "mg/L",
            "low",
            "medium",
            "low",
            "Manganese is below the configured screening threshold."
        )

    # ========================================================
    # NITRATE
    # ========================================================

    def assess_nitrate(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "Nitrate",
                None,
                "mg/L",
                "unknown",
                "low",
                "unknown",
                "Nitrate measurement unavailable."
            )

        if value > self.thresholds.NITRATE_HIGH:

            return self._assessment(
                "Nitrate",
                value,
                "mg/L",
                "high",
                "low",
                "Water treatment may be required.",
                "Elevated nitrate indicates water-quality concerns."
            )

        return self._assessment(
            "Nitrate",
            value,
            "mg/L",
            "low",
            "low",
            "low",
            "Nitrate is below the configured screening threshold."
        )

    # ========================================================
    # FLUORIDE
    # ========================================================

    def assess_fluoride(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "Fluoride",
                None,
                "mg/L",
                "unknown",
                "low",
                "unknown",
                "Fluoride measurement unavailable."
            )

        if value > self.thresholds.FLUORIDE_HIGH:

            return self._assessment(
                "Fluoride",
                value,
                "mg/L",
                "high",
                "low",
                "Treatment may be required.",
                "Elevated fluoride represents a water-quality concern."
            )

        return self._assessment(
            "Fluoride",
            value,
            "mg/L",
            "low",
            "low",
            "low",
            "Fluoride is below the configured screening threshold."
        )

    # ========================================================
    # ARSENIC
    # ========================================================

    def assess_arsenic(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "Arsenic",
                None,
                "mg/L",
                "unknown",
                "low",
                "unknown",
                "Arsenic measurement unavailable."
            )

        if value > self.thresholds.ARSENIC_HIGH:

            return self._assessment(
                "Arsenic",
                value,
                "mg/L",
                "high",
                "low",
                "Specialized treatment may be required.",
                "Arsenic exceeds the configured screening threshold."
            )

        return self._assessment(
            "Arsenic",
            value,
            "mg/L",
            "low",
            "low",
            "low",
            "Arsenic is below the configured screening threshold."
        )

    # ========================================================
    # TURBIDITY
    # ========================================================

    def assess_turbidity(
        self,
        value: Optional[float]
    ) -> ParameterAssessment:

        if value is None:

            return self._assessment(
                "Turbidity",
                None,
                "NTU",
                "unknown",
                "medium",
                "unknown",
                "Turbidity measurement unavailable."
            )

        if value > self.thresholds.TURBIDITY_HIGH:

            return self._assessment(
                "Turbidity",
                value,
                "NTU",
                "high",
                "medium",
                "Filtration may be required.",
                "Elevated turbidity can increase filtration requirements."
            )

        return self._assessment(
            "Turbidity",
            value,
            "NTU",
            "low",
            "medium",
            "low",
            "Turbidity is below the configured screening threshold."
        )

    # ========================================================
    # FULL OBSERVATION
    # ========================================================

    def analyze_observation(
        self,
        observation: Any,
        distance_km: Optional[float] = None
    ) -> WaterQualityAssessment:

        if observation is None:

            return WaterQualityAssessment(
                available=False,
                source=None,
                observation_date=None,
                station_id=None,
                distance_km=distance_km,
                parameters=[],
                critical_concerns=[],
                treatment_concerns=[],
                missing_parameters=[
                    "all"
                ],
                data_quality="unavailable",
                summary="No water-quality observation available."
            )

        assessments = [

            self.assess_ph(
                getattr(
                    observation,
                    "ph",
                    None
                )
            ),

            self.assess_tds(
                getattr(
                    observation,
                    "tds_mg_l",
                    None
                )
            ),

            self.assess_ec(
                getattr(
                    observation,
                    "electrical_conductivity_us_cm",
                    None
                )
            ),

            self.assess_hardness(
                getattr(
                    observation,
                    "total_hardness_mg_l",
                    None
                )
            ),

            self.assess_chloride(
                getattr(
                    observation,
                    "chloride_mg_l",
                    None
                )
            ),

            self.assess_sulfate(
                getattr(
                    observation,
                    "sulfate_mg_l",
                    None
                )
            ),

            self.assess_silica(
                getattr(
                    observation,
                    "silica_mg_l",
                    None
                )
            ),

            self.assess_iron(
                getattr(
                    observation,
                    "iron_mg_l",
                    None
                )
            ),

            self.assess_manganese(
                getattr(
                    observation,
                    "manganese_mg_l",
                    None
                )
            ),

            self.assess_nitrate(
                getattr(
                    observation,
                    "nitrate_mg_l",
                    None
                )
            ),

            self.assess_fluoride(
                getattr(
                    observation,
                    "fluoride_mg_l",
                    None
                )
            ),

            self.assess_arsenic(
                getattr(
                    observation,
                    "arsenic_mg_l",
                    None
                )
            ),

            self.assess_turbidity(
                getattr(
                    observation,
                    "turbidity_ntu",
                    None
                )
            )
        ]

        critical_concerns = []

        treatment_concerns = []

        missing_parameters = []

        for assessment in assessments:

            if not assessment.available:

                missing_parameters.append(
                    assessment.parameter
                )

            if assessment.concern_level == "high":

                critical_concerns.append(
                    assessment.parameter
                )

            if (
                assessment.treatment_concern
                not in {
                    "low",
                    "unknown"
                }
            ):

                treatment_concerns.append(
                    assessment.parameter
                )

        available_count = sum(
            1
            for item in assessments
            if item.available
        )

        total_count = len(assessments)

        completeness = (
            available_count / total_count
            if total_count
            else 0
        )

        if completeness >= 0.8:

            data_quality = "high"

        elif completeness >= 0.5:

            data_quality = "medium"

        elif completeness > 0:

            data_quality = "low"

        else:

            data_quality = "unavailable"

        summary = self._generate_summary(
            critical_concerns,
            treatment_concerns,
            missing_parameters,
            data_quality
        )

        return WaterQualityAssessment(

            available=True,

            source=getattr(
                observation,
                "source",
                None
            ),

            observation_date=getattr(
                observation,
                "observation_date",
                None
            ),

            station_id=getattr(
                observation,
                "station_id",
                None
            ),

            distance_km=distance_km,

            parameters=assessments,

            critical_concerns=critical_concerns,

            treatment_concerns=treatment_concerns,

            missing_parameters=missing_parameters,

            data_quality=data_quality,

            summary=summary
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def _generate_summary(
        critical_concerns: List[str],
        treatment_concerns: List[str],
        missing_parameters: List[str],
        data_quality: str
    ) -> str:

        if data_quality == "unavailable":

            return (
                "Water-quality data is unavailable."
            )

        if critical_concerns:

            return (
                "One or more water-quality parameters "
                "show elevated screening concerns. "
                "Additional treatment assessment is required."
            )

        if treatment_concerns:

            return (
                "Water-quality data is available, but "
                "one or more parameters may require "
                "water treatment depending on the "
                "cooling-system design."
            )

        if missing_parameters:

            return (
                "Available measurements do not show "
                "major configured screening concerns, "
                "but some parameters are missing."
            )

        return (
            "Available water-quality measurements do not "
            "show major configured screening concerns."
        )

    # ========================================================
    # CONVENIENCE METHOD
    # ========================================================

    def analyze_nearby_observation(
        self,
        nearby_observation: Any
    ) -> WaterQualityAssessment:

        if nearby_observation is None:

            return self.analyze_observation(
                None
            )

        observation = getattr(
            nearby_observation,
            "observation",
            nearby_observation
        )

        distance = getattr(
            nearby_observation,
            "distance_km",
            None
        )

        return self.analyze_observation(
            observation=observation,
            distance_km=distance
        )


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def analyze_water_quality(
    observation: Any,
    distance_km: Optional[float] = None
) -> Dict[str, Any]:

    model = WaterQualityModel()

    result = model.analyze_observation(
        observation=observation,
        distance_km=distance_km
    )

    return asdict(result)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from types import SimpleNamespace

    sample = SimpleNamespace(

        station_id="TEST-001",

        observation_date="2024-05-15",

        ph=7.4,

        tds_mg_l=420,

        electrical_conductivity_us_cm=680,

        total_hardness_mg_l=180,

        chloride_mg_l=95,

        sulfate_mg_l=80,

        silica_mg_l=18,

        iron_mg_l=0.12,

        manganese_mg_l=0.04,

        nitrate_mg_l=12,

        fluoride_mg_l=0.7,

        arsenic_mg_l=0.002,

        turbidity_ntu=2.1,

        source="CGWB",

    )

    result = analyze_water_quality(
        observation=sample,
        distance_km=8.4
    )

    import json

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )