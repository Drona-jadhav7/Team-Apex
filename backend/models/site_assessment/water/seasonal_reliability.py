"""
India AI Grid
Seasonal Water Reliability Model

File:
    backend/models/site_assessment/water/seasonal_reliability.py

Purpose:
    Evaluate the seasonal reliability of a water source for
    preliminary data-center site assessment.

The model considers:

    - Monthly water observations
    - Seasonal availability
    - Dry-season conditions
    - Monsoon conditions
    - Inter-month variability
    - Missing observations
    - Low-water months
    - Critical dry-period performance

IMPORTANT
---------
This model does NOT determine legal water availability.

It also does NOT determine whether a data center can legally
withdraw a specific quantity of water.

It provides a hydrological reliability indicator that can later
be combined with:

    water_availability.py
    water_quality.py
    groundwater.py
    surface_water.py
    treatment.py
    infrastructure.py
    water_score.py
"""


from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any, Dict, List, Optional


# ============================================================
# TYPE ALIASES
# ============================================================

Number = Optional[float]


# ============================================================
# MONTH NAMES
# ============================================================

MONTH_NAMES: Dict[int, str] = {

    1: "January",

    2: "February",

    3: "March",

    4: "April",

    5: "May",

    6: "June",

    7: "July",

    8: "August",

    9: "September",

    10: "October",

    11: "November",

    12: "December",
}


# ============================================================
# MONTHLY OBSERVATION
# ============================================================


@dataclass
class MonthlyWaterObservation:
    """
    Normalized monthly water observation.

    value represents the measured water-availability indicator
    supplied by the upstream API.

    Depending on the source, this could represent:

        - river flow
        - reservoir storage
        - groundwater level
        - available water volume
        - another normalized indicator

    The unit must be specified by the upstream adapter.
    """

    month: int

    value: Number

    unit: Optional[str] = None

    observation_count: int = 1

    source: Optional[str] = None


# ============================================================
# SEASONAL RESULT
# ============================================================


@dataclass
class SeasonalPeriodResult:
    """
    Result for one seasonal period.
    """

    name: str

    months: List[int]

    months_available: int

    months_expected: int

    average_value: Number

    minimum_value: Number

    maximum_value: Number

    missing_months: List[int]

    low_water_months: List[int]

    reliability: str


# ============================================================
# COMPLETE ASSESSMENT
# ============================================================


@dataclass
class SeasonalReliabilityAssessment:
    """
    Complete seasonal reliability assessment.
    """

    data_available: bool

    months_available: int

    months_expected: int

    data_completeness: str

    annual_average: Number

    annual_minimum: Number

    annual_maximum: Number

    annual_variability: Number

    dry_season: SeasonalPeriodResult

    monsoon_season: SeasonalPeriodResult

    post_monsoon_season: SeasonalPeriodResult

    critical_dry_months: List[int]

    critical_dry_month_value: Number

    seasonal_reliability: str

    drought_sensitivity: str

    concerns: List[str]

    warnings: List[str]

    summary: str


# ============================================================
# THRESHOLDS
# ============================================================


class SeasonalReliabilityThresholds:
    """
    Preliminary screening thresholds.

    These are NOT engineering standards.

    They are used to identify patterns in historical or
    API-provided observations.
    """

    # Minimum fraction of annual average considered low.

    LOW_WATER_RATIO: float = 0.30

    VERY_LOW_WATER_RATIO: float = 0.15

    # Data completeness

    HIGH_COMPLETENESS: float = 0.90

    MEDIUM_COMPLETENESS: float = 0.70

    LOW_COMPLETENESS: float = 0.50

    # Variability

    LOW_VARIABILITY: float = 0.25

    MODERATE_VARIABILITY: float = 0.50

    HIGH_VARIABILITY: float = 0.75


# ============================================================
# MODEL
# ============================================================


class SeasonalReliabilityModel:
    """
    Analyze seasonal water reliability.
    """

    # --------------------------------------------------------
    # Seasonal definitions
    # --------------------------------------------------------

    DRY_SEASON_MONTHS: List[int] = [
        3,
        4,
        5,
    ]

    MONSOON_MONTHS: List[int] = [
        6,
        7,
        8,
        9,
    ]

    POST_MONSOON_MONTHS: List[int] = [
        10,
        11,
        12,
        1,
        2,
    ]

    def __init__(
        self,
        thresholds: Optional[
            SeasonalReliabilityThresholds
        ] = None,
    ) -> None:

        self.thresholds = (
            thresholds
            if thresholds is not None
            else SeasonalReliabilityThresholds()
        )

    # ========================================================
    # MONTH VALIDATION
    # ========================================================

    @staticmethod
    def valid_month(
        month: int,
    ) -> bool:

        return 1 <= month <= 12

    # ========================================================
    # NORMALIZE OBSERVATIONS
    # ========================================================

    @staticmethod
    def normalize_observations(
        observations: List[
            MonthlyWaterObservation
        ],
    ) -> Dict[int, float]:

        normalized: Dict[int, float] = {}

        for observation in observations:

            if not SeasonalReliabilityModel.valid_month(
                observation.month
            ):
                continue

            if observation.value is None:
                continue

            if observation.value < 0:
                continue

            normalized[
                observation.month
            ] = observation.value

        return normalized

    # ========================================================
    # DATA COMPLETENESS
    # ========================================================

    def data_completeness(
        self,
        observations: Dict[int, float],
    ) -> str:

        months_available: int = len(
            observations
        )

        completeness: float = (
            months_available / 12.0
        )

        if (
            completeness
            >= self.thresholds.HIGH_COMPLETENESS
        ):
            return "high"

        if (
            completeness
            >= self.thresholds.MEDIUM_COMPLETENESS
        ):
            return "medium"

        if (
            completeness
            >= self.thresholds.LOW_COMPLETENESS
        ):
            return "low"

        return "very_low"

    # ========================================================
    # STATISTICS
    # ========================================================

    @staticmethod
    def calculate_average(
        values: List[float],
    ) -> Number:

        if not values:
            return None

        return mean(values)

    @staticmethod
    def calculate_minimum(
        values: List[float],
    ) -> Number:

        if not values:
            return None

        return min(values)

    @staticmethod
    def calculate_maximum(
        values: List[float],
    ) -> Number:

        if not values:
            return None

        return max(values)

    # ========================================================
    # VARIABILITY
    # ========================================================

    @staticmethod
    def calculate_variability(
        values: List[float],
    ) -> Number:
        """
        Calculate normalized range:

            (max - min) / average

        This is intentionally simple and transparent.

        A future version can replace this with a more
        statistically rigorous coefficient of variation when
        sufficient historical data becomes available.
        """

        if not values:
            return None

        average: float = mean(values)

        if average == 0:
            return None

        minimum: float = min(values)

        maximum: float = max(values)

        return (
            maximum - minimum
        ) / average

    # ========================================================
    # LOW WATER MONTHS
    # ========================================================

    def identify_low_water_months(
        self,
        observations: Dict[int, float],
        annual_average: Number,
    ) -> List[int]:

        if annual_average is None:
            return []

        if annual_average <= 0:
            return []

        low_threshold: float = (
            annual_average
            * self.thresholds.LOW_WATER_RATIO
        )

        low_months: List[int] = []

        for month, value in observations.items():

            if value <= low_threshold:

                low_months.append(
                    month
                )

        low_months.sort()

        return low_months

    # ========================================================
    # SEASON ANALYSIS
    # ========================================================

    def analyze_period(
        self,
        name: str,
        months: List[int],
        observations: Dict[int, float],
        annual_average: Number,
    ) -> SeasonalPeriodResult:

        period_values: List[float] = []

        missing_months: List[int] = []

        low_water_months: List[int] = []

        for month in months:

            if month not in observations:

                missing_months.append(
                    month
                )

                continue

            value: float = observations[
                month
            ]

            period_values.append(
                value
            )

            if (
                annual_average is not None
                and annual_average > 0
            ):

                low_threshold: float = (
                    annual_average
                    * self.thresholds.LOW_WATER_RATIO
                )

                if value <= low_threshold:

                    low_water_months.append(
                        month
                    )

        months_available: int = len(
            period_values
        )

        months_expected: int = len(
            months
        )

        average_value: Number = (
            self.calculate_average(
                period_values
            )
        )

        minimum_value: Number = (
            self.calculate_minimum(
                period_values
            )
        )

        maximum_value: Number = (
            self.calculate_maximum(
                period_values
            )
        )

        reliability: str = (
            self.period_reliability(
                months_available=months_available,
                months_expected=months_expected,
                average_value=average_value,
                annual_average=annual_average,
                low_water_months=low_water_months,
            )
        )

        return SeasonalPeriodResult(

            name=name,

            months=months,

            months_available=months_available,

            months_expected=months_expected,

            average_value=average_value,

            minimum_value=minimum_value,

            maximum_value=maximum_value,

            missing_months=missing_months,

            low_water_months=low_water_months,

            reliability=reliability,
        )

    # ========================================================
    # PERIOD RELIABILITY
    # ========================================================

    def period_reliability(
        self,
        months_available: int,
        months_expected: int,
        average_value: Number,
        annual_average: Number,
        low_water_months: List[int],
    ) -> str:

        if months_expected == 0:
            return "unknown"

        completeness: float = (
            months_available
            / months_expected
        )

        if completeness < 0.50:
            return "insufficient_data"

        if (
            average_value is None
            or annual_average is None
            or annual_average <= 0
        ):
            return "unknown"

        average_ratio: float = (
            average_value
            / annual_average
        )

        low_month_ratio: float = (
            len(low_water_months)
            / months_expected
        )

        if (
            average_ratio
            <= self.thresholds.VERY_LOW_WATER_RATIO
            or low_month_ratio >= 0.75
        ):

            return "very_low"

        if (
            average_ratio
            <= self.thresholds.LOW_WATER_RATIO
            or low_month_ratio >= 0.50
        ):

            return "low"

        if (
            average_ratio < 0.75
            or low_month_ratio > 0.0
        ):

            return "moderate"

        return "high"

    # ========================================================
    # DRY-SEASON ANALYSIS
    # ========================================================

    def analyze_dry_season(
        self,
        observations: Dict[int, float],
        annual_average: Number,
    ) -> SeasonalPeriodResult:

        return self.analyze_period(
            name="dry_season",
            months=self.DRY_SEASON_MONTHS,
            observations=observations,
            annual_average=annual_average,
        )

    # ========================================================
    # MONSOON ANALYSIS
    # ========================================================

    def analyze_monsoon(
        self,
        observations: Dict[int, float],
        annual_average: Number,
    ) -> SeasonalPeriodResult:

        return self.analyze_period(
            name="monsoon",
            months=self.MONSOON_MONTHS,
            observations=observations,
            annual_average=annual_average,
        )

    # ========================================================
    # POST-MONSOON ANALYSIS
    # ========================================================

    def analyze_post_monsoon(
        self,
        observations: Dict[int, float],
        annual_average: Number,
    ) -> SeasonalPeriodResult:

        return self.analyze_period(
            name="post_monsoon",
            months=self.POST_MONSOON_MONTHS,
            observations=observations,
            annual_average=annual_average,
        )

    # ========================================================
    # CRITICAL DRY MONTH
    # ========================================================

    def critical_dry_month(
        self,
        observations: Dict[int, float],
    ) -> tuple[
        List[int],
        Number,
    ]:

        available_dry_months: Dict[
            int,
            float,
        ] = {}

        for month in self.DRY_SEASON_MONTHS:

            if month in observations:

                available_dry_months[
                    month
                ] = observations[month]

        if not available_dry_months:

            return [], None

        minimum_value: float = min(
            available_dry_months.values()
        )

        critical_months: List[int] = [

            month

            for month, value
            in available_dry_months.items()

            if value == minimum_value
        ]

        critical_months.sort()

        return (
            critical_months,
            minimum_value,
        )

    # ========================================================
    # DROUGHT SENSITIVITY
    # ========================================================

    def drought_sensitivity(
        self,
        dry_season: SeasonalPeriodResult,
        annual_variability: Number,
    ) -> str:

        if (
            dry_season.reliability
            == "insufficient_data"
        ):

            return "unknown"

        if (
            annual_variability is not None
            and annual_variability
            >= self.thresholds.HIGH_VARIABILITY
        ):

            if dry_season.reliability in {
                "low",
                "very_low",
            }:

                return "high"

            return "moderate"

        if dry_season.reliability == "very_low":

            return "high"

        if dry_season.reliability == "low":

            return "moderate"

        return "low"

    # ========================================================
    # OVERALL RELIABILITY
    # ========================================================

    def overall_reliability(
        self,
        data_completeness: str,
        dry_season: SeasonalPeriodResult,
        annual_variability: Number,
    ) -> str:

        if data_completeness == "very_low":

            return "insufficient_data"

        if (
            dry_season.reliability
            in {
                "very_low",
                "insufficient_data",
            }
        ):

            return "low"

        if dry_season.reliability == "low":

            return "moderate"

        if (
            annual_variability is not None
            and annual_variability
            >= self.thresholds.HIGH_VARIABILITY
        ):

            return "moderate"

        if data_completeness == "low":

            return "moderate"

        return "high"

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(
        self,
        observations: List[
            MonthlyWaterObservation
        ],
    ) -> SeasonalReliabilityAssessment:

        normalized: Dict[
            int,
            float,
        ] = self.normalize_observations(
            observations
        )

        months_available: int = len(
            normalized
        )

        data_available: bool = (
            months_available > 0
        )

        completeness: str = (
            self.data_completeness(
                normalized
            )
        )

        values: List[float] = list(
            normalized.values()
        )

        annual_average: Number = (
            self.calculate_average(
                values
            )
        )

        annual_minimum: Number = (
            self.calculate_minimum(
                values
            )
        )

        annual_maximum: Number = (
            self.calculate_maximum(
                values
            )
        )

        annual_variability: Number = (
            self.calculate_variability(
                values
            )
        )

        # ----------------------------------------------------
        # Seasonal analysis
        # ----------------------------------------------------

        dry_season: SeasonalPeriodResult = (
            self.analyze_dry_season(
                observations=normalized,
                annual_average=annual_average,
            )
        )

        monsoon_season: SeasonalPeriodResult = (
            self.analyze_monsoon(
                observations=normalized,
                annual_average=annual_average,
            )
        )

        post_monsoon_season: SeasonalPeriodResult = (
            self.analyze_post_monsoon(
                observations=normalized,
                annual_average=annual_average,
            )
        )

        # ----------------------------------------------------
        # Critical dry month
        # ----------------------------------------------------

        (
            critical_dry_months,
            critical_dry_month_value,
        ) = self.critical_dry_month(
            normalized
        )

        # ----------------------------------------------------
        # Drought sensitivity
        # ----------------------------------------------------

        drought_sensitivity: str = (
            self.drought_sensitivity(
                dry_season=dry_season,
                annual_variability=annual_variability,
            )
        )

        # ----------------------------------------------------
        # Overall reliability
        # ----------------------------------------------------

        reliability: str = (
            self.overall_reliability(
                data_completeness=completeness,
                dry_season=dry_season,
                annual_variability=annual_variability,
            )
        )

        # ----------------------------------------------------
        # Concerns
        # ----------------------------------------------------

        concerns: List[str] = []

        warnings: List[str] = []

        if dry_season.reliability in {
            "low",
            "very_low",
        }:

            concerns.append(
                "dry_season_water_reliability"
            )

        if len(
            dry_season.low_water_months
        ) > 0:

            concerns.append(
                "low_water_conditions_during_dry_season"
            )

        if drought_sensitivity == "high":

            concerns.append(
                "high_drought_sensitivity"
            )

        if (
            annual_variability is not None
            and annual_variability
            >= self.thresholds.HIGH_VARIABILITY
        ):

            concerns.append(
                "high_annual_water_variability"
            )

        if completeness in {
            "low",
            "very_low",
        }:

            warnings.append(
                "Insufficient monthly observations "
                "may reduce seasonal reliability."
            )

        if (
            len(
                dry_season.missing_months
            )
            > 0
        ):

            warnings.append(
                "One or more dry-season months "
                "have missing observations."
            )

        if (
            annual_variability is not None
            and annual_variability
            >= self.thresholds.MODERATE_VARIABILITY
        ):

            warnings.append(
                "Water conditions vary substantially "
                "between months."
            )

        warnings.append(
            "Seasonal reliability is an analytical "
            "indicator and does not establish legal "
            "or guaranteed water supply."
        )

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        summary: str = (
            self.generate_summary(
                data_completeness=completeness,
                annual_average=annual_average,
                annual_variability=annual_variability,
                dry_season=dry_season,
                drought_sensitivity=drought_sensitivity,
                reliability=reliability,
            )
        )

        return SeasonalReliabilityAssessment(

            data_available=data_available,

            months_available=months_available,

            months_expected=12,

            data_completeness=completeness,

            annual_average=annual_average,

            annual_minimum=annual_minimum,

            annual_maximum=annual_maximum,

            annual_variability=annual_variability,

            dry_season=dry_season,

            monsoon_season=monsoon_season,

            post_monsoon_season=post_monsoon_season,

            critical_dry_months=critical_dry_months,

            critical_dry_month_value=critical_dry_month_value,

            seasonal_reliability=reliability,

            drought_sensitivity=drought_sensitivity,

            concerns=concerns,

            warnings=warnings,

            summary=summary,
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def generate_summary(
        data_completeness: str,
        annual_average: Number,
        annual_variability: Number,
        dry_season: SeasonalPeriodResult,
        drought_sensitivity: str,
        reliability: str,
    ) -> str:

        if annual_average is None:

            average_text: str = (
                "unknown"
            )

        else:

            average_text = (
                f"{annual_average:.3f}"
            )

        if annual_variability is None:

            variability_text: str = (
                "unknown"
            )

        else:

            variability_text = (
                f"{annual_variability:.3f}"
            )

        return (
            "Seasonal water analysis found "
            f"{data_completeness} data completeness. "
            f"The annual observed average is "
            f"{average_text}, with normalized "
            f"variability of {variability_text}. "
            f"The dry-season reliability is "
            f"'{dry_season.reliability}', while "
            f"drought sensitivity is "
            f"'{drought_sensitivity}'. "
            f"The resulting seasonal reliability "
            f"indicator is '{reliability}'."
        )


# ============================================================
# PUBLIC API
# ============================================================


def analyze_seasonal_reliability(
    observations: List[
        MonthlyWaterObservation
    ],
) -> Dict[str, Any]:
    """
    Public service-layer function.
    """

    model: SeasonalReliabilityModel = (
        SeasonalReliabilityModel()
    )

    result: SeasonalReliabilityAssessment = (
        model.analyze(
            observations
        )
    )

    return asdict(result)


# ============================================================
# DEVELOPMENT TEST
# ============================================================


if __name__ == "__main__":

    import json

    sample_observations: List[
        MonthlyWaterObservation
    ] = [

        MonthlyWaterObservation(
            month=1,
            value=65.0,
            unit="normalized",
            source="TEST",
        ),

        MonthlyWaterObservation(
            month=2,
            value=60.0,
            unit="normalized",
            source="TEST",
        ),

        MonthlyWaterObservation(
            month=3,
            value=48.0,
            unit="normalized",
            source="TEST",
        ),

        MonthlyWaterObservation(
            month=4,
            value=35.0,
            unit="normalized",
            source="TEST",
        ),

        MonthlyWaterObservation(
            month=5,
            value=22.0,
            unit="normalized",
            source="TEST",
        ),

        MonthlyWaterObservation(
            month=6,
            value=55.0,
            unit="normalized",
            source="TEST",
        ),

        MonthlyWaterObservation(
            month=7,
            value=95.0,
            unit="normalized",
            source="TEST",
        ),

        MonthlyWaterObservation(
            month=8,
            value=100.0,
            unit="normalized",
            source="TEST",
        ),

        MonthlyWaterObservation(
            month=9,
            value=85.0,
            unit="normalized",
            source="TEST",
        ),

        MonthlyWaterObservation(
            month=10,
            value=72.0,
            unit="normalized",
            source="TEST",
        ),

        MonthlyWaterObservation(
            month=11,
            value=68.0,
            unit="normalized",
            source="TEST",
        ),

        MonthlyWaterObservation(
            month=12,
            value=66.0,
            unit="normalized",
            source="TEST",
        ),
    ]

    model: SeasonalReliabilityModel = (
        SeasonalReliabilityModel()
    )

    result: SeasonalReliabilityAssessment = (
        model.analyze(
            sample_observations
        )
    )

    print(
        json.dumps(
            asdict(result),
            indent=2,
            ensure_ascii=False,
        )
    )