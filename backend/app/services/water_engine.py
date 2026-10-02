from typing import Dict, List, Tuple
from backend.app.models.schemas import (
    WaterInput,
    SubMetricResult,
    WaterAssessmentOutput,
)

WATER_WEIGHTS: Dict[str, float] = {
    "water_availability": 0.15,
    "water_quality": 0.15,
    "demand_stress": 0.15,
    "reuse_effluent_proximity": 0.15,
    "supply_demand_balance": 0.20,
    "storage_headroom": 0.10,
    "climate_resilience": 0.10,
}

def evaluate_water_availability(params: WaterInput) -> SubMetricResult:
    """
    Sub-model 1: Water Availability (Weight: 0.15)
    Derived from Central Ground Water Authority (CGWA) Stage of Groundwater Extraction.
    """
    gw_pct = params.groundwater_extraction_pct
    if gw_pct <= 65.0:
        score = 95.0 - (gw_pct / 65.0) * 10.0
        category = "Safe (CGWA Zone)"
        details = f"Aquifer extraction at {gw_pct:.1f}% (Safe CGWA category, high recharge headroom)."
    elif gw_pct <= 70.0:
        score = 85.0 - ((gw_pct - 65.0) / 5.0) * 10.0
        category = "Safe / Moderate"
        details = f"Aquifer extraction at {gw_pct:.1f}% (Approaching semi-critical CGWA boundary)."
    elif gw_pct <= 90.0:
        score = 75.0 - ((gw_pct - 70.0) / 20.0) * 20.0
        category = "Semi-Critical (CGWA Zone)"
        details = f"Aquifer extraction at {gw_pct:.1f}% (Semi-critical; NOC permits required from CGWA)."
    elif gw_pct <= 100.0:
        score = 55.0 - ((gw_pct - 90.0) / 10.0) * 20.0
        category = "Critical (CGWA Zone)"
        details = f"Aquifer extraction at {gw_pct:.1f}% (Critical extraction zone; strict extraction ceilings)."
    else:
        score = max(10.0, 35.0 - (gw_pct - 100.0) * 1.2)
        category = "Over-Exploited (CGWA Zone)"
        details = f"Aquifer extraction at {gw_pct:.1f}% (Over-exploited; commercial groundwater extraction prohibited)."

    score = round(max(0.0, min(100.0, score)), 2)
    weight = WATER_WEIGHTS["water_availability"]
    return SubMetricResult(
        name="Water Availability",
        key="water_availability",
        score=score,
        weight=weight,
        weighted_score=round(score * weight, 2),
        category=category,
        details=details,
        flagged=(score < 50.0),
    )

def evaluate_water_quality(params: WaterInput) -> SubMetricResult:
    """
    Sub-model 2: Water Quality (Weight: 0.15)
    Derived from Total Dissolved Solids (TDS in mg/L) per BIS 10500 standards
    and industrial cooling tower scaling/fouling dynamics.
    """
    tds = params.water_quality_tds
    if tds <= 300.0:
        score = 98.0 - (tds / 300.0) * 8.0
        category = "Optimal (Low Mineral)"
        details = f"TDS at {tds:.0f} mg/L (High purity surface/treated water; minimal scaling risk)."
    elif tds <= 500.0:
        score = 90.0 - ((tds - 300.0) / 200.0) * 12.0
        category = "Desirable (BIS 10500)"
        details = f"TDS at {tds:.0f} mg/L (Within BIS acceptable limit of 500 mg/L; standard filtration)."
    elif tds <= 1000.0:
        score = 78.0 - ((tds - 500.0) / 500.0) * 22.0
        category = "Moderate Hardness"
        details = f"TDS at {tds:.0f} mg/L (Moderate mineral load; demands anti-scalant dosing & softener)."
    elif tds <= 2000.0:
        score = 56.0 - ((tds - 1000.0) / 1000.0) * 24.0
        category = "Permissible / High Scaling"
        details = f"TDS at {tds:.0f} mg/L (At BIS 2000 mg/L upper ceiling; RO pre-treatment mandatory)."
    else:
        score = max(10.0, 32.0 - ((tds - 2000.0) / 1000.0) * 15.0)
        category = "Brackish / Severe Fouling"
        details = f"TDS at {tds:.0f} mg/L (Severe salinity; requires industrial high-recovery RO/ZLD)."

    score = round(max(0.0, min(100.0, score)), 2)
    weight = WATER_WEIGHTS["water_quality"]
    return SubMetricResult(
        name="Water Quality",
        key="water_quality",
        score=score,
        weight=weight,
        weighted_score=round(score * weight, 2),
        category=category,
        details=details,
        flagged=(score < 50.0),
    )

def evaluate_demand_stress(params: WaterInput) -> SubMetricResult:
    """
    Sub-model 3: Demand Stress (Weight: 0.15)
    Quantifies competing industrial extraction stress and local water scarcity.
    CRITICAL SPECIFICATION: Sub-score < 60 must trigger an automated Stress Flag.
    """
    if params.demand_stress_score is not None:
        score = float(params.demand_stress_score)
    else:
        # Calculate from composite industrial and aquifer draw
        composite_stress = 0.55 * params.local_aquifer_stress_pct + 0.45 * params.industrial_density_index
        score = 100.0 - (composite_stress - 20.0) * 1.15

    score = round(max(0.0, min(100.0, score)), 2)
    stress_flag = (score < 60.0)

    if score >= 80.0:
        category = "Low Stress"
        details = f"Stress score {score:.1f}/100. Ample basin headroom with low competitive industrial draw."
    elif score >= 60.0:
        category = "Moderate Stress"
        details = f"Stress score {score:.1f}/100. Manageable industrial baseline with seasonal fluctuation."
    elif score >= 50.0:
        category = "High Stress (Flagged)"
        details = f"Stress score {score:.1f}/100. Elevated industrial extraction stress (< 60 threshold triggered)."
    else:
        category = "Severe Stress (Flagged)"
        details = f"Stress score {score:.1f}/100. Critical competitive extraction stress (< 50 threshold breached)."

    weight = WATER_WEIGHTS["demand_stress"]
    return SubMetricResult(
        name="Demand Stress",
        key="demand_stress",
        score=score,
        weight=weight,
        weighted_score=round(score * weight, 2),
        category=category,
        details=details,
        flagged=stress_flag,
    )

def evaluate_reuse_effluent_proximity(params: WaterInput) -> SubMetricResult:
    """
    Sub-model 4: Reuse & Effluent Proximity (Weight: 0.15)
    Evaluates proximity to Sewage Treatment Plants (STP) / CETP for tertiary treated greywater cooling.
    """
    dist = params.stp_distance_km
    supply = params.tertiary_supply_mld

    if dist <= 2.0:
        base_score = 98.0 - (dist / 2.0) * 6.0
        cat = "Immediate Direct Access"
    elif dist <= 5.0:
        base_score = 92.0 - ((dist - 2.0) / 3.0) * 14.0
        cat = "Feasible Pipeline Corridor"
    elif dist <= 10.0:
        base_score = 78.0 - ((dist - 5.0) / 5.0) * 22.0
        cat = "Intermediate Transit Distance"
    elif dist <= 15.0:
        base_score = 56.0 - ((dist - 10.0) / 5.0) * 20.0
        cat = "Distant Pipeline Corridor"
    else:
        base_score = max(10.0, 36.0 - (dist - 15.0) * 1.5)
        cat = "Unviable Dual-Pipe Distance"

    # Volume adequacy adjustment (boost if tertiary supply > 10 MLD)
    volume_bonus = min(5.0, (supply / 20.0) * 5.0)
    score = round(max(0.0, min(100.0, base_score + volume_bonus)), 2)

    details = f"Nearest STP/CETP {dist:.1f} km away with {supply:.1f} MLD tertiary treated capacity."
    weight = WATER_WEIGHTS["reuse_effluent_proximity"]
    return SubMetricResult(
        name="Reuse & Effluent Proximity",
        key="reuse_effluent_proximity",
        score=score,
        weight=weight,
        weighted_score=round(score * weight, 2),
        category=cat,
        details=details,
        flagged=(score < 50.0),
    )

def evaluate_supply_demand_balance(params: WaterInput) -> SubMetricResult:
    """
    Sub-model 5: Supply vs Demand Balance (Weight: 0.20)
    Calculates safety ratio of assured supply MLD vs data center demand MLD.
    """
    demand = max(0.1, params.data_center_demand_mld)
    supply = params.assured_supply_mld
    ratio = supply / demand

    if ratio >= 2.5:
        score = 100.0
        category = "Substantial Surplus"
        details = f"Assured supply is {ratio:.2f}x of projected AI cooling demand ({supply:.2f} MLD vs {demand:.2f} MLD)."
    elif ratio >= 1.8:
        score = 88.0 + ((ratio - 1.8) / 0.7) * 11.0
        category = "Comfortable Surplus"
        details = f"Assured supply is {ratio:.2f}x of projected AI cooling demand ({supply:.2f} MLD vs {demand:.2f} MLD)."
    elif ratio >= 1.3:
        score = 72.0 + ((ratio - 1.3) / 0.5) * 16.0
        category = "Adequate Balance"
        details = f"Assured supply is {ratio:.2f}x of demand; seasonal rationing requires buffer planning."
    elif ratio >= 1.0:
        score = 55.0 + ((ratio - 1.0) / 0.3) * 17.0
        category = "Tight Supply Margin"
        details = f"Assured supply is {ratio:.2f}x of demand; near-zero margin for thermal peaking."
    else:
        score = max(5.0, ratio * 50.0)
        category = "Deficit State"
        details = f"Supply deficit! Assured supply is only {ratio:.2f}x of demand ({supply:.2f} MLD vs {demand:.2f} MLD)."

    score = round(max(0.0, min(100.0, score)), 2)
    weight = WATER_WEIGHTS["supply_demand_balance"]
    return SubMetricResult(
        name="Supply vs Demand Balance",
        key="supply_demand_balance",
        score=score,
        weight=weight,
        weighted_score=round(score * weight, 2),
        category=category,
        details=details,
        flagged=(score < 55.0),
    )

def evaluate_storage_headroom(params: WaterInput) -> SubMetricResult:
    """
    Sub-model 6: Storage Headroom / 72hr Buffer (Weight: 0.10)
    Measures dedicated on-site emergency reservoir buffer hours against the 72h mission-critical target.
    """
    hours = params.on_site_storage_hours
    if hours >= 72.0:
        score = 100.0
        category = "Target Met (>= 72h)"
        details = f"{hours:.0f} hours on-site storage capacity complies with the full 72-hour autonomous cooling mandate."
    elif hours >= 48.0:
        score = 75.0 + ((hours - 48.0) / 24.0) * 24.0
        category = "Intermediate Buffer (48-72h)"
        details = f"{hours:.0f} hours on-site buffer (48h baseline met; below recommended 72h standard)."
    elif hours >= 24.0:
        score = 50.0 + ((hours - 24.0) / 24.0) * 25.0
        category = "Minimal Buffer (24-48h)"
        details = f"{hours:.0f} hours on-site buffer; vulnerable to municipal supply curtailment exceeding 24h."
    else:
        score = max(5.0, (hours / 24.0) * 50.0)
        category = "Deficient Buffer (< 24h)"
        details = f"Critically deficient! Only {hours:.0f} hours buffer; high risk of emergency thermal throttling."

    score = round(max(0.0, min(100.0, score)), 2)
    weight = WATER_WEIGHTS["storage_headroom"]
    return SubMetricResult(
        name="Storage Headroom (72hr Buffer)",
        key="storage_headroom",
        score=score,
        weight=weight,
        weighted_score=round(score * weight, 2),
        category=category,
        details=details,
        flagged=(score < 60.0),
    )

def evaluate_climate_resilience(params: WaterInput) -> SubMetricResult:
    """
    Sub-model 7: Climate Resilience (Weight: 0.10)
    Combines meteorological drought vulnerability, flood zone exposure, and coastal elevation.
    """
    elev = params.elevation_m
    drought = params.drought_risk_index
    flood = params.flood_zone_risk

    # Penalty for low elevation coastal storm surge (< 10m)
    coastal_penalty = 22.0 if elev < 10.0 else (10.0 if elev < 15.0 else 0.0)
    raw_resilience = 100.0 - (0.42 * drought + 0.38 * flood + coastal_penalty)
    score = round(max(10.0, min(100.0, raw_resilience)), 2)

    if score >= 80.0:
        category = "High Climate Resilience"
        details = f"Resilience score {score:.1f}/100. Elevation {elev:.1f}m, low drought index ({drought:.0f})."
    elif score >= 60.0:
        category = "Moderate Climate Resilience"
        details = f"Resilience score {score:.1f}/100. Elevation {elev:.1f}m with moderate hydrological risk."
    elif score >= 45.0:
        category = "Vulnerable to Extremes"
        details = f"Resilience score {score:.1f}/100. Elevated flood ({flood:.0f}) or drought risk ({drought:.0f})."
    else:
        category = "Severe Climate Exposure"
        details = f"Resilience score {score:.1f}/100. Critical exposure to coastal storm surge or drought."

    weight = WATER_WEIGHTS["climate_resilience"]
    return SubMetricResult(
        name="Climate Resilience",
        key="climate_resilience",
        score=score,
        weight=weight,
        weighted_score=round(score * weight, 2),
        category=category,
        details=details,
        flagged=(score < 50.0 or elev < 10.0),
    )

def calculate_water_assessment(params: WaterInput) -> WaterAssessmentOutput:
    """
    Runs the 7-model water pipeline and aggregates scores according to Hackathon specifications:
    Water Score = sum(Score_i * Weight_i)
    """
    sub_metrics: List[SubMetricResult] = [
        evaluate_water_availability(params),
        evaluate_water_quality(params),
        evaluate_demand_stress(params),
        evaluate_reuse_effluent_proximity(params),
        evaluate_supply_demand_balance(params),
        evaluate_storage_headroom(params),
        evaluate_climate_resilience(params),
    ]

    total_weighted_score = sum(sm.weighted_score for sm in sub_metrics)
    water_score = round(total_weighted_score, 2)

    # Check automated stress flag on demand stress
    demand_metric = next(sm for sm in sub_metrics if sm.key == "demand_stress")
    stress_flag_triggered = demand_metric.flagged

    if water_score >= 80.0:
        summary = "Excellent hydrological foundation with robust supply-demand balance and treated water access."
    elif water_score >= 65.0:
        summary = "Viable water profile; requires monitored graywater recycling and buffer enforcement."
    elif water_score >= 50.0:
        summary = "Constrained hydrological environment with significant aquifer pressure or quality issues."
    else:
        summary = "Severe water deficit or critical aquifer stress; high risk of operational water curtailment."

    return WaterAssessmentOutput(
        water_score=water_score,
        weights=WATER_WEIGHTS,
        sub_metrics=sub_metrics,
        stress_flag_triggered=stress_flag_triggered,
        summary=summary,
    )
