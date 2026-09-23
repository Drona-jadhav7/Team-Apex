"""
India AI Grid
Data Center Water Demand Model

File:
    backend/models/site_assessment/water/water_demand.py

Purpose:
    Estimate water demand for a proposed data center.

The model estimates:

    - IT load
    - Facility load
    - PUE
    - Cooling technology
    - Cooling water consumption
    - Other facility water consumption
    - Daily water demand
    - Monthly water demand
    - Annual water demand
    - Peak water demand
    - Water intensity

The model is designed for PRELIMINARY SITE ASSESSMENT.

It is NOT a replacement for:

    - detailed mechanical engineering
    - cooling-system design
    - environmental assessment
    - water-allocation permissions
    - utility confirmation
    - OEM specifications

The final site water score should combine this demand model
with:

    surface_water.py
    groundwater.py
    seasonal_reliability.py
    water_quality.py
    water_availability.py
"""


from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


# ============================================================
# TYPE ALIAS
# ============================================================

Number = Optional[float]


# ============================================================
# COOLING TECHNOLOGIES
# ============================================================

COOLING_TECHNOLOGIES = {
    "air_cooled",
    "water_cooled",
    "evaporative",
    "hybrid",
    "direct_to_chip",
    "immersion",
    "custom",
}


# ============================================================
# DATA CENTER INPUT
# ============================================================


@dataclass
class DataCenterWaterDemandInput:
    """
    Input parameters for water-demand estimation.

    it_load_mw:
        Expected IT equipment load.

    utilization:
        Average fraction of IT capacity actually operating.

        Example:

            0.50 = 50%
            0.80 = 80%
            1.00 = 100%

    pue:
        Power Usage Effectiveness.

        Example:

            1.20
            1.40
            1.60

    cooling_technology:
        Primary cooling technology.

    cooling_water_liters_per_kwh:
        Water consumption associated with cooling.

        This should ideally come from the selected cooling
        system/OEM design.

    non_cooling_water_liters_per_kwh:
        Water used for:

            - domestic use
            - cleaning
            - landscaping
            - other facility operations

    operating_hours_per_day:
        Expected operating hours.

    peak_factor:
        Peak-to-average demand multiplier.

    """

    it_load_mw: float

    utilization: float

    pue: float

    cooling_technology: str

    cooling_water_liters_per_kwh: float

    non_cooling_water_liters_per_kwh: float = 0.0

    operating_hours_per_day: float = 24.0

    peak_factor: float = 1.20


# ============================================================
# WATER DEMAND RESULT
# ============================================================


@dataclass
class WaterDemandAssessment:
    """
    Complete water-demand assessment.
    """

    valid_input: bool

    it_load_mw: float

    utilization: float

    effective_it_load_mw: float

    pue: float

    facility_load_mw: float

    cooling_technology: str

    operating_hours_per_day: float

    cooling_water_liters_per_kwh: float

    non_cooling_water_liters_per_kwh: float

    cooling_water_liters_per_day: float

    non_cooling_water_liters_per_day: float

    total_water_liters_per_day: float

    total_water_m3_per_day: float

    peak_water_m3_per_day: float

    total_water_m3_per_month: float

    total_water_m3_per_year: float

    water_intensity_liters_per_kwh: float

    water_intensity_liters_per_it_kwh: float

    cooling_share_percent: float

    non_cooling_share_percent: float

    demand_category: str

    concerns: List[str]

    warnings: List[str]

    summary: str


# ============================================================
# THRESHOLDS
# ============================================================


class WaterDemandThresholds:
    """
    Preliminary screening thresholds.

    These are NOT regulatory limits.
    """

    LOW_DAILY_DEMAND_M3: float = 50.0

    MODERATE_DAILY_DEMAND_M3: float = 250.0

    HIGH_DAILY_DEMAND_M3: float = 1000.0

    VERY_HIGH_DAILY_DEMAND_M3: float = 5000.0

    HIGH_WATER_INTENSITY_L_PER_KWH: float = 2.0

    VERY_HIGH_WATER_INTENSITY_L_PER_KWH: float = 4.0

    MIN_PUE: float = 1.0

    MAX_REASONABLE_PUE: float = 3.0


# ============================================================
# MODEL
# ============================================================


class WaterDemandModel:
    """
    Estimate data-center water demand.
    """

    def __init__(
        self,
        thresholds: Optional[
            WaterDemandThresholds
        ] = None,
    ) -> None:

        self.thresholds = (
            thresholds
            if thresholds is not None
            else WaterDemandThresholds()
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def validate_input(
        data: DataCenterWaterDemandInput,
    ) -> List[str]:
        """
        Validate model inputs.

        Returns a list of validation errors.
        """

        errors: List[str] = []

        if data.it_load_mw <= 0:

            errors.append(
                "it_load_mw must be greater than zero."
            )

        if not 0.0 < data.utilization <= 1.0:

            errors.append(
                "utilization must be greater than 0 "
                "and less than or equal to 1."
            )

        if data.pue < 1.0:

            errors.append(
                "pue cannot be below 1.0."
            )

        if data.pue > 10.0:

            errors.append(
                "pue is outside the supported range."
            )

        cooling_type: str = (
            data.cooling_technology
            .strip()
            .lower()
        )

        if cooling_type not in COOLING_TECHNOLOGIES:

            errors.append(
                "Unsupported cooling technology: "
                f"{data.cooling_technology}"
            )

        if (
            data.cooling_water_liters_per_kwh
            < 0
        ):

            errors.append(
                "cooling_water_liters_per_kwh "
                "cannot be negative."
            )

        if (
            data.non_cooling_water_liters_per_kwh
            < 0
        ):

            errors.append(
                "non_cooling_water_liters_per_kwh "
                "cannot be negative."
            )

        if not (
            0.0 < data.operating_hours_per_day <= 24.0
        ):

            errors.append(
                "operating_hours_per_day must be "
                "between 0 and 24."
            )

        if data.peak_factor < 1.0:

            errors.append(
                "peak_factor must be at least 1.0."
            )

        return errors

    # ========================================================
    # EFFECTIVE IT LOAD
    # ========================================================

    @staticmethod
    def effective_it_load(
        it_load_mw: float,
        utilization: float,
    ) -> float:
        """
        Calculate average operating IT load.
        """

        return (
            it_load_mw
            * utilization
        )

    # ========================================================
    # FACILITY LOAD
    # ========================================================

    @staticmethod
    def facility_load(
        effective_it_load_mw: float,
        pue: float,
    ) -> float:
        """
        Calculate total facility electrical load.

        Facility Load = IT Load × PUE
        """

        return (
            effective_it_load_mw
            * pue
        )

    # ========================================================
    # ENERGY
    # ========================================================

    @staticmethod
    def daily_energy_kwh(
        load_mw: float,
        operating_hours_per_day: float,
    ) -> float:
        """
        Convert MW load to daily kWh.
        """

        return (
            load_mw
            * 1000.0
            * operating_hours_per_day
        )

    # ========================================================
    # COOLING WATER
    # ========================================================

    @staticmethod
    def cooling_water_demand(
        energy_kwh: float,
        water_intensity_liters_per_kwh: float,
    ) -> float:
        """
        Calculate daily cooling-water consumption.
        """

        return (
            energy_kwh
            * water_intensity_liters_per_kwh
        )

    # ========================================================
    # NON-COOLING WATER
    # ========================================================

    @staticmethod
    def non_cooling_water_demand(
        energy_kwh: float,
        water_intensity_liters_per_kwh: float,
    ) -> float:
        """
        Calculate non-cooling water consumption.
        """

        return (
            energy_kwh
            * water_intensity_liters_per_kwh
        )

    # ========================================================
    # TOTAL WATER
    # ========================================================

    @staticmethod
    def total_water_demand(
        cooling_water_liters: float,
        non_cooling_water_liters: float,
    ) -> float:
        """
        Total water demand in litres.
        """

        return (
            cooling_water_liters
            + non_cooling_water_liters
        )

    # ========================================================
    # LITRES → CUBIC METRES
    # ========================================================

    @staticmethod
    def liters_to_m3(
        liters: float,
    ) -> float:

        return liters / 1000.0

    # ========================================================
    # MONTHLY DEMAND
    # ========================================================

    @staticmethod
    def monthly_demand_m3(
        daily_demand_m3: float,
        days: int = 30,
    ) -> float:

        return (
            daily_demand_m3
            * days
        )

    # ========================================================
    # ANNUAL DEMAND
    # ========================================================

    @staticmethod
    def annual_demand_m3(
        daily_demand_m3: float,
        days: int = 365,
    ) -> float:

        return (
            daily_demand_m3
            * days
        )

    # ========================================================
    # PEAK DEMAND
    # ========================================================

    @staticmethod
    def peak_demand_m3(
        average_daily_demand_m3: float,
        peak_factor: float,
    ) -> float:

        return (
            average_daily_demand_m3
            * peak_factor
        )

    # ========================================================
    # WATER INTENSITY
    # ========================================================

    @staticmethod
    def water_intensity(
        total_water_liters: float,
        energy_kwh: float,
    ) -> float:
        """
        Total water consumption per facility kWh.
        """

        if energy_kwh <= 0:

            return 0.0

        return (
            total_water_liters
            / energy_kwh
        )

    # ========================================================
    # IT WATER INTENSITY
    # ========================================================

    @staticmethod
    def it_water_intensity(
        total_water_liters: float,
        it_energy_kwh: float,
    ) -> float:
        """
        Water consumption per IT kWh.
        """

        if it_energy_kwh <= 0:

            return 0.0

        return (
            total_water_liters
            / it_energy_kwh
        )

    # ========================================================
    # WATER SHARES
    # ========================================================

    @staticmethod
    def water_share(
        component_liters: float,
        total_liters: float,
    ) -> float:

        if total_liters <= 0:

            return 0.0

        return (
            component_liters
            / total_liters
        ) * 100.0

    # ========================================================
    # DEMAND CATEGORY
    # ========================================================

    def demand_category(
        self,
        daily_demand_m3: float,
    ) -> str:

        if (
            daily_demand_m3
            < self.thresholds.LOW_DAILY_DEMAND_M3
        ):

            return "low"

        if (
            daily_demand_m3
            < self.thresholds.MODERATE_DAILY_DEMAND_M3
        ):

            return "moderate"

        if (
            daily_demand_m3
            < self.thresholds.HIGH_DAILY_DEMAND_M3
        ):

            return "high"

        if (
            daily_demand_m3
            < self.thresholds.VERY_HIGH_DAILY_DEMAND_M3
        ):

            return "very_high"

        return "extremely_high"

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(
        self,
        data: DataCenterWaterDemandInput,
    ) -> WaterDemandAssessment:
        """
        Generate complete water-demand assessment.
        """

        errors: List[str] = (
            self.validate_input(data)
        )

        if errors:

            return self.invalid_result(
                data=data,
                errors=errors,
            )

        cooling_type: str = (
            data.cooling_technology
            .strip()
            .lower()
        )

        # ----------------------------------------------------
        # IT LOAD
        # ----------------------------------------------------

        effective_it_load_mw: float = (
            self.effective_it_load(
                it_load_mw=data.it_load_mw,
                utilization=data.utilization,
            )
        )

        # ----------------------------------------------------
        # FACILITY LOAD
        # ----------------------------------------------------

        facility_load_mw: float = (
            self.facility_load(
                effective_it_load_mw=effective_it_load_mw,
                pue=data.pue,
            )
        )

        # ----------------------------------------------------
        # ENERGY
        # ----------------------------------------------------

        facility_energy_kwh: float = (
            self.daily_energy_kwh(
                load_mw=facility_load_mw,
                operating_hours_per_day=(
                    data.operating_hours_per_day
                ),
            )
        )

        it_energy_kwh: float = (
            self.daily_energy_kwh(
                load_mw=effective_it_load_mw,
                operating_hours_per_day=(
                    data.operating_hours_per_day
                ),
            )
        )

        # ----------------------------------------------------
        # COOLING WATER
        # ----------------------------------------------------

        cooling_water_liters: float = (
            self.cooling_water_demand(
                energy_kwh=facility_energy_kwh,
                water_intensity_liters_per_kwh=(
                    data.cooling_water_liters_per_kwh
                ),
            )
        )

        # ----------------------------------------------------
        # NON-COOLING WATER
        # ----------------------------------------------------

        non_cooling_water_liters: float = (
            self.non_cooling_water_demand(
                energy_kwh=facility_energy_kwh,
                water_intensity_liters_per_kwh=(
                    data.non_cooling_water_liters_per_kwh
                ),
            )
        )

        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

        total_water_liters: float = (
            self.total_water_demand(
                cooling_water_liters=(
                    cooling_water_liters
                ),
                non_cooling_water_liters=(
                    non_cooling_water_liters
                ),
            )
        )

        total_water_m3: float = (
            self.liters_to_m3(
                total_water_liters
            )
        )

        # ----------------------------------------------------
        # PEAK
        # ----------------------------------------------------

        peak_water_m3: float = (
            self.peak_demand_m3(
                average_daily_demand_m3=(
                    total_water_m3
                ),
                peak_factor=data.peak_factor,
            )
        )

        # ----------------------------------------------------
        # MONTHLY
        # ----------------------------------------------------

        monthly_water_m3: float = (
            self.monthly_demand_m3(
                daily_demand_m3=total_water_m3
            )
        )

        # ----------------------------------------------------
        # ANNUAL
        # ----------------------------------------------------

        annual_water_m3: float = (
            self.annual_demand_m3(
                daily_demand_m3=total_water_m3
            )
        )

        # ----------------------------------------------------
        # INTENSITY
        # ----------------------------------------------------

        water_intensity: float = (
            self.water_intensity(
                total_water_liters=(
                    total_water_liters
                ),
                energy_kwh=facility_energy_kwh,
            )
        )

        it_water_intensity: float = (
            self.it_water_intensity(
                total_water_liters=(
                    total_water_liters
                ),
                it_energy_kwh=it_energy_kwh,
            )
        )

        # ----------------------------------------------------
        # SHARES
        # ----------------------------------------------------

        cooling_share: float = (
            self.water_share(
                component_liters=(
                    cooling_water_liters
                ),
                total_liters=(
                    total_water_liters
                ),
            )
        )

        non_cooling_share: float = (
            self.water_share(
                component_liters=(
                    non_cooling_water_liters
                ),
                total_liters=(
                    total_water_liters
                ),
            )
        )

        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        category: str = (
            self.demand_category(
                daily_demand_m3=total_water_m3
            )
        )

        # ----------------------------------------------------
        # WARNINGS
        # ----------------------------------------------------

        concerns: List[str] = []

        warnings: List[str] = []

        if (
            water_intensity
            >= self.thresholds.VERY_HIGH_WATER_INTENSITY_L_PER_KWH
        ):

            concerns.append(
                "very_high_water_intensity"
            )

        elif (
            water_intensity
            >= self.thresholds.HIGH_WATER_INTENSITY_L_PER_KWH
        ):

            concerns.append(
                "high_water_intensity"
            )

        if (
            category
            in {
                "very_high",
                "extremely_high",
            }
        ):

            concerns.append(
                "high_absolute_water_demand"
            )

        if cooling_type in {
            "water_cooled",
            "evaporative",
            "hybrid",
        }:

            warnings.append(
                "Cooling configuration has direct "
                "water-demand implications."
            )

        if cooling_type in {
            "direct_to_chip",
            "immersion",
        }:

            warnings.append(
                "Cooling water demand depends heavily "
                "on the actual heat-rejection architecture."
            )

        warnings.append(
            "Water demand is an estimate and should "
            "be replaced by detailed engineering data "
            "during final design."
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary: str = (
            self.generate_summary(
                it_load_mw=data.it_load_mw,
                effective_it_load_mw=(
                    effective_it_load_mw
                ),
                facility_load_mw=(
                    facility_load_mw
                ),
                cooling_type=cooling_type,
                daily_water_m3=total_water_m3,
                annual_water_m3=annual_water_m3,
                water_intensity=water_intensity,
                category=category,
            )
        )

        return WaterDemandAssessment(

            valid_input=True,

            it_load_mw=data.it_load_mw,

            utilization=data.utilization,

            effective_it_load_mw=(
                effective_it_load_mw
            ),

            pue=data.pue,

            facility_load_mw=(
                facility_load_mw
            ),

            cooling_technology=cooling_type,

            operating_hours_per_day=(
                data.operating_hours_per_day
            ),

            cooling_water_liters_per_kwh=(
                data.cooling_water_liters_per_kwh
            ),

            non_cooling_water_liters_per_kwh=(
                data.non_cooling_water_liters_per_kwh
            ),

            cooling_water_liters_per_day=(
                cooling_water_liters
            ),

            non_cooling_water_liters_per_day=(
                non_cooling_water_liters
            ),

            total_water_liters_per_day=(
                total_water_liters
            ),

            total_water_m3_per_day=(
                total_water_m3
            ),

            peak_water_m3_per_day=(
                peak_water_m3
            ),

            total_water_m3_per_month=(
                monthly_water_m3
            ),

            total_water_m3_per_year=(
                annual_water_m3
            ),

            water_intensity_liters_per_kwh=(
                water_intensity
            ),

            water_intensity_liters_per_it_kwh=(
                it_water_intensity
            ),

            cooling_share_percent=(
                cooling_share
            ),

            non_cooling_share_percent=(
                non_cooling_share
            ),

            demand_category=category,

            concerns=concerns,

            warnings=warnings,

            summary=summary,
        )

    # ========================================================
    # INVALID RESULT
    # ========================================================

    @staticmethod
    def invalid_result(
        data: DataCenterWaterDemandInput,
        errors: List[str],
    ) -> WaterDemandAssessment:
        """
        Return a safe invalid result rather than raising an
        exception through the API layer.
        """

        return WaterDemandAssessment(

            valid_input=False,

            it_load_mw=data.it_load_mw,

            utilization=data.utilization,

            effective_it_load_mw=0.0,

            pue=data.pue,

            facility_load_mw=0.0,

            cooling_technology=(
                data.cooling_technology
            ),

            operating_hours_per_day=(
                data.operating_hours_per_day
            ),

            cooling_water_liters_per_kwh=(
                data.cooling_water_liters_per_kwh
            ),

            non_cooling_water_liters_per_kwh=(
                data.non_cooling_water_liters_per_kwh
            ),

            cooling_water_liters_per_day=0.0,

            non_cooling_water_liters_per_day=0.0,

            total_water_liters_per_day=0.0,

            total_water_m3_per_day=0.0,

            peak_water_m3_per_day=0.0,

            total_water_m3_per_month=0.0,

            total_water_m3_per_year=0.0,

            water_intensity_liters_per_kwh=0.0,

            water_intensity_liters_per_it_kwh=0.0,

            cooling_share_percent=0.0,

            non_cooling_share_percent=0.0,

            demand_category="invalid",

            concerns=[
                "invalid_input"
            ],

            warnings=errors,

            summary=(
                "Water-demand calculation could not "
                "be completed because one or more "
                "inputs are invalid."
            ),
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def generate_summary(
        it_load_mw: float,
        effective_it_load_mw: float,
        facility_load_mw: float,
        cooling_type: str,
        daily_water_m3: float,
        annual_water_m3: float,
        water_intensity: float,
        category: str,
    ) -> str:

        return (
            f"The proposed data center has an IT "
            f"capacity of {it_load_mw:.2f} MW with "
            f"an estimated effective IT load of "
            f"{effective_it_load_mw:.2f} MW. "
            f"Estimated facility load is "
            f"{facility_load_mw:.2f} MW using "
            f"'{cooling_type}' cooling. "
            f"Estimated water demand is "
            f"{daily_water_m3:.2f} m³/day and "
            f"{annual_water_m3:.2f} m³/year. "
            f"Estimated water intensity is "
            f"{water_intensity:.3f} L/kWh. "
            f"The preliminary demand category is "
            f"'{category}'."
        )


# ============================================================
# PUBLIC API
# ============================================================


def analyze_water_demand(
    data: DataCenterWaterDemandInput,
) -> Dict[str, Any]:
    """
    Public service-layer function.
    """

    model: WaterDemandModel = (
        WaterDemandModel()
    )

    result: WaterDemandAssessment = (
        model.analyze(data)
    )

    return asdict(result)


# ============================================================
# DEVELOPMENT TEST
# ============================================================


if __name__ == "__main__":

    import json

    sample_input: DataCenterWaterDemandInput = (
        DataCenterWaterDemandInput(

            it_load_mw=50.0,

            utilization=0.70,

            pue=1.30,

            cooling_technology="water_cooled",

            cooling_water_liters_per_kwh=1.20,

            non_cooling_water_liters_per_kwh=0.05,

            operating_hours_per_day=24.0,

            peak_factor=1.25,
        )
    )

    model: WaterDemandModel = (
        WaterDemandModel()
    )

    result: WaterDemandAssessment = (
        model.analyze(
            sample_input
        )
    )

    print(
        json.dumps(
            asdict(result),
            indent=2,
            ensure_ascii=False,
        )
    )