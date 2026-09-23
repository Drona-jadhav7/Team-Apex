"""
India AI Grid
Water Supply-Demand Balance Model

File:
    backend/models/site_assessment/water/water_supply_demand.py

Purpose:
    Compare sustainable water supply against data-center water demand.

This model combines:
    - Sustainable water supply
    - Average data-center demand
    - Peak data-center demand
    - Dry-season supply and demand
    - Annual supply and demand
    - Seasonal reliability
    - Data completeness

Outputs:
    - Supply-demand ratio
    - Supply coverage
    - Surplus
    - Deficit
    - Peak stress
    - Dry-season stress
    - Overall water stress
    - Planning recommendations

IMPORTANT:
    This is a preliminary site-screening model.

    It does not establish:
        - legal water rights
        - permitted abstraction
        - guaranteed water supply
        - environmental clearance
        - groundwater extraction permission
        - government allocation
"""


from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


# ============================================================
# TYPE ALIAS
# ============================================================

Number = Optional[float]


# ============================================================
# INPUT MODEL
# ============================================================


@dataclass
class WaterSupplyDemandInput:
    """
    Input data required for water supply-demand analysis.

    All water quantities are expressed in m3/day unless
    otherwise specified.
    """

    sustainable_supply_m3_per_day: float

    average_demand_m3_per_day: float

    peak_demand_m3_per_day: float

    dry_season_supply_m3_per_day: Optional[float] = None

    dry_season_demand_m3_per_day: Optional[float] = None

    annual_supply_m3: Optional[float] = None

    annual_demand_m3: Optional[float] = None

    seasonal_reliability: Optional[str] = None

    data_completeness: Optional[str] = None

    source_count: int = 1


# ============================================================
# RESULT MODEL
# ============================================================


@dataclass
class WaterSupplyDemandAssessment:
    """
    Complete water supply-demand assessment.
    """

    valid_input: bool

    sustainable_supply_m3_per_day: float

    average_demand_m3_per_day: float

    peak_demand_m3_per_day: float

    dry_season_supply_m3_per_day: Number

    dry_season_demand_m3_per_day: Number

    daily_surplus_m3: Number

    daily_deficit_m3: Number

    peak_surplus_m3: Number

    peak_deficit_m3: Number

    dry_season_surplus_m3: Number

    dry_season_deficit_m3: Number

    supply_demand_ratio: Number

    peak_supply_coverage_ratio: Number

    dry_season_coverage_ratio: Number

    annual_supply_m3: Number

    annual_demand_m3: Number

    annual_surplus_m3: Number

    annual_deficit_m3: Number

    average_supply_coverage_percent: Number

    peak_supply_coverage_percent: Number

    dry_season_coverage_percent: Number

    water_stress_category: str

    peak_stress_category: str

    dry_season_stress_category: str

    seasonal_reliability: Optional[str]

    data_completeness: Optional[str]

    source_count: int

    concerns: List[str]

    warnings: List[str]

    recommendations: List[str]

    summary: str


# ============================================================
# THRESHOLDS
# ============================================================


class WaterBalanceThresholds:
    """
    Preliminary screening thresholds.

    These are analytical thresholds, not regulatory standards.
    """

    VERY_LOW_COVERAGE: float = 0.50

    LOW_COVERAGE: float = 0.75

    MODERATE_COVERAGE: float = 1.00

    HIGH_COVERAGE: float = 1.25

    VERY_HIGH_COVERAGE: float = 1.50


# ============================================================
# MODEL
# ============================================================


class WaterSupplyDemandModel:
    """
    Compare sustainable water supply against data-center demand.
    """

    def __init__(
        self,
        thresholds: Optional[WaterBalanceThresholds] = None,
    ) -> None:

        self.thresholds = (
            thresholds
            if thresholds is not None
            else WaterBalanceThresholds()
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def validate_input(
        data: WaterSupplyDemandInput,
    ) -> List[str]:
        """
        Validate model inputs.
        """

        errors: List[str] = []

        if data.sustainable_supply_m3_per_day < 0:
            errors.append(
                "sustainable_supply_m3_per_day "
                "cannot be negative."
            )

        if data.average_demand_m3_per_day < 0:
            errors.append(
                "average_demand_m3_per_day "
                "cannot be negative."
            )

        if data.peak_demand_m3_per_day < 0:
            errors.append(
                "peak_demand_m3_per_day "
                "cannot be negative."
            )

        if (
            data.peak_demand_m3_per_day
            < data.average_demand_m3_per_day
        ):
            errors.append(
                "peak_demand_m3_per_day cannot be "
                "less than average_demand_m3_per_day."
            )

        if (
            data.dry_season_supply_m3_per_day is not None
            and data.dry_season_supply_m3_per_day < 0
        ):
            errors.append(
                "dry_season_supply_m3_per_day "
                "cannot be negative."
            )

        if (
            data.dry_season_demand_m3_per_day is not None
            and data.dry_season_demand_m3_per_day < 0
        ):
            errors.append(
                "dry_season_demand_m3_per_day "
                "cannot be negative."
            )

        if (
            data.annual_supply_m3 is not None
            and data.annual_supply_m3 < 0
        ):
            errors.append(
                "annual_supply_m3 cannot be negative."
            )

        if (
            data.annual_demand_m3 is not None
            and data.annual_demand_m3 < 0
        ):
            errors.append(
                "annual_demand_m3 cannot be negative."
            )

        if data.source_count < 0:
            errors.append(
                "source_count cannot be negative."
            )

        return errors

    # ========================================================
    # BALANCE
    # ========================================================

    @staticmethod
    def calculate_balance(
        supply: float,
        demand: float,
    ) -> float:
        """
        Calculate supply minus demand.

        Positive:
            surplus

        Negative:
            deficit
        """

        return supply - demand

    # ========================================================
    # SURPLUS
    # ========================================================

    @staticmethod
    def calculate_surplus(
        supply: float,
        demand: float,
    ) -> float:
        """
        Return only positive surplus.
        """

        balance = supply - demand

        return max(balance, 0.0)

    # ========================================================
    # DEFICIT
    # ========================================================

    @staticmethod
    def calculate_deficit(
        supply: float,
        demand: float,
    ) -> float:
        """
        Return only positive deficit.
        """

        balance = supply - demand

        return max(-balance, 0.0)

    # ========================================================
    # COVERAGE RATIO
    # ========================================================

    @staticmethod
    def coverage_ratio(
        supply: float,
        demand: float,
    ) -> Number:
        """
        Calculate:

            supply / demand
        """

        if demand <= 0:
            return None

        return supply / demand

    # ========================================================
    # COVERAGE PERCENT
    # ========================================================

    @staticmethod
    def coverage_percent(
        supply: float,
        demand: float,
    ) -> Number:
        """
        Calculate supply coverage percentage.
        """

        ratio = WaterSupplyDemandModel.coverage_ratio(
            supply,
            demand,
        )

        if ratio is None:
            return None

        return ratio * 100.0

    # ========================================================
    # STRESS CATEGORY
    # ========================================================

    def stress_category(
        self,
        coverage_ratio: Number,
    ) -> str:
        """
        Convert coverage ratio into a screening category.
        """

        if coverage_ratio is None:
            return "no_demand"

        if (
            coverage_ratio
            < self.thresholds.VERY_LOW_COVERAGE
        ):
            return "critical"

        if (
            coverage_ratio
            < self.thresholds.LOW_COVERAGE
        ):
            return "high"

        if (
            coverage_ratio
            < self.thresholds.MODERATE_COVERAGE
        ):
            return "moderate"

        if (
            coverage_ratio
            < self.thresholds.HIGH_COVERAGE
        ):
            return "low"

        if (
            coverage_ratio
            < self.thresholds.VERY_HIGH_COVERAGE
        ):
            return "comfortable"

        return "high_surplus"

    # ========================================================
    # ANNUAL BALANCE
    # ========================================================

    @staticmethod
    def annual_balance(
        annual_supply_m3: Optional[float],
        annual_demand_m3: Optional[float],
    ) -> Number:
        """
        Calculate annual supply-demand balance.
        """

        if (
            annual_supply_m3 is None
            or annual_demand_m3 is None
        ):
            return None

        return annual_supply_m3 - annual_demand_m3

    # ========================================================
    # ANNUAL SURPLUS
    # ========================================================

    @staticmethod
    def annual_surplus(
        annual_supply_m3: Optional[float],
        annual_demand_m3: Optional[float],
    ) -> Number:
        """
        Calculate annual surplus.
        """

        if (
            annual_supply_m3 is None
            or annual_demand_m3 is None
        ):
            return None

        return max(
            annual_supply_m3 - annual_demand_m3,
            0.0,
        )

    # ========================================================
    # ANNUAL DEFICIT
    # ========================================================

    @staticmethod
    def annual_deficit(
        annual_supply_m3: Optional[float],
        annual_demand_m3: Optional[float],
    ) -> Number:
        """
        Calculate annual deficit.
        """

        if (
            annual_supply_m3 is None
            or annual_demand_m3 is None
        ):
            return None

        return max(
            annual_demand_m3 - annual_supply_m3,
            0.0,
        )

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(
        self,
        data: WaterSupplyDemandInput,
    ) -> WaterSupplyDemandAssessment:
        """
        Generate complete water supply-demand assessment.
        """

        errors = self.validate_input(data)

        if errors:
            return self.invalid_result(
                data=data,
                errors=errors,
            )

        # ----------------------------------------------------
        # AVERAGE SUPPLY VS DEMAND
        # ----------------------------------------------------

        daily_surplus = self.calculate_surplus(
            supply=data.sustainable_supply_m3_per_day,
            demand=data.average_demand_m3_per_day,
        )

        daily_deficit = self.calculate_deficit(
            supply=data.sustainable_supply_m3_per_day,
            demand=data.average_demand_m3_per_day,
        )

        supply_demand_ratio = self.coverage_ratio(
            supply=data.sustainable_supply_m3_per_day,
            demand=data.average_demand_m3_per_day,
        )

        average_coverage_percent = self.coverage_percent(
            supply=data.sustainable_supply_m3_per_day,
            demand=data.average_demand_m3_per_day,
        )

        # ----------------------------------------------------
        # PEAK SUPPLY VS DEMAND
        # ----------------------------------------------------

        peak_surplus = self.calculate_surplus(
            supply=data.sustainable_supply_m3_per_day,
            demand=data.peak_demand_m3_per_day,
        )

        peak_deficit = self.calculate_deficit(
            supply=data.sustainable_supply_m3_per_day,
            demand=data.peak_demand_m3_per_day,
        )

        peak_coverage_ratio = self.coverage_ratio(
            supply=data.sustainable_supply_m3_per_day,
            demand=data.peak_demand_m3_per_day,
        )

        peak_coverage_percent = self.coverage_percent(
            supply=data.sustainable_supply_m3_per_day,
            demand=data.peak_demand_m3_per_day,
        )

        # ----------------------------------------------------
        # DRY-SEASON SUPPLY VS DEMAND
        # ----------------------------------------------------

        dry_supply = data.dry_season_supply_m3_per_day

        dry_demand = data.dry_season_demand_m3_per_day

        if (
            dry_supply is not None
            and dry_demand is not None
        ):

            dry_surplus: Number = (
                self.calculate_surplus(
                    supply=dry_supply,
                    demand=dry_demand,
                )
            )

            dry_deficit: Number = (
                self.calculate_deficit(
                    supply=dry_supply,
                    demand=dry_demand,
                )
            )

            dry_coverage_ratio: Number = (
                self.coverage_ratio(
                    supply=dry_supply,
                    demand=dry_demand,
                )
            )

            dry_coverage_percent: Number = (
                self.coverage_percent(
                    supply=dry_supply,
                    demand=dry_demand,
                )
            )

        else:

            dry_surplus = None
            dry_deficit = None
            dry_coverage_ratio = None
            dry_coverage_percent = None

        # ----------------------------------------------------
        # ANNUAL BALANCE
        # ----------------------------------------------------

        annual_surplus = self.annual_surplus(
            annual_supply_m3=data.annual_supply_m3,
            annual_demand_m3=data.annual_demand_m3,
        )

        annual_deficit = self.annual_deficit(
            annual_supply_m3=data.annual_supply_m3,
            annual_demand_m3=data.annual_demand_m3,
        )

        # ----------------------------------------------------
        # STRESS CATEGORIES
        # ----------------------------------------------------

        water_stress = self.stress_category(
            supply_demand_ratio,
        )

        peak_stress = self.stress_category(
            peak_coverage_ratio,
        )

        dry_stress = self.stress_category(
            dry_coverage_ratio,
        )

        # ----------------------------------------------------
        # CONCERNS
        # ----------------------------------------------------

        concerns: List[str] = []

        warnings: List[str] = []

        recommendations: List[str] = []

        # Average water stress

        if water_stress == "critical":

            concerns.append(
                "critical_average_water_deficit"
            )

        elif water_stress == "high":

            concerns.append(
                "high_average_water_stress"
            )

        elif water_stress == "moderate":

            concerns.append(
                "moderate_average_water_stress"
            )

        # Peak water stress

        if peak_stress in {
            "critical",
            "high",
        }:

            concerns.append(
                "peak_demand_exceeds_available_supply"
            )

            recommendations.append(
                "Evaluate additional storage, "
                "supplementary supply, or water "
                "demand-reduction measures."
            )

        # Dry-season stress

        if dry_stress == "critical":

            concerns.append(
                "critical_dry_season_water_deficit"
            )

            recommendations.append(
                "Evaluate dry-season storage, "
                "alternative permitted sources, "
                "water reuse, or demand reduction."
            )

        elif dry_stress == "high":

            concerns.append(
                "high_dry_season_water_stress"
            )

        # Seasonal reliability

        if data.seasonal_reliability in {
            "low",
            "very_low",
        }:

            concerns.append(
                "low_seasonal_water_reliability"
            )

            recommendations.append(
                "Evaluate seasonal supply rather than "
                "relying only on annual averages."
            )

        # Data completeness

        if data.data_completeness in {
            "low",
            "very_low",
        }:

            warnings.append(
                "Water-supply observations have "
                "limited data completeness."
            )

        # Source count

        if data.source_count <= 0:

            warnings.append(
                "No water source has been identified."
            )

        elif data.source_count == 1:

            warnings.append(
                "The assessment currently relies on "
                "one identified water source."
            )

            recommendations.append(
                "Evaluate source diversification and "
                "backup water-supply options."
            )

        # Annual information

        if (
            data.annual_supply_m3 is None
            or data.annual_demand_m3 is None
        ):

            warnings.append(
                "Annual supply or demand data was not "
                "provided; annual balance is unavailable."
            )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary = self.generate_summary(
            supply=data.sustainable_supply_m3_per_day,
            average_demand=data.average_demand_m3_per_day,
            peak_demand=data.peak_demand_m3_per_day,
            ratio=supply_demand_ratio,
            water_stress=water_stress,
            peak_stress=peak_stress,
            dry_stress=dry_stress,
        )

        return WaterSupplyDemandAssessment(

            valid_input=True,

            sustainable_supply_m3_per_day=(
                data.sustainable_supply_m3_per_day
            ),

            average_demand_m3_per_day=(
                data.average_demand_m3_per_day
            ),

            peak_demand_m3_per_day=(
                data.peak_demand_m3_per_day
            ),

            dry_season_supply_m3_per_day=dry_supply,

            dry_season_demand_m3_per_day=dry_demand,

            daily_surplus_m3=daily_surplus,

            daily_deficit_m3=daily_deficit,

            peak_surplus_m3=peak_surplus,

            peak_deficit_m3=peak_deficit,

            dry_season_surplus_m3=dry_surplus,

            dry_season_deficit_m3=dry_deficit,

            supply_demand_ratio=supply_demand_ratio,

            peak_supply_coverage_ratio=(
                peak_coverage_ratio
            ),

            dry_season_coverage_ratio=(
                dry_coverage_ratio
            ),

            annual_supply_m3=(
                data.annual_supply_m3
            ),

            annual_demand_m3=(
                data.annual_demand_m3
            ),

            annual_surplus_m3=annual_surplus,

            annual_deficit_m3=annual_deficit,

            average_supply_coverage_percent=(
                average_coverage_percent
            ),

            peak_supply_coverage_percent=(
                peak_coverage_percent
            ),

            dry_season_coverage_percent=(
                dry_coverage_percent
            ),

            water_stress_category=water_stress,

            peak_stress_category=peak_stress,

            dry_season_stress_category=dry_stress,

            seasonal_reliability=(
                data.seasonal_reliability
            ),

            data_completeness=(
                data.data_completeness
            ),

            source_count=data.source_count,

            concerns=concerns,

            warnings=warnings,

            recommendations=recommendations,

            summary=summary,
        )

    # ========================================================
    # INVALID RESULT
    # ========================================================

    @staticmethod
    def invalid_result(
        data: WaterSupplyDemandInput,
        errors: List[str],
    ) -> WaterSupplyDemandAssessment:
        """
        Return a safe result when input validation fails.
        """

        return WaterSupplyDemandAssessment(

            valid_input=False,

            sustainable_supply_m3_per_day=(
                data.sustainable_supply_m3_per_day
            ),

            average_demand_m3_per_day=(
                data.average_demand_m3_per_day
            ),

            peak_demand_m3_per_day=(
                data.peak_demand_m3_per_day
            ),

            dry_season_supply_m3_per_day=(
                data.dry_season_supply_m3_per_day
            ),

            dry_season_demand_m3_per_day=(
                data.dry_season_demand_m3_per_day
            ),

            daily_surplus_m3=None,

            daily_deficit_m3=None,

            peak_surplus_m3=None,

            peak_deficit_m3=None,

            dry_season_surplus_m3=None,

            dry_season_deficit_m3=None,

            supply_demand_ratio=None,

            peak_supply_coverage_ratio=None,

            dry_season_coverage_ratio=None,

            annual_supply_m3=data.annual_supply_m3,

            annual_demand_m3=data.annual_demand_m3,

            annual_surplus_m3=None,

            annual_deficit_m3=None,

            average_supply_coverage_percent=None,

            peak_supply_coverage_percent=None,

            dry_season_coverage_percent=None,

            water_stress_category="invalid",

            peak_stress_category="invalid",

            dry_season_stress_category="invalid",

            seasonal_reliability=(
                data.seasonal_reliability
            ),

            data_completeness=(
                data.data_completeness
            ),

            source_count=data.source_count,

            concerns=[
                "invalid_input",
            ],

            warnings=errors,

            recommendations=[],

            summary=(
                "Water supply-demand analysis could "
                "not be completed because the input "
                "data is invalid."
            ),
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def generate_summary(
        supply: float,
        average_demand: float,
        peak_demand: float,
        ratio: Number,
        water_stress: str,
        peak_stress: str,
        dry_stress: str,
    ) -> str:
        """
        Generate a human-readable assessment summary.
        """

        if ratio is None:

            ratio_text = "unknown"

        else:

            ratio_text = f"{ratio:.2f}"

        return (
            f"The site has an estimated sustainable "
            f"water supply of {supply:.2f} m³/day "
            f"against an average data-center demand "
            f"of {average_demand:.2f} m³/day and peak "
            f"demand of {peak_demand:.2f} m³/day. "
            f"The average supply-demand ratio is "
            f"{ratio_text}. The preliminary average "
            f"water-stress category is "
            f"'{water_stress}', peak stress is "
            f"'{peak_stress}', and dry-season stress "
            f"is '{dry_stress}'."
        )


# ============================================================
# PUBLIC API
# ============================================================


def analyze_water_supply_demand(
    data: WaterSupplyDemandInput,
) -> Dict[str, Any]:
    """
    Public service-layer function.

    Returns:
        Dictionary suitable for an API response.
    """

    model = WaterSupplyDemandModel()

    result = model.analyze(data)

    return asdict(result)


# ============================================================
# DEVELOPMENT TEST
# ============================================================


if __name__ == "__main__":

    import json

    sample_input = WaterSupplyDemandInput(

        sustainable_supply_m3_per_day=3000.0,

        average_demand_m3_per_day=1200.0,

        peak_demand_m3_per_day=1500.0,

        dry_season_supply_m3_per_day=1800.0,

        dry_season_demand_m3_per_day=1200.0,

        annual_supply_m3=1095000.0,

        annual_demand_m3=438000.0,

        seasonal_reliability="moderate",

        data_completeness="high",

        source_count=2,
    )

    model = WaterSupplyDemandModel()

    result = model.analyze(
        sample_input
    )

    print(
        json.dumps(
            asdict(result),
            indent=2,
            ensure_ascii=False,
        )
    )