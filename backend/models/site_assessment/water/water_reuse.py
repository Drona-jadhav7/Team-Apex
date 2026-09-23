"""
India AI Grid
Water Reuse and Recycling Model

File:
    backend/models/site_assessment/water/water_reuse.py

Purpose:
    Estimate how much freshwater demand can be reduced through
    water recycling and reuse in a data-center facility.

The model considers:

    - Total water demand
    - Cooling-water demand
    - Reuse percentage
    - Recycling efficiency
    - Reuse losses
    - Freshwater savings
    - Reused-water volume
    - Net freshwater demand
    - Reuse-system capacity
    - Reuse potential
    - Water-reuse category

IMPORTANT:
    This is a preliminary planning model.

    It does not establish:
        - water-treatment requirements
        - discharge permissions
        - health/safety compliance
        - cooling-system engineering requirements
        - regulatory reuse limits
        - water-quality specifications

    Those requirements should be handled by the appropriate
    engineering and regulatory models.
"""


from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


# ============================================================
# TYPE ALIAS
# ============================================================

Number = float


# ============================================================
# INPUT MODEL
# ============================================================


@dataclass
class WaterReuseInput:
    """
    Input data for water-reuse analysis.

    Units:

        Water volumes -> m3/day
        Percentages   -> 0 to 100

    total_water_demand_m3_per_day:
        Total water demand of the data center.

    cooling_water_demand_m3_per_day:
        Portion of total demand associated with cooling.

    reuse_percentage:
        Percentage of recoverable water targeted for reuse.

    recycling_efficiency_percent:
        Percentage of collected/recoverable water that can
        successfully be recycled.

    reuse_loss_percentage:
        Expected losses during collection, treatment,
        evaporation, blowdown, leakage, etc.

    reuse_system_capacity_m3_per_day:
        Maximum volume the reuse system can process per day.

    additional_reusable_water_m3_per_day:
        Optional non-cooling water that can be recovered
        and reused.

    minimum_freshwater_requirement_m3_per_day:
        Optional minimum freshwater requirement that cannot
        be replaced through reuse.
    """

    total_water_demand_m3_per_day: float

    cooling_water_demand_m3_per_day: float

    reuse_percentage: float = 0.0

    recycling_efficiency_percent: float = 0.0

    reuse_loss_percentage: float = 0.0

    reuse_system_capacity_m3_per_day: float = 0.0

    additional_reusable_water_m3_per_day: float = 0.0

    minimum_freshwater_requirement_m3_per_day: float = 0.0


# ============================================================
# RESULT MODEL
# ============================================================


@dataclass
class WaterReuseAssessment:
    """
    Complete water-reuse assessment.
    """

    valid_input: bool

    total_water_demand_m3_per_day: float

    cooling_water_demand_m3_per_day: float

    reuse_percentage: float

    recycling_efficiency_percent: float

    reuse_loss_percentage: float

    reuse_system_capacity_m3_per_day: float

    potential_reusable_water_m3_per_day: float

    recoverable_water_m3_per_day: float

    recycled_water_m3_per_day: float

    reuse_losses_m3_per_day: float

    additional_reused_water_m3_per_day: float

    total_reused_water_m3_per_day: float

    freshwater_demand_before_reuse_m3_per_day: float

    freshwater_demand_after_reuse_m3_per_day: float

    freshwater_savings_m3_per_day: float

    freshwater_savings_percent: float

    reuse_system_utilization_percent: float

    reuse_coverage_percent: float

    reuse_category: str

    concerns: List[str]

    warnings: List[str]

    recommendations: List[str]

    summary: str


# ============================================================
# THRESHOLDS
# ============================================================


class WaterReuseThresholds:
    """
    Preliminary water-reuse classification thresholds.

    These are analytical thresholds and are not regulatory
    standards.
    """

    LOW_REUSE_PERCENT = 10.0

    MODERATE_REUSE_PERCENT = 30.0

    GOOD_REUSE_PERCENT = 50.0

    HIGH_REUSE_PERCENT = 70.0

    VERY_HIGH_REUSE_PERCENT = 90.0


# ============================================================
# MODEL
# ============================================================


class WaterReuseModel:
    """
    Estimate freshwater savings from water reuse.
    """

    def __init__(
        self,
        thresholds: WaterReuseThresholds | None = None,
    ) -> None:

        self.thresholds = (
            thresholds
            if thresholds is not None
            else WaterReuseThresholds()
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def validate_input(
        data: WaterReuseInput,
    ) -> List[str]:
        """
        Validate reuse-model inputs.
        """

        errors: List[str] = []

        if data.total_water_demand_m3_per_day < 0:

            errors.append(
                "total_water_demand_m3_per_day "
                "cannot be negative."
            )

        if data.cooling_water_demand_m3_per_day < 0:

            errors.append(
                "cooling_water_demand_m3_per_day "
                "cannot be negative."
            )

        if (
            data.cooling_water_demand_m3_per_day
            > data.total_water_demand_m3_per_day
        ):

            errors.append(
                "cooling_water_demand_m3_per_day "
                "cannot exceed total_water_demand_m3_per_day."
            )

        if not 0 <= data.reuse_percentage <= 100:

            errors.append(
                "reuse_percentage must be between "
                "0 and 100."
            )

        if not 0 <= data.recycling_efficiency_percent <= 100:

            errors.append(
                "recycling_efficiency_percent must be "
                "between 0 and 100."
            )

        if not 0 <= data.reuse_loss_percentage <= 100:

            errors.append(
                "reuse_loss_percentage must be "
                "between 0 and 100."
            )

        if data.reuse_system_capacity_m3_per_day < 0:

            errors.append(
                "reuse_system_capacity_m3_per_day "
                "cannot be negative."
            )

        if data.additional_reusable_water_m3_per_day < 0:

            errors.append(
                "additional_reusable_water_m3_per_day "
                "cannot be negative."
            )

        if data.minimum_freshwater_requirement_m3_per_day < 0:

            errors.append(
                "minimum_freshwater_requirement_m3_per_day "
                "cannot be negative."
            )

        if (
            data.minimum_freshwater_requirement_m3_per_day
            > data.total_water_demand_m3_per_day
        ):

            errors.append(
                "minimum_freshwater_requirement_m3_per_day "
                "cannot exceed total water demand."
            )

        return errors

    # ========================================================
    # POTENTIAL REUSABLE WATER
    # ========================================================

    @staticmethod
    def calculate_potential_reusable_water(
        cooling_demand_m3_per_day: float,
        reuse_percentage: float,
    ) -> float:
        """
        Calculate the amount of cooling water targeted
        for recovery/reuse.
        """

        return (
            cooling_demand_m3_per_day
            * reuse_percentage
            / 100.0
        )

    # ========================================================
    # RECOVERABLE WATER
    # ========================================================

    @staticmethod
    def calculate_recoverable_water(
        potential_reusable_water_m3_per_day: float,
        recycling_efficiency_percent: float,
    ) -> float:
        """
        Calculate water successfully recoverable by the
        recycling process.
        """

        return (
            potential_reusable_water_m3_per_day
            * recycling_efficiency_percent
            / 100.0
        )

    # ========================================================
    # REUSE LOSSES
    # ========================================================

    @staticmethod
    def calculate_reuse_losses(
        recoverable_water_m3_per_day: float,
        reuse_loss_percentage: float,
    ) -> float:
        """
        Calculate losses occurring during reuse processing.
        """

        return (
            recoverable_water_m3_per_day
            * reuse_loss_percentage
            / 100.0
        )

    # ========================================================
    # RECYCLED WATER
    # ========================================================

    @staticmethod
    def calculate_recycled_water(
        recoverable_water_m3_per_day: float,
        reuse_loss_percentage: float,
    ) -> float:
        """
        Calculate water actually returned to the facility
        for reuse after processing losses.
        """

        return (
            recoverable_water_m3_per_day
            * (
                1.0
                - reuse_loss_percentage / 100.0
            )
        )

    # ========================================================
    # CAPACITY LIMIT
    # ========================================================

    @staticmethod
    def apply_system_capacity(
        recycled_water_m3_per_day: float,
        system_capacity_m3_per_day: float,
    ) -> float:
        """
        Ensure the actual reused volume does not exceed
        treatment/reuse-system capacity.
        """

        if system_capacity_m3_per_day <= 0:

            return 0.0

        return min(
            recycled_water_m3_per_day,
            system_capacity_m3_per_day,
        )

    # ========================================================
    # FRESHWATER DEMAND
    # ========================================================

    @staticmethod
    def calculate_freshwater_demand(
        total_water_demand_m3_per_day: float,
        total_reused_water_m3_per_day: float,
        minimum_freshwater_requirement_m3_per_day: float,
    ) -> float:
        """
        Calculate net freshwater demand after reuse.
        """

        calculated_demand = max(
            total_water_demand_m3_per_day
            - total_reused_water_m3_per_day,
            0.0,
        )

        return max(
            calculated_demand,
            minimum_freshwater_requirement_m3_per_day,
        )

    # ========================================================
    # CATEGORY
    # ========================================================

    def classify_reuse(
        self,
        savings_percent: float,
    ) -> str:
        """
        Classify freshwater-reduction performance.
        """

        if savings_percent <= 0:

            return "none"

        if (
            savings_percent
            < self.thresholds.LOW_REUSE_PERCENT
        ):

            return "low"

        if (
            savings_percent
            < self.thresholds.MODERATE_REUSE_PERCENT
        ):

            return "moderate"

        if (
            savings_percent
            < self.thresholds.GOOD_REUSE_PERCENT
        ):

            return "good"

        if (
            savings_percent
            < self.thresholds.HIGH_REUSE_PERCENT
        ):

            return "high"

        if (
            savings_percent
            < self.thresholds.VERY_HIGH_REUSE_PERCENT
        ):

            return "very_high"

        return "maximum"

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(
        self,
        data: WaterReuseInput,
    ) -> WaterReuseAssessment:
        """
        Perform complete water-reuse analysis.
        """

        errors = self.validate_input(data)

        if errors:

            return self.invalid_result(
                data,
                errors,
            )

        # ----------------------------------------------------
        # POTENTIAL RECOVERY
        # ----------------------------------------------------

        potential_reusable_water = (
            self.calculate_potential_reusable_water(
                cooling_demand_m3_per_day=(
                    data.cooling_water_demand_m3_per_day
                ),
                reuse_percentage=(
                    data.reuse_percentage
                ),
            )
        )

        # ----------------------------------------------------
        # RECOVERABLE WATER
        # ----------------------------------------------------

        recoverable_water = (
            self.calculate_recoverable_water(
                potential_reusable_water_m3_per_day=(
                    potential_reusable_water
                ),
                recycling_efficiency_percent=(
                    data.recycling_efficiency_percent
                ),
            )
        )

        # ----------------------------------------------------
        # REUSE LOSSES
        # ----------------------------------------------------

        reuse_losses = (
            self.calculate_reuse_losses(
                recoverable_water_m3_per_day=(
                    recoverable_water
                ),
                reuse_loss_percentage=(
                    data.reuse_loss_percentage
                ),
            )
        )

        # ----------------------------------------------------
        # RECYCLED WATER
        # ----------------------------------------------------

        recycled_water = (
            self.calculate_recycled_water(
                recoverable_water_m3_per_day=(
                    recoverable_water
                ),
                reuse_loss_percentage=(
                    data.reuse_loss_percentage
                ),
            )
        )

        # ----------------------------------------------------
        # ADDITIONAL REUSE
        # ----------------------------------------------------

        additional_reused_water = min(
            data.additional_reusable_water_m3_per_day,
            max(
                data.total_water_demand_m3_per_day
                - recycled_water,
                0.0,
            ),
        )

        # ----------------------------------------------------
        # SYSTEM CAPACITY
        # ----------------------------------------------------

        recycled_water_with_capacity = (
            self.apply_system_capacity(
                recycled_water_m3_per_day=(
                    recycled_water
                ),
                system_capacity_m3_per_day=(
                    data.reuse_system_capacity_m3_per_day
                ),
            )
        )

        # ----------------------------------------------------
        # TOTAL REUSED WATER
        # ----------------------------------------------------

        total_reused_water = min(
            recycled_water_with_capacity
            + additional_reused_water,
            data.total_water_demand_m3_per_day,
        )

        # ----------------------------------------------------
        # FRESHWATER DEMAND
        # ----------------------------------------------------

        freshwater_before = (
            data.total_water_demand_m3_per_day
        )

        freshwater_after = (
            self.calculate_freshwater_demand(
                total_water_demand_m3_per_day=(
                    data.total_water_demand_m3_per_day
                ),
                total_reused_water_m3_per_day=(
                    total_reused_water
                ),
                minimum_freshwater_requirement_m3_per_day=(
                    data.minimum_freshwater_requirement_m3_per_day
                ),
            )
        )

        # ----------------------------------------------------
        # FRESHWATER SAVINGS
        # ----------------------------------------------------

        freshwater_savings = max(
            freshwater_before
            - freshwater_after,
            0.0,
        )

        if freshwater_before > 0:

            freshwater_savings_percent = (
                freshwater_savings
                / freshwater_before
                * 100.0
            )

        else:

            freshwater_savings_percent = 0.0

        # ----------------------------------------------------
        # SYSTEM UTILIZATION
        # ----------------------------------------------------

        if data.reuse_system_capacity_m3_per_day > 0:

            system_utilization = (
                total_reused_water
                / data.reuse_system_capacity_m3_per_day
                * 100.0
            )

        else:

            system_utilization = 0.0

        system_utilization = min(
            system_utilization,
            100.0,
        )

        # ----------------------------------------------------
        # REUSE COVERAGE
        # ----------------------------------------------------

        if data.total_water_demand_m3_per_day > 0:

            reuse_coverage = (
                total_reused_water
                / data.total_water_demand_m3_per_day
                * 100.0
            )

        else:

            reuse_coverage = 0.0

        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        reuse_category = self.classify_reuse(
            freshwater_savings_percent,
        )

        # ----------------------------------------------------
        # CONCERNS
        # ----------------------------------------------------

        concerns: List[str] = []

        warnings: List[str] = []

        recommendations: List[str] = []

        # ----------------------------------------------------
        # NO REUSE
        # ----------------------------------------------------

        if total_reused_water <= 0:

            concerns.append(
                "no_water_reuse"
            )

            recommendations.append(
                "Evaluate cooling-water recovery "
                "and recycling opportunities."
            )

        # ----------------------------------------------------
        # LOW REUSE
        # ----------------------------------------------------

        elif reuse_category == "low":

            warnings.append(
                "Freshwater reduction from reuse "
                "is currently limited."
            )

            recommendations.append(
                "Evaluate higher-efficiency water "
                "recovery and reuse systems."
            )

        # ----------------------------------------------------
        # CAPACITY LIMIT
        # ----------------------------------------------------

        if (
            recycled_water
            > data.reuse_system_capacity_m3_per_day
            and data.reuse_system_capacity_m3_per_day
            > 0
        ):

            warnings.append(
                "Reuse-system capacity limits the "
                "amount of water that can be reused."
            )

            recommendations.append(
                "Consider increasing treatment and "
                "reuse-system capacity."
            )

        # ----------------------------------------------------
        # HIGH LOSSES
        # ----------------------------------------------------

        if data.reuse_loss_percentage > 30:

            warnings.append(
                "Reuse-system losses are relatively high."
            )

            recommendations.append(
                "Evaluate treatment-process and "
                "distribution losses."
            )

        # ----------------------------------------------------
        # NO REUSE INFRASTRUCTURE
        # ----------------------------------------------------

        if (
            data.reuse_percentage > 0
            and data.reuse_system_capacity_m3_per_day <= 0
        ):

            concerns.append(
                "reuse_target_exists_without_reuse_capacity"
            )

            recommendations.append(
                "Provide adequate treatment and "
                "reuse-system capacity."
            )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary = self.generate_summary(
            total_demand=(
                data.total_water_demand_m3_per_day
            ),
            reused_water=(
                total_reused_water
            ),
            freshwater_before=(
                freshwater_before
            ),
            freshwater_after=(
                freshwater_after
            ),
            savings_percent=(
                freshwater_savings_percent
            ),
            category=(
                reuse_category
            ),
        )

        return WaterReuseAssessment(

            valid_input=True,

            total_water_demand_m3_per_day=(
                data.total_water_demand_m3_per_day
            ),

            cooling_water_demand_m3_per_day=(
                data.cooling_water_demand_m3_per_day
            ),

            reuse_percentage=(
                data.reuse_percentage
            ),

            recycling_efficiency_percent=(
                data.recycling_efficiency_percent
            ),

            reuse_loss_percentage=(
                data.reuse_loss_percentage
            ),

            reuse_system_capacity_m3_per_day=(
                data.reuse_system_capacity_m3_per_day
            ),

            potential_reusable_water_m3_per_day=(
                potential_reusable_water
            ),

            recoverable_water_m3_per_day=(
                recoverable_water
            ),

            recycled_water_m3_per_day=(
                recycled_water_with_capacity
            ),

            reuse_losses_m3_per_day=(
                reuse_losses
            ),

            additional_reused_water_m3_per_day=(
                additional_reused_water
            ),

            total_reused_water_m3_per_day=(
                total_reused_water
            ),

            freshwater_demand_before_reuse_m3_per_day=(
                freshwater_before
            ),

            freshwater_demand_after_reuse_m3_per_day=(
                freshwater_after
            ),

            freshwater_savings_m3_per_day=(
                freshwater_savings
            ),

            freshwater_savings_percent=(
                freshwater_savings_percent
            ),

            reuse_system_utilization_percent=(
                system_utilization
            ),

            reuse_coverage_percent=(
                reuse_coverage
            ),

            reuse_category=(
                reuse_category
            ),

            concerns=(
                concerns
            ),

            warnings=(
                warnings
            ),

            recommendations=(
                recommendations
            ),

            summary=(
                summary
            ),
        )

    # ========================================================
    # INVALID RESULT
    # ========================================================

    @staticmethod
    def invalid_result(
        data: WaterReuseInput,
        errors: List[str],
    ) -> WaterReuseAssessment:
        """
        Return a safe result when validation fails.
        """

        return WaterReuseAssessment(

            valid_input=False,

            total_water_demand_m3_per_day=(
                data.total_water_demand_m3_per_day
            ),

            cooling_water_demand_m3_per_day=(
                data.cooling_water_demand_m3_per_day
            ),

            reuse_percentage=(
                data.reuse_percentage
            ),

            recycling_efficiency_percent=(
                data.recycling_efficiency_percent
            ),

            reuse_loss_percentage=(
                data.reuse_loss_percentage
            ),

            reuse_system_capacity_m3_per_day=(
                data.reuse_system_capacity_m3_per_day
            ),

            potential_reusable_water_m3_per_day=0.0,

            recoverable_water_m3_per_day=0.0,

            recycled_water_m3_per_day=0.0,

            reuse_losses_m3_per_day=0.0,

            additional_reused_water_m3_per_day=0.0,

            total_reused_water_m3_per_day=0.0,

            freshwater_demand_before_reuse_m3_per_day=(
                data.total_water_demand_m3_per_day
            ),

            freshwater_demand_after_reuse_m3_per_day=(
                data.total_water_demand_m3_per_day
            ),

            freshwater_savings_m3_per_day=0.0,

            freshwater_savings_percent=0.0,

            reuse_system_utilization_percent=0.0,

            reuse_coverage_percent=0.0,

            reuse_category="invalid",

            concerns=[
                "invalid_input",
            ],

            warnings=errors,

            recommendations=[],

            summary=(
                "Water-reuse analysis could not be "
                "completed because the input data "
                "is invalid."
            ),
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def generate_summary(
        total_demand: float,
        reused_water: float,
        freshwater_before: float,
        freshwater_after: float,
        savings_percent: float,
        category: str,
    ) -> str:
        """
        Generate human-readable summary.
        """

        return (
            f"The data center has an estimated total "
            f"water demand of {total_demand:.2f} m³/day. "
            f"The modeled reuse system supplies "
            f"{reused_water:.2f} m³/day of reused water. "
            f"Freshwater demand decreases from "
            f"{freshwater_before:.2f} m³/day to "
            f"{freshwater_after:.2f} m³/day, representing "
            f"a freshwater reduction of "
            f"{savings_percent:.2f}%. The preliminary "
            f"water-reuse category is '{category}'."
        )


# ============================================================
# PUBLIC API
# ============================================================


def analyze_water_reuse(
    data: WaterReuseInput,
) -> Dict[str, Any]:
    """
    Public service-layer function.

    Returns:
        Dictionary suitable for an API response.
    """

    model = WaterReuseModel()

    result = model.analyze(data)

    return asdict(result)


# ============================================================
# DEVELOPMENT TEST
# ============================================================


if __name__ == "__main__":

    import json

    sample_input = WaterReuseInput(

        total_water_demand_m3_per_day=1200.0,

        cooling_water_demand_m3_per_day=900.0,

        reuse_percentage=80.0,

        recycling_efficiency_percent=90.0,

        reuse_loss_percentage=10.0,

        reuse_system_capacity_m3_per_day=700.0,

        additional_reusable_water_m3_per_day=50.0,

        minimum_freshwater_requirement_m3_per_day=200.0,
    )

    model = WaterReuseModel()

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