"""
India AI Grid
Water Storage and Resilience Model

File:
    backend/models/site_assessment/water/water_storage.py

Purpose:
    Evaluate whether a proposed data-center site has enough
    water storage to handle temporary supply interruptions.

The model evaluates:

    - Storage capacity
    - Normal operating demand
    - Peak demand
    - Emergency reserve
    - Storage autonomy
    - Recommended storage
    - Storage deficit
    - Resilience category

IMPORTANT:
    This is a preliminary site-screening model.

    It does not determine:
        - regulatory storage requirements
        - fire-code requirements
        - engineering design requirements
        - structural requirements
        - legally mandated emergency reserves

    Those should be handled by the appropriate engineering
    and regulatory layers.
"""


from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


Number = Optional[float]


# ============================================================
# INPUT MODEL
# ============================================================


@dataclass
class WaterStorageInput:
    """
    Input values for water-storage analysis.

    Units:

        storage -> m3
        demand  -> m3/day

    storage_capacity_m3:
        Total usable water-storage capacity.

    average_demand_m3_per_day:
        Expected normal operating demand.

    peak_demand_m3_per_day:
        Maximum expected operating demand.

    emergency_reserve_days:
        Desired number of days of emergency autonomy.

    minimum_operating_reserve_m3:
        Optional fixed reserve that should remain untouched.

    existing_backup_supply_m3_per_day:
        Optional additional supply available during
        interruptions.
    """

    storage_capacity_m3: float

    average_demand_m3_per_day: float

    peak_demand_m3_per_day: float

    emergency_reserve_days: float = 1.0

    minimum_operating_reserve_m3: float = 0.0

    existing_backup_supply_m3_per_day: float = 0.0


# ============================================================
# RESULT MODEL
# ============================================================


@dataclass
class WaterStorageAssessment:
    """
    Complete water-storage assessment.
    """

    valid_input: bool

    storage_capacity_m3: float

    average_demand_m3_per_day: float

    peak_demand_m3_per_day: float

    emergency_reserve_days: float

    minimum_operating_reserve_m3: float

    existing_backup_supply_m3_per_day: float

    usable_storage_m3: float

    average_storage_autonomy_days: Number

    peak_storage_autonomy_days: Number

    required_emergency_storage_m3: float

    recommended_storage_m3: float

    storage_surplus_m3: float

    storage_deficit_m3: float

    average_autonomy_coverage_percent: Number

    peak_autonomy_coverage_percent: Number

    resilience_category: str

    concerns: List[str]

    warnings: List[str]

    recommendations: List[str]

    summary: str


# ============================================================
# THRESHOLDS
# ============================================================


class WaterStorageThresholds:
    """
    Preliminary resilience thresholds.

    These are screening thresholds and are not engineering
    standards.
    """

    CRITICAL_AUTONOMY_DAYS = 0.5

    LOW_AUTONOMY_DAYS = 1.0

    MODERATE_AUTONOMY_DAYS = 2.0

    GOOD_AUTONOMY_DAYS = 3.0

    HIGH_AUTONOMY_DAYS = 7.0


# ============================================================
# MODEL
# ============================================================


class WaterStorageModel:
    """
    Evaluate storage capacity and water autonomy.
    """

    def __init__(
        self,
        thresholds: Optional[WaterStorageThresholds] = None,
    ) -> None:

        self.thresholds = (
            thresholds
            if thresholds is not None
            else WaterStorageThresholds()
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def validate_input(
        data: WaterStorageInput,
    ) -> List[str]:
        """
        Validate storage inputs.
        """

        errors: List[str] = []

        if data.storage_capacity_m3 < 0:

            errors.append(
                "storage_capacity_m3 cannot be negative."
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

        if data.emergency_reserve_days < 0:

            errors.append(
                "emergency_reserve_days "
                "cannot be negative."
            )

        if data.minimum_operating_reserve_m3 < 0:

            errors.append(
                "minimum_operating_reserve_m3 "
                "cannot be negative."
            )

        if data.existing_backup_supply_m3_per_day < 0:

            errors.append(
                "existing_backup_supply_m3_per_day "
                "cannot be negative."
            )

        return errors

    # ========================================================
    # USABLE STORAGE
    # ========================================================

    @staticmethod
    def calculate_usable_storage(
        storage_capacity_m3: float,
        minimum_operating_reserve_m3: float,
    ) -> float:
        """
        Calculate storage that can actually be consumed.

        Example:

            total storage = 5000 m3
            reserve       = 1000 m3

            usable storage = 4000 m3
        """

        return max(
            storage_capacity_m3
            - minimum_operating_reserve_m3,
            0.0,
        )

    # ========================================================
    # AUTONOMY
    # ========================================================

    @staticmethod
    def calculate_autonomy_days(
        usable_storage_m3: float,
        demand_m3_per_day: float,
    ) -> Number:
        """
        Calculate how many days the available storage can
        support the site.
        """

        if demand_m3_per_day <= 0:

            return None

        return (
            usable_storage_m3
            / demand_m3_per_day
        )

    # ========================================================
    # REQUIRED STORAGE
    # ========================================================

    @staticmethod
    def calculate_required_storage(
        demand_m3_per_day: float,
        reserve_days: float,
    ) -> float:
        """
        Calculate storage required for the requested
        emergency-reserve duration.
        """

        return (
            demand_m3_per_day
            * reserve_days
        )

    # ========================================================
    # STORAGE SURPLUS
    # ========================================================

    @staticmethod
    def calculate_storage_surplus(
        usable_storage_m3: float,
        required_storage_m3: float,
    ) -> float:
        """
        Calculate storage above the required reserve.
        """

        return max(
            usable_storage_m3
            - required_storage_m3,
            0.0,
        )

    # ========================================================
    # STORAGE DEFICIT
    # ========================================================

    @staticmethod
    def calculate_storage_deficit(
        usable_storage_m3: float,
        required_storage_m3: float,
    ) -> float:
        """
        Calculate storage shortfall.
        """

        return max(
            required_storage_m3
            - usable_storage_m3,
            0.0,
        )

    # ========================================================
    # COVERAGE
    # ========================================================

    @staticmethod
    def calculate_coverage_percent(
        autonomy_days: Number,
        required_days: float,
    ) -> Number:
        """
        Calculate autonomy coverage as a percentage.
        """

        if (
            autonomy_days is None
            or required_days <= 0
        ):

            return None

        return (
            autonomy_days
            / required_days
        ) * 100.0

    # ========================================================
    # RESILIENCE CATEGORY
    # ========================================================

    def classify_resilience(
        self,
        autonomy_days: Number,
    ) -> str:
        """
        Classify water-storage resilience.
        """

        if autonomy_days is None:

            return "no_demand"

        if (
            autonomy_days
            < self.thresholds.CRITICAL_AUTONOMY_DAYS
        ):

            return "critical"

        if (
            autonomy_days
            < self.thresholds.LOW_AUTONOMY_DAYS
        ):

            return "low"

        if (
            autonomy_days
            < self.thresholds.MODERATE_AUTONOMY_DAYS
        ):

            return "moderate"

        if (
            autonomy_days
            < self.thresholds.GOOD_AUTONOMY_DAYS
        ):

            return "good"

        if (
            autonomy_days
            < self.thresholds.HIGH_AUTONOMY_DAYS
        ):

            return "high"

        return "very_high"

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(
        self,
        data: WaterStorageInput,
    ) -> WaterStorageAssessment:
        """
        Perform complete storage assessment.
        """

        errors = self.validate_input(data)

        if errors:

            return self.invalid_result(
                data,
                errors,
            )

        # ----------------------------------------------------
        # USABLE STORAGE
        # ----------------------------------------------------

        usable_storage = (
            self.calculate_usable_storage(
                storage_capacity_m3=(
                    data.storage_capacity_m3
                ),
                minimum_operating_reserve_m3=(
                    data.minimum_operating_reserve_m3
                ),
            )
        )

        # ----------------------------------------------------
        # AVERAGE AUTONOMY
        # ----------------------------------------------------

        average_autonomy = (
            self.calculate_autonomy_days(
                usable_storage_m3=usable_storage,
                demand_m3_per_day=(
                    data.average_demand_m3_per_day
                ),
            )
        )

        # ----------------------------------------------------
        # PEAK AUTONOMY
        # ----------------------------------------------------

        peak_autonomy = (
            self.calculate_autonomy_days(
                usable_storage_m3=usable_storage,
                demand_m3_per_day=(
                    data.peak_demand_m3_per_day
                ),
            )
        )

        # ----------------------------------------------------
        # REQUIRED EMERGENCY STORAGE
        # ----------------------------------------------------

        required_emergency_storage = (
            self.calculate_required_storage(
                demand_m3_per_day=(
                    data.peak_demand_m3_per_day
                ),
                reserve_days=(
                    data.emergency_reserve_days
                ),
            )
        )

        # ----------------------------------------------------
        # STORAGE BALANCE
        # ----------------------------------------------------

        storage_surplus = (
            self.calculate_storage_surplus(
                usable_storage_m3=usable_storage,
                required_storage_m3=(
                    required_emergency_storage
                ),
            )
        )

        storage_deficit = (
            self.calculate_storage_deficit(
                usable_storage_m3=usable_storage,
                required_storage_m3=(
                    required_emergency_storage
                ),
            )
        )

        # ----------------------------------------------------
        # RECOMMENDED STORAGE
        # ----------------------------------------------------

        recommended_storage = (
            required_emergency_storage
            + data.minimum_operating_reserve_m3
        )

        # ----------------------------------------------------
        # COVERAGE
        # ----------------------------------------------------

        average_coverage = (
            self.calculate_coverage_percent(
                autonomy_days=average_autonomy,
                required_days=(
                    data.emergency_reserve_days
                ),
            )
        )

        peak_coverage = (
            self.calculate_coverage_percent(
                autonomy_days=peak_autonomy,
                required_days=(
                    data.emergency_reserve_days
                ),
            )
        )

        # ----------------------------------------------------
        # RESILIENCE
        # ----------------------------------------------------

        resilience = self.classify_resilience(
            peak_autonomy,
        )

        # ----------------------------------------------------
        # CONCERNS
        # ----------------------------------------------------

        concerns: List[str] = []

        warnings: List[str] = []

        recommendations: List[str] = []

        # ----------------------------------------------------
        # STORAGE DEFICIT
        # ----------------------------------------------------

        if storage_deficit > 0:

            concerns.append(
                "insufficient_emergency_storage"
            )

            recommendations.append(
                "Increase usable water-storage "
                "capacity to meet the requested "
                "emergency reserve."
            )

        # ----------------------------------------------------
        # PEAK AUTONOMY
        # ----------------------------------------------------

        if resilience == "critical":

            concerns.append(
                "critical_peak_water_autonomy"
            )

            recommendations.append(
                "Provide additional storage or "
                "a reliable backup water source."
            )

        elif resilience == "low":

            concerns.append(
                "low_peak_water_autonomy"
            )

            recommendations.append(
                "Evaluate additional storage to "
                "improve interruption resilience."
            )

        elif resilience == "moderate":

            warnings.append(
                "Peak-demand water autonomy is "
                "limited."
            )

        # ----------------------------------------------------
        # ZERO STORAGE
        # ----------------------------------------------------

        if data.storage_capacity_m3 == 0:

            concerns.append(
                "no_water_storage_capacity"
            )

            recommendations.append(
                "Provide dedicated water-storage "
                "infrastructure."
            )

        # ----------------------------------------------------
        # BACKUP SUPPLY
        # ----------------------------------------------------

        if data.existing_backup_supply_m3_per_day <= 0:

            warnings.append(
                "No backup water supply was included "
                "in the assessment."
            )

            recommendations.append(
                "Evaluate a secondary permitted water "
                "source or other continuity mechanism."
            )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary = self.generate_summary(
            storage=(
                data.storage_capacity_m3
            ),
            usable_storage=usable_storage,
            average_autonomy=average_autonomy,
            peak_autonomy=peak_autonomy,
            required_storage=(
                required_emergency_storage
            ),
            resilience=resilience,
        )

        return WaterStorageAssessment(

            valid_input=True,

            storage_capacity_m3=(
                data.storage_capacity_m3
            ),

            average_demand_m3_per_day=(
                data.average_demand_m3_per_day
            ),

            peak_demand_m3_per_day=(
                data.peak_demand_m3_per_day
            ),

            emergency_reserve_days=(
                data.emergency_reserve_days
            ),

            minimum_operating_reserve_m3=(
                data.minimum_operating_reserve_m3
            ),

            existing_backup_supply_m3_per_day=(
                data.existing_backup_supply_m3_per_day
            ),

            usable_storage_m3=usable_storage,

            average_storage_autonomy_days=(
                average_autonomy
            ),

            peak_storage_autonomy_days=(
                peak_autonomy
            ),

            required_emergency_storage_m3=(
                required_emergency_storage
            ),

            recommended_storage_m3=(
                recommended_storage
            ),

            storage_surplus_m3=(
                storage_surplus
            ),

            storage_deficit_m3=(
                storage_deficit
            ),

            average_autonomy_coverage_percent=(
                average_coverage
            ),

            peak_autonomy_coverage_percent=(
                peak_coverage
            ),

            resilience_category=resilience,

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
        data: WaterStorageInput,
        errors: List[str],
    ) -> WaterStorageAssessment:
        """
        Return a safe result when input validation fails.
        """

        return WaterStorageAssessment(

            valid_input=False,

            storage_capacity_m3=(
                data.storage_capacity_m3
            ),

            average_demand_m3_per_day=(
                data.average_demand_m3_per_day
            ),

            peak_demand_m3_per_day=(
                data.peak_demand_m3_per_day
            ),

            emergency_reserve_days=(
                data.emergency_reserve_days
            ),

            minimum_operating_reserve_m3=(
                data.minimum_operating_reserve_m3
            ),

            existing_backup_supply_m3_per_day=(
                data.existing_backup_supply_m3_per_day
            ),

            usable_storage_m3=0.0,

            average_storage_autonomy_days=None,

            peak_storage_autonomy_days=None,

            required_emergency_storage_m3=0.0,

            recommended_storage_m3=0.0,

            storage_surplus_m3=0.0,

            storage_deficit_m3=0.0,

            average_autonomy_coverage_percent=None,

            peak_autonomy_coverage_percent=None,

            resilience_category="invalid",

            concerns=[
                "invalid_input",
            ],

            warnings=errors,

            recommendations=[],

            summary=(
                "Water storage analysis could not "
                "be completed because the input "
                "data is invalid."
            ),
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def generate_summary(
        storage: float,
        usable_storage: float,
        average_autonomy: Number,
        peak_autonomy: Number,
        required_storage: float,
        resilience: str,
    ) -> str:
        """
        Generate human-readable summary.
        """

        if average_autonomy is None:

            average_text = "unknown"

        else:

            average_text = (
                f"{average_autonomy:.2f}"
            )

        if peak_autonomy is None:

            peak_text = "unknown"

        else:

            peak_text = (
                f"{peak_autonomy:.2f}"
            )

        return (
            f"The site has {storage:.2f} m³ of total "
            f"storage, of which {usable_storage:.2f} m³ "
            f"is considered usable. Storage provides "
            f"approximately {average_text} days of "
            f"average-demand autonomy and "
            f"{peak_text} days of peak-demand "
            f"autonomy. The calculated emergency "
            f"storage requirement is "
            f"{required_storage:.2f} m³. The "
            f"preliminary storage-resilience category "
            f"is '{resilience}'."
        )


# ============================================================
# PUBLIC API
# ============================================================


def analyze_water_storage(
    data: WaterStorageInput,
) -> Dict[str, Any]:
    """
    Public service-layer function.

    Returns:
        Dictionary suitable for an API response.
    """

    model = WaterStorageModel()

    result = model.analyze(data)

    return asdict(result)


# ============================================================
# DEVELOPMENT TEST
# ============================================================


if __name__ == "__main__":

    import json

    sample_input = WaterStorageInput(

        storage_capacity_m3=5000.0,

        average_demand_m3_per_day=1200.0,

        peak_demand_m3_per_day=1500.0,

        emergency_reserve_days=2.0,

        minimum_operating_reserve_m3=500.0,

        existing_backup_supply_m3_per_day=300.0,
    )

    model = WaterStorageModel()

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