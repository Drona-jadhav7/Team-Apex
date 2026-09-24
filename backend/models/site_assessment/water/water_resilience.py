"""
India AI Grid
Water Resilience Assessment Model

File:
    backend/models/site_assessment/water/water_resilience.py

Purpose:
    Combine water supply, demand, storage, seasonal reliability,
    and backup-supply information into a single water-resilience
    assessment for a proposed data-center site.

This model is intended for preliminary site screening.

It does NOT determine:
    - legal water rights
    - abstraction permissions
    - environmental clearances
    - engineering design requirements
    - statutory fire-water requirements
    - guaranteed water availability

Those should be handled by the appropriate regulatory,
engineering, and infrastructure models.
"""


from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


Number = Optional[float]


# ============================================================
# INPUT MODEL
# ============================================================


@dataclass
class WaterResilienceInput:
    """
    Inputs for the water-resilience model.

    Supply:
        sustainable_supply_m3_per_day

    Demand:
        average_demand_m3_per_day
        peak_demand_m3_per_day

    Dry season:
        dry_season_supply_m3_per_day
        dry_season_demand_m3_per_day

    Storage:
        storage_capacity_m3
        minimum_operating_reserve_m3

    Reliability:
        seasonal_reliability

    Backup:
        backup_supply_m3_per_day
        backup_storage_days

    Data:
        data_completeness
        source_count
    """

    sustainable_supply_m3_per_day: float

    average_demand_m3_per_day: float

    peak_demand_m3_per_day: float

    dry_season_supply_m3_per_day: Optional[float] = None

    dry_season_demand_m3_per_day: Optional[float] = None

    storage_capacity_m3: float = 0.0

    minimum_operating_reserve_m3: float = 0.0

    seasonal_reliability: Optional[str] = None

    backup_supply_m3_per_day: float = 0.0

    backup_storage_days: float = 0.0

    data_completeness: Optional[str] = None

    source_count: int = 1


# ============================================================
# RESULT MODEL
# ============================================================


@dataclass
class WaterResilienceAssessment:
    """
    Complete water-resilience assessment.
    """

    valid_input: bool

    sustainable_supply_m3_per_day: float

    average_demand_m3_per_day: float

    peak_demand_m3_per_day: float

    average_supply_coverage_ratio: Number

    peak_supply_coverage_ratio: Number

    dry_season_supply_coverage_ratio: Number

    storage_capacity_m3: float

    usable_storage_m3: float

    peak_storage_autonomy_days: Number

    backup_supply_m3_per_day: float

    backup_storage_days: float

    backup_supply_coverage_ratio: Number

    seasonal_reliability: Optional[str]

    data_completeness: Optional[str]

    source_count: int

    supply_resilience_category: str

    storage_resilience_category: str

    seasonal_resilience_category: str

    backup_resilience_category: str

    overall_resilience_category: str

    resilience_score: float

    critical_factors: List[str]

    concerns: List[str]

    warnings: List[str]

    recommendations: List[str]

    summary: str


# ============================================================
# THRESHOLDS
# ============================================================


class WaterResilienceThresholds:
    """
    Preliminary screening thresholds.

    These values are analytical thresholds and are NOT
    regulatory standards.
    """

    # Supply coverage

    SUPPLY_CRITICAL_RATIO = 0.50

    SUPPLY_LOW_RATIO = 0.75

    SUPPLY_MODERATE_RATIO = 1.00

    SUPPLY_GOOD_RATIO = 1.25

    # Storage autonomy

    STORAGE_CRITICAL_DAYS = 0.5

    STORAGE_LOW_DAYS = 1.0

    STORAGE_MODERATE_DAYS = 2.0

    STORAGE_GOOD_DAYS = 3.0

    # Backup coverage

    BACKUP_CRITICAL_RATIO = 0.25

    BACKUP_LOW_RATIO = 0.50

    BACKUP_MODERATE_RATIO = 0.75

    BACKUP_GOOD_RATIO = 1.00


# ============================================================
# MODEL
# ============================================================


class WaterResilienceModel:
    """
    Evaluate overall water resilience of a data-center site.
    """

    def __init__(
        self,
        thresholds: Optional[WaterResilienceThresholds] = None,
    ) -> None:

        self.thresholds = (
            thresholds
            if thresholds is not None
            else WaterResilienceThresholds()
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def validate_input(
        data: WaterResilienceInput,
    ) -> List[str]:
        """
        Validate all input values.
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
            data.dry_season_supply_m3_per_day
            is not None
            and data.dry_season_supply_m3_per_day < 0
        ):
            errors.append(
                "dry_season_supply_m3_per_day "
                "cannot be negative."
            )

        if (
            data.dry_season_demand_m3_per_day
            is not None
            and data.dry_season_demand_m3_per_day < 0
        ):
            errors.append(
                "dry_season_demand_m3_per_day "
                "cannot be negative."
            )

        if data.storage_capacity_m3 < 0:
            errors.append(
                "storage_capacity_m3 "
                "cannot be negative."
            )

        if data.minimum_operating_reserve_m3 < 0:
            errors.append(
                "minimum_operating_reserve_m3 "
                "cannot be negative."
            )

        if (
            data.minimum_operating_reserve_m3
            > data.storage_capacity_m3
        ):
            errors.append(
                "minimum_operating_reserve_m3 cannot "
                "exceed storage_capacity_m3."
            )

        if data.backup_supply_m3_per_day < 0:
            errors.append(
                "backup_supply_m3_per_day "
                "cannot be negative."
            )

        if data.backup_storage_days < 0:
            errors.append(
                "backup_storage_days "
                "cannot be negative."
            )

        if data.source_count < 0:
            errors.append(
                "source_count cannot be negative."
            )

        return errors

    # ========================================================
    # COVERAGE RATIO
    # ========================================================

    @staticmethod
    def coverage_ratio(
        supply_m3_per_day: float,
        demand_m3_per_day: float,
    ) -> Number:
        """
        Calculate supply / demand.
        """

        if demand_m3_per_day <= 0:
            return None

        return (
            supply_m3_per_day
            / demand_m3_per_day
        )

    # ========================================================
    # STORAGE AUTONOMY
    # ========================================================

    @staticmethod
    def storage_autonomy_days(
        storage_capacity_m3: float,
        reserve_m3: float,
        demand_m3_per_day: float,
    ) -> Number:
        """
        Calculate usable storage autonomy.
        """

        usable_storage = max(
            storage_capacity_m3 - reserve_m3,
            0.0,
        )

        if demand_m3_per_day <= 0:
            return None

        return (
            usable_storage
            / demand_m3_per_day
        )

    # ========================================================
    # SUPPLY CATEGORY
    # ========================================================

    def classify_supply(
        self,
        ratio: Number,
    ) -> str:
        """
        Classify supply resilience.
        """

        if ratio is None:
            return "no_demand"

        if (
            ratio
            < self.thresholds.SUPPLY_CRITICAL_RATIO
        ):
            return "critical"

        if (
            ratio
            < self.thresholds.SUPPLY_LOW_RATIO
        ):
            return "low"

        if (
            ratio
            < self.thresholds.SUPPLY_MODERATE_RATIO
        ):
            return "moderate"

        if (
            ratio
            < self.thresholds.SUPPLY_GOOD_RATIO
        ):
            return "good"

        return "high"

    # ========================================================
    # STORAGE CATEGORY
    # ========================================================

    def classify_storage(
        self,
        autonomy_days: Number,
    ) -> str:
        """
        Classify storage resilience.
        """

        if autonomy_days is None:
            return "no_demand"

        if (
            autonomy_days
            < self.thresholds.STORAGE_CRITICAL_DAYS
        ):
            return "critical"

        if (
            autonomy_days
            < self.thresholds.STORAGE_LOW_DAYS
        ):
            return "low"

        if (
            autonomy_days
            < self.thresholds.STORAGE_MODERATE_DAYS
        ):
            return "moderate"

        if (
            autonomy_days
            < self.thresholds.STORAGE_GOOD_DAYS
        ):
            return "good"

        return "high"

    # ========================================================
    # BACKUP CATEGORY
    # ========================================================

    def classify_backup(
        self,
        ratio: Number,
    ) -> str:
        """
        Classify backup-supply coverage.
        """

        if ratio is None:
            return "no_demand"

        if (
            ratio
            < self.thresholds.BACKUP_CRITICAL_RATIO
        ):
            return "critical"

        if (
            ratio
            < self.thresholds.BACKUP_LOW_RATIO
        ):
            return "low"

        if (
            ratio
            < self.thresholds.BACKUP_MODERATE_RATIO
        ):
            return "moderate"

        if (
            ratio
            < self.thresholds.BACKUP_GOOD_RATIO
        ):
            return "good"

        return "high"

    # ========================================================
    # SEASONAL CATEGORY
    # ========================================================

    @staticmethod
    def classify_seasonal_reliability(
        reliability: Optional[str],
    ) -> str:
        """
        Normalize seasonal-reliability information.
        """

        if reliability is None:
            return "unknown"

        normalized = reliability.strip().lower()

        if normalized in {
            "very_low",
            "very low",
            "critical",
        }:
            return "critical"

        if normalized == "low":
            return "low"

        if normalized == "moderate":
            return "moderate"

        if normalized in {
            "good",
            "high",
        }:
            return "good"

        if normalized in {
            "very_high",
            "very high",
        }:
            return "high"

        return "unknown"

    # ========================================================
    # SCORE COMPONENT
    # ========================================================

    @staticmethod
    def category_score(
        category: str,
    ) -> float:
        """
        Convert qualitative category to numerical score.

        Score range:
            0 - 100
        """

        scores = {
            "critical": 0.0,
            "low": 25.0,
            "moderate": 50.0,
            "good": 75.0,
            "high": 100.0,
            "unknown": 50.0,
            "no_demand": 100.0,
        }

        return scores.get(
            category,
            50.0,
        )

    # ========================================================
    # OVERALL CATEGORY
    # ========================================================

    @staticmethod
    def classify_overall(
        score: float,
    ) -> str:
        """
        Convert resilience score into overall category.
        """

        if score < 25:
            return "critical"

        if score < 50:
            return "low"

        if score < 70:
            return "moderate"

        if score < 85:
            return "good"

        return "high"

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(
        self,
        data: WaterResilienceInput,
    ) -> WaterResilienceAssessment:
        """
        Generate complete water-resilience assessment.
        """

        errors = self.validate_input(data)

        if errors:
            return self.invalid_result(
                data,
                errors,
            )

        # ----------------------------------------------------
        # SUPPLY COVERAGE
        # ----------------------------------------------------

        average_supply_ratio = (
            self.coverage_ratio(
                supply_m3_per_day=(
                    data.sustainable_supply_m3_per_day
                ),
                demand_m3_per_day=(
                    data.average_demand_m3_per_day
                ),
            )
        )

        peak_supply_ratio = (
            self.coverage_ratio(
                supply_m3_per_day=(
                    data.sustainable_supply_m3_per_day
                ),
                demand_m3_per_day=(
                    data.peak_demand_m3_per_day
                ),
            )
        )

        # ----------------------------------------------------
        # DRY-SEASON COVERAGE
        # ----------------------------------------------------

        if (
            data.dry_season_supply_m3_per_day
            is not None
            and data.dry_season_demand_m3_per_day
            is not None
        ):

            dry_season_ratio = (
                self.coverage_ratio(
                    supply_m3_per_day=(
                        data.dry_season_supply_m3_per_day
                    ),
                    demand_m3_per_day=(
                        data.dry_season_demand_m3_per_day
                    ),
                )
            )

        else:

            dry_season_ratio = None

        # ----------------------------------------------------
        # STORAGE
        # ----------------------------------------------------

        usable_storage = max(
            data.storage_capacity_m3
            - data.minimum_operating_reserve_m3,
            0.0,
        )

        peak_storage_autonomy = (
            self.storage_autonomy_days(
                storage_capacity_m3=(
                    data.storage_capacity_m3
                ),
                reserve_m3=(
                    data.minimum_operating_reserve_m3
                ),
                demand_m3_per_day=(
                    data.peak_demand_m3_per_day
                ),
            )
        )

        # ----------------------------------------------------
        # BACKUP
        # ----------------------------------------------------

        backup_ratio = (
            self.coverage_ratio(
                supply_m3_per_day=(
                    data.backup_supply_m3_per_day
                ),
                demand_m3_per_day=(
                    data.peak_demand_m3_per_day
                ),
            )
        )

        # ----------------------------------------------------
        # CATEGORIES
        # ----------------------------------------------------

        supply_category = self.classify_supply(
            peak_supply_ratio,
        )

        storage_category = self.classify_storage(
            peak_storage_autonomy,
        )

        seasonal_category = (
            self.classify_seasonal_reliability(
                data.seasonal_reliability,
            )
        )

        backup_category = self.classify_backup(
            backup_ratio,
        )

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        supply_score = self.category_score(
            supply_category,
        )

        storage_score = self.category_score(
            storage_category,
        )

        seasonal_score = self.category_score(
            seasonal_category,
        )

        backup_score = self.category_score(
            backup_category,
        )

        resilience_score = (
            supply_score * 0.40
            + storage_score * 0.25
            + seasonal_score * 0.20
            + backup_score * 0.15
        )

        resilience_score = round(
            resilience_score,
            2,
        )

        overall_category = self.classify_overall(
            resilience_score,
        )

        # ----------------------------------------------------
        # CONCERNS
        # ----------------------------------------------------

        critical_factors: List[str] = []

        concerns: List[str] = []

        warnings: List[str] = []

        recommendations: List[str] = []

        # Supply

        if supply_category in {
            "critical",
            "low",
        }:

            critical_factors.append(
                "insufficient_peak_water_supply"
            )

            concerns.append(
                "Peak water demand may exceed "
                "sustainable supply."
            )

            recommendations.append(
                "Increase sustainable supply, "
                "reduce water demand, or provide "
                "additional permitted supply."
            )

        # Dry season

        if dry_season_ratio is not None:

            if dry_season_ratio < 1.0:

                critical_factors.append(
                    "dry_season_supply_deficit"
                )

                concerns.append(
                    "Dry-season supply may not cover "
                    "dry-season demand."
                )

                recommendations.append(
                    "Evaluate dry-season storage, "
                    "water reuse, or supplementary "
                    "permitted supply."
                )

        else:

            warnings.append(
                "Dry-season supply-demand data "
                "is unavailable."
            )

        # Storage

        if storage_category == "critical":

            critical_factors.append(
                "critical_storage_autonomy"
            )

            concerns.append(
                "Water storage provides very limited "
                "peak-demand autonomy."
            )

            recommendations.append(
                "Increase usable water-storage capacity."
            )

        elif storage_category == "low":

            concerns.append(
                "Low water-storage autonomy."
            )

            recommendations.append(
                "Consider increasing storage capacity."
            )

        # Seasonal reliability

        if seasonal_category == "critical":

            critical_factors.append(
                "critical_seasonal_reliability"
            )

            concerns.append(
                "Seasonal water reliability is low."
            )

        elif seasonal_category == "low":

            concerns.append(
                "Seasonal water reliability is limited."
            )

        elif seasonal_category == "unknown":

            warnings.append(
                "Seasonal reliability has not "
                "been established."
            )

        # Backup

        if backup_category == "critical":

            concerns.append(
                "Backup water supply is very limited."
            )

            recommendations.append(
                "Evaluate a secondary water source "
                "for continuity."
            )

        elif backup_category == "low":

            concerns.append(
                "Backup water supply provides "
                "limited peak-demand coverage."
            )

        if data.backup_storage_days <= 0:

            warnings.append(
                "No backup-storage duration "
                "was provided."
            )

        # Data completeness

        if data.data_completeness in {
            "low",
            "very_low",
        }:

            warnings.append(
                "Water data completeness is limited; "
                "resilience results may have high uncertainty."
            )

        # Source count

        if data.source_count <= 1:

            warnings.append(
                "The assessment relies on a single "
                "or insufficiently diversified water source."
            )

            recommendations.append(
                "Evaluate source diversification."
            )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary = self.generate_summary(
            supply_ratio=peak_supply_ratio,
            dry_ratio=dry_season_ratio,
            storage_days=peak_storage_autonomy,
            backup_ratio=backup_ratio,
            score=resilience_score,
            category=overall_category,
        )

        return WaterResilienceAssessment(

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

            average_supply_coverage_ratio=(
                average_supply_ratio
            ),

            peak_supply_coverage_ratio=(
                peak_supply_ratio
            ),

            dry_season_supply_coverage_ratio=(
                dry_season_ratio
            ),

            storage_capacity_m3=(
                data.storage_capacity_m3
            ),

            usable_storage_m3=(
                usable_storage
            ),

            peak_storage_autonomy_days=(
                peak_storage_autonomy
            ),

            backup_supply_m3_per_day=(
                data.backup_supply_m3_per_day
            ),

            backup_storage_days=(
                data.backup_storage_days
            ),

            backup_supply_coverage_ratio=(
                backup_ratio
            ),

            seasonal_reliability=(
                data.seasonal_reliability
            ),

            data_completeness=(
                data.data_completeness
            ),

            source_count=(
                data.source_count
            ),

            supply_resilience_category=(
                supply_category
            ),

            storage_resilience_category=(
                storage_category
            ),

            seasonal_resilience_category=(
                seasonal_category
            ),

            backup_resilience_category=(
                backup_category
            ),

            overall_resilience_category=(
                overall_category
            ),

            resilience_score=(
                resilience_score
            ),

            critical_factors=(
                critical_factors
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
        data: WaterResilienceInput,
        errors: List[str],
    ) -> WaterResilienceAssessment:
        """
        Return a safe result when validation fails.
        """

        return WaterResilienceAssessment(

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

            average_supply_coverage_ratio=None,

            peak_supply_coverage_ratio=None,

            dry_season_supply_coverage_ratio=None,

            storage_capacity_m3=(
                data.storage_capacity_m3
            ),

            usable_storage_m3=0.0,

            peak_storage_autonomy_days=None,

            backup_supply_m3_per_day=(
                data.backup_supply_m3_per_day
            ),

            backup_storage_days=(
                data.backup_storage_days
            ),

            backup_supply_coverage_ratio=None,

            seasonal_reliability=(
                data.seasonal_reliability
            ),

            data_completeness=(
                data.data_completeness
            ),

            source_count=(
                data.source_count
            ),

            supply_resilience_category="invalid",

            storage_resilience_category="invalid",

            seasonal_resilience_category="invalid",

            backup_resilience_category="invalid",

            overall_resilience_category="invalid",

            resilience_score=0.0,

            critical_factors=[
                "invalid_input",
            ],

            concerns=[
                "invalid_input",
            ],

            warnings=errors,

            recommendations=[],

            summary=(
                "Water resilience analysis could not "
                "be completed because the input "
                "data is invalid."
            ),
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def generate_summary(
        supply_ratio: Number,
        dry_ratio: Number,
        storage_days: Number,
        backup_ratio: Number,
        score: float,
        category: str,
    ) -> str:
        """
        Generate a human-readable summary.
        """

        if supply_ratio is None:
            supply_text = "unknown"
        else:
            supply_text = f"{supply_ratio:.2f}"

        if dry_ratio is None:
            dry_text = "unknown"
        else:
            dry_text = f"{dry_ratio:.2f}"

        if storage_days is None:
            storage_text = "unknown"
        else:
            storage_text = f"{storage_days:.2f}"

        if backup_ratio is None:
            backup_text = "unknown"
        else:
            backup_text = f"{backup_ratio:.2f}"

        return (
            "The site's preliminary water-resilience "
            f"assessment reports a peak supply-demand "
            f"coverage ratio of {supply_text}, dry-season "
            f"coverage ratio of {dry_text}, peak-storage "
            f"autonomy of {storage_text} days, and backup "
            f"supply coverage ratio of {backup_text}. "
            f"The calculated resilience score is "
            f"{score:.2f}/100 and the overall preliminary "
            f"resilience category is '{category}'."
        )


# ============================================================
# PUBLIC API
# ============================================================


def analyze_water_resilience(
    data: WaterResilienceInput,
) -> Dict[str, Any]:
    """
    Public service-layer function.

    Returns:
        Dictionary suitable for an API response.
    """

    model = WaterResilienceModel()

    result = model.analyze(data)

    return asdict(result)


# ============================================================
# DEVELOPMENT TEST
# ============================================================


if __name__ == "__main__":

    import json

    sample_input = WaterResilienceInput(

        sustainable_supply_m3_per_day=3000.0,

        average_demand_m3_per_day=1200.0,

        peak_demand_m3_per_day=1500.0,

        dry_season_supply_m3_per_day=1800.0,

        dry_season_demand_m3_per_day=1200.0,

        storage_capacity_m3=5000.0,

        minimum_operating_reserve_m3=500.0,

        seasonal_reliability="moderate",

        backup_supply_m3_per_day=300.0,

        backup_storage_days=2.0,

        data_completeness="high",

        source_count=2,
    )

    model = WaterResilienceModel()

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