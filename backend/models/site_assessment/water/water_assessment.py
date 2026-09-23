"""
India AI Grid
Integrated Water Assessment Model

File:
    backend/models/site_assessment/water/water_assessment.py

Purpose:
    Combines the individual water-assessment models into one
    site-level water assessment.

Expected water modules:

    water_availability.py
    water_quality.py
    water_demand.py
    water_reuse.py
    water_supply_demand.py
    water_storage.py
    water_resilience.py

This module is intentionally independent from those files.
Each individual model can be connected later through the
application/service layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Union


# ============================================================
# TYPE DEFINITIONS
# ============================================================

JSONPrimitive = Union[
    str,
    int,
    float,
    bool,
    None,
]

JSONValue = Union[
    JSONPrimitive,
    List["JSONValue"],
    Dict[str, "JSONValue"],
]


ModelResult = Dict[str, JSONValue]

ModelResults = Dict[str, ModelResult]

ScoreMap = Dict[str, float]

CategoryMap = Dict[str, str]


# ============================================================
# INPUT MODEL
# ============================================================


@dataclass
class WaterAssessmentInput:
    """
    Input to the integrated water assessment.

    Each model can be omitted while the backend is being
    developed.
    """

    water_availability: Optional[ModelResult] = None

    water_quality: Optional[ModelResult] = None

    water_demand: Optional[ModelResult] = None

    water_reuse: Optional[ModelResult] = None

    water_supply_demand: Optional[ModelResult] = None

    water_storage: Optional[ModelResult] = None

    water_resilience: Optional[ModelResult] = None


# ============================================================
# RESULT MODEL
# ============================================================


@dataclass
class WaterAssessmentResult:
    """
    Final integrated water-assessment result.
    """

    valid_input: bool

    overall_water_score: float

    overall_water_category: str

    model_count: int

    completed_model_count: int

    missing_models: List[str]

    critical_issues: List[str]

    concerns: List[str]

    warnings: List[str]

    recommendations: List[str]

    component_scores: ScoreMap

    component_categories: CategoryMap

    models: ModelResults

    summary: str

    def to_dict(self) -> Dict[str, JSONValue]:
        """
        Convert the result into a JSON-compatible dictionary.

        This method is used instead of dataclasses.asdict()
        so Pylance can keep complete type information.
        """

        return {
            "valid_input": self.valid_input,
            "overall_water_score": (
                self.overall_water_score
            ),
            "overall_water_category": (
                self.overall_water_category
            ),
            "model_count": self.model_count,
            "completed_model_count": (
                self.completed_model_count
            ),
            "missing_models": list(
                self.missing_models
            ),
            "critical_issues": list(
                self.critical_issues
            ),
            "concerns": list(
                self.concerns
            ),
            "warnings": list(
                self.warnings
            ),
            "recommendations": list(
                self.recommendations
            ),
            "component_scores": dict(
                self.component_scores
            ),
            "component_categories": dict(
                self.component_categories
            ),
            "models": dict(
                self.models
            ),
            "summary": self.summary,
        }


# ============================================================
# WATER ASSESSMENT MODEL
# ============================================================


class WaterAssessmentModel:
    """
    Main integrated water-assessment engine.
    """

    # --------------------------------------------------------
    # MODEL NAMES
    # --------------------------------------------------------

    MODEL_NAMES: Tuple[str, ...] = (
        "water_availability",
        "water_quality",
        "water_demand",
        "water_reuse",
        "water_supply_demand",
        "water_storage",
        "water_resilience",
    )

    # --------------------------------------------------------
    # MODEL WEIGHTS
    # --------------------------------------------------------

    MODEL_WEIGHTS: Dict[str, float] = {
        "water_availability": 0.20,
        "water_quality": 0.15,
        "water_demand": 0.10,
        "water_reuse": 0.10,
        "water_supply_demand": 0.15,
        "water_storage": 0.10,
        "water_resilience": 0.20,
    }

    # ========================================================
    # MODEL MAP
    # ========================================================

    @staticmethod
    def _build_model_map(
        data: WaterAssessmentInput,
    ) -> Dict[str, Optional[ModelResult]]:
        """
        Build a strongly typed map of all water models.
        """

        return {
            "water_availability": (
                data.water_availability
            ),
            "water_quality": (
                data.water_quality
            ),
            "water_demand": (
                data.water_demand
            ),
            "water_reuse": (
                data.water_reuse
            ),
            "water_supply_demand": (
                data.water_supply_demand
            ),
            "water_storage": (
                data.water_storage
            ),
            "water_resilience": (
                data.water_resilience
            ),
        }

    # ========================================================
    # VALUE HELPERS
    # ========================================================

    @staticmethod
    def _get_bool(
        result: ModelResult,
        key: str,
        default: bool,
    ) -> bool:
        """
        Safely retrieve a boolean.
        """

        value = result.get(key)

        if isinstance(value, bool):
            return value

        return default

    @staticmethod
    def _get_number(
        result: ModelResult,
        key: str,
    ) -> Optional[float]:
        """
        Safely retrieve a numeric value.
        """

        value = result.get(key)

        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        return None

    @staticmethod
    def _get_string(
        result: ModelResult,
        key: str,
    ) -> Optional[str]:
        """
        Safely retrieve a string.
        """

        value = result.get(key)

        if isinstance(value, str):

            cleaned = value.strip()

            if cleaned:
                return cleaned

        return None

    # ========================================================
    # COMPLETION
    # ========================================================

    @classmethod
    def _is_completed(
        cls,
        result: ModelResult,
    ) -> bool:
        """
        Determine whether a model returned a valid result.
        """

        return cls._get_bool(
            result,
            "valid_input",
            True,
        )

    # ========================================================
    # CATEGORY
    # ========================================================

    @classmethod
    def _get_category(
        cls,
        result: ModelResult,
    ) -> str:
        """
        Extract a category from an individual model.
        """

        category_keys: Tuple[str, ...] = (
            "overall_resilience_category",
            "water_stress_category",
            "reuse_category",
            "storage_category",
            "quality_category",
            "availability_category",
            "demand_category",
            "category",
        )

        for key in category_keys:

            category = cls._get_string(
                result,
                key,
            )

            if category is not None:
                return category

        return "unknown"

    # ========================================================
    # SCORE
    # ========================================================

    @classmethod
    def _get_score(
        cls,
        result: ModelResult,
    ) -> float:
        """
        Extract a 0-100 score.

        If an individual model does not expose a score,
        its category is converted to a preliminary score.
        """

        score_keys: Tuple[str, ...] = (
            "resilience_score",
            "water_score",
            "quality_score",
            "availability_score",
            "reuse_score",
            "storage_score",
            "score",
        )

        for key in score_keys:

            score = cls._get_number(
                result,
                key,
            )

            if score is not None:

                return cls._clamp_score(
                    score
                )

        category = cls._get_category(
            result
        ).lower()

        category_scores: Dict[str, float] = {
            "critical": 0.0,
            "very_low": 10.0,
            "very low": 10.0,
            "low": 25.0,
            "moderate": 50.0,
            "medium": 50.0,
            "good": 75.0,
            "high": 90.0,
            "very_high": 100.0,
            "very high": 100.0,
            "maximum": 100.0,
            "high_surplus": 100.0,
            "surplus": 90.0,
            "none": 0.0,
            "unknown": 50.0,
        }

        return category_scores.get(
            category,
            50.0,
        )

    # ========================================================
    # CLAMP SCORE
    # ========================================================

    @staticmethod
    def _clamp_score(
        score: float,
    ) -> float:
        """
        Keep score inside 0-100.
        """

        if score < 0.0:
            return 0.0

        if score > 100.0:
            return 100.0

        return score

    # ========================================================
    # LIST EXTRACTION
    # ========================================================

    @staticmethod
    def _extract_strings(
        result: ModelResult,
        key: str,
    ) -> List[str]:
        """
        Extract a list of strings from a model result.

        Non-string values are ignored deliberately. This keeps
        the integrated assessment predictable.
        """

        value = result.get(key)

        if not isinstance(value, list):
            return []

        output: List[str] = []

        for item in value:

            if isinstance(item, str):

                cleaned = item.strip()

                if cleaned:
                    output.append(
                        cleaned
                    )

        return output

    # ========================================================
    # UNIQUE LIST
    # ========================================================

    @staticmethod
    def _unique(
        values: List[str],
    ) -> List[str]:
        """
        Remove duplicates while preserving order.
        """

        result: List[str] = []

        seen: Set[str] = set()

        for value in values:

            cleaned = value.strip()

            if not cleaned:
                continue

            if cleaned in seen:
                continue

            seen.add(
                cleaned
            )

            result.append(
                cleaned
            )

        return result

    # ========================================================
    # OVERALL SCORE
    # ========================================================

    @classmethod
    def _calculate_overall_score(
        cls,
        component_scores: ScoreMap,
    ) -> float:
        """
        Calculate weighted overall score.

        Missing components are excluded and the remaining
        weights are normalized.
        """

        weighted_total = 0.0

        available_weight = 0.0

        for model_name, score in (
            component_scores.items()
        ):

            weight = cls.MODEL_WEIGHTS.get(
                model_name
            )

            if weight is None:
                continue

            if weight <= 0.0:
                continue

            weighted_total += (
                score * weight
            )

            available_weight += weight

        if available_weight <= 0.0:
            return 0.0

        return (
            weighted_total
            / available_weight
        )

    # ========================================================
    # OVERALL CATEGORY
    # ========================================================

    @staticmethod
    def _classify_score(
        score: float,
    ) -> str:
        """
        Convert overall score into a screening category.
        """

        if score < 25.0:
            return "critical"

        if score < 50.0:
            return "low"

        if score < 70.0:
            return "moderate"

        if score < 85.0:
            return "good"

        return "high"

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def _build_summary(
        score: float,
        category: str,
        completed: int,
        total: int,
        missing: List[str],
        critical_count: int,
    ) -> str:
        """
        Generate a concise human-readable summary.
        """

        summary = (
            "The integrated water assessment produced "
            f"a preliminary score of {score:.2f}/100 "
            f"with an overall water category of "
            f"'{category}'. "
            f"{completed} of {total} water models "
            "provided usable results."
        )

        if critical_count > 0:

            summary += (
                f" {critical_count} critical "
                "water issue(s) were identified."
            )

        if missing:

            summary += (
                " The assessment is incomplete because "
                "the following models have not returned "
                "results: "
                + ", ".join(
                    missing
                )
                + "."
            )

        return summary

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(
        self,
        data: WaterAssessmentInput,
    ) -> WaterAssessmentResult:
        """
        Execute the complete integrated water assessment.
        """

        model_map = self._build_model_map(
            data
        )

        model_results: ModelResults = {}

        completed_models: List[str] = []

        missing_models: List[str] = []

        critical_issues: List[str] = []

        concerns: List[str] = []

        warnings: List[str] = []

        recommendations: List[str] = []

        component_scores: ScoreMap = {}

        component_categories: CategoryMap = {}

        # ----------------------------------------------------
        # PROCESS MODELS
        # ----------------------------------------------------

        for model_name in self.MODEL_NAMES:

            result = model_map.get(
                model_name
            )

            # ----------------------------------------------
            # MISSING
            # ----------------------------------------------

            if result is None:

                missing_models.append(
                    model_name
                )

                continue

            # ----------------------------------------------
            # STORE
            # ----------------------------------------------

            model_results[
                model_name
            ] = result

            # ----------------------------------------------
            # VALIDITY
            # ----------------------------------------------

            if self._is_completed(
                result
            ):

                completed_models.append(
                    model_name
                )

            else:

                warnings.append(
                    f"{model_name} did not produce "
                    "a valid assessment."
                )

            # ----------------------------------------------
            # SCORE
            # ----------------------------------------------

            component_scores[
                model_name
            ] = round(
                self._get_score(
                    result
                ),
                2,
            )

            # ----------------------------------------------
            # CATEGORY
            # ----------------------------------------------

            component_categories[
                model_name
            ] = self._get_category(
                result
            )

            # ----------------------------------------------
            # ISSUES
            # ----------------------------------------------

            critical_issues.extend(
                self._extract_strings(
                    result,
                    "critical_factors",
                )
            )

            critical_issues.extend(
                self._extract_strings(
                    result,
                    "critical_issues",
                )
            )

            concerns.extend(
                self._extract_strings(
                    result,
                    "concerns",
                )
            )

            warnings.extend(
                self._extract_strings(
                    result,
                    "warnings",
                )
            )

            recommendations.extend(
                self._extract_strings(
                    result,
                    "recommendations",
                )
            )

        # ----------------------------------------------------
        # REMOVE DUPLICATES
        # ----------------------------------------------------

        critical_issues = self._unique(
            critical_issues
        )

        concerns = self._unique(
            concerns
        )

        warnings = self._unique(
            warnings
        )

        recommendations = self._unique(
            recommendations
        )

        # ----------------------------------------------------
        # INCOMPLETE WARNING
        # ----------------------------------------------------

        if missing_models:

            warnings.append(
                "The integrated water assessment "
                "is incomplete because one or more "
                "water models have not returned results."
            )

        warnings = self._unique(
            warnings
        )

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        overall_score = (
            self._calculate_overall_score(
                component_scores
            )
        )

        overall_category = (
            self._classify_score(
                overall_score
            )
        )

        # ----------------------------------------------------
        # VALIDITY
        # ----------------------------------------------------

        valid_input = (
            len(completed_models) > 0
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary = self._build_summary(
            score=overall_score,
            category=overall_category,
            completed=len(
                completed_models
            ),
            total=len(
                self.MODEL_NAMES
            ),
            missing=missing_models,
            critical_count=len(
                critical_issues
            ),
        )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        return WaterAssessmentResult(

            valid_input=valid_input,

            overall_water_score=round(
                overall_score,
                2,
            ),

            overall_water_category=(
                overall_category
            ),

            model_count=len(
                self.MODEL_NAMES
            ),

            completed_model_count=len(
                completed_models
            ),

            missing_models=list(
                missing_models
            ),

            critical_issues=list(
                critical_issues
            ),

            concerns=list(
                concerns
            ),

            warnings=list(
                warnings
            ),

            recommendations=list(
                recommendations
            ),

            component_scores=dict(
                component_scores
            ),

            component_categories=dict(
                component_categories
            ),

            models=dict(
                model_results
            ),

            summary=summary,
        )


# ============================================================
# PUBLIC API
# ============================================================


def analyze_water_assessment(
    data: WaterAssessmentInput,
) -> Dict[str, JSONValue]:
    """
    Public function used by the service/API layer.
    """

    model = WaterAssessmentModel()

    result = model.analyze(
        data
    )

    return result.to_dict()


# ============================================================
# DEVELOPMENT TEST
# ============================================================


def _run_development_test() -> None:
    """
    Local development test.

    Run:

        python water_assessment.py
    """

    import json

    sample_input = WaterAssessmentInput(

        water_availability={
            "valid_input": True,
            "availability_score": 85.0,
            "availability_category": "high",
        },

        water_quality={
            "valid_input": True,
            "quality_score": 80.0,
            "quality_category": "good",
        },

        water_demand={
            "valid_input": True,
            "demand_category": "moderate",
        },

        water_reuse={
            "valid_input": True,
            "reuse_category": "high",
            "freshwater_savings_percent": 55.0,
        },

        water_supply_demand={
            "valid_input": True,
            "water_stress_category": "high_surplus",
        },

        water_storage={
            "valid_input": True,
            "storage_category": "good",
            "storage_score": 75.0,
        },

        water_resilience={
            "valid_input": True,
            "overall_resilience_category": "good",
            "resilience_score": 78.0,
        },
    )

    result = analyze_water_assessment(
        sample_input
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":

    _run_development_test()
