from typing import Dict, List
from backend.app.models.schemas import (
    PowerInput,
    SubMetricResult,
    PowerAssessmentOutput,
)

POWER_WEIGHTS: Dict[str, float] = {
    "substation_proximity": 0.30,
    "voltage_class": 0.30,
    "substation_spare_mva_margin": 0.20,
    "renewable_open_access_corridors": 0.20,
}

def evaluate_substation_proximity(params: PowerInput) -> SubMetricResult:
    """
    Metric 1: Substation Proximity (Weight: 0.30)
    Proximity to nearest EHV transmission substation reduces line losses,
    transmission line capex, and Right-of-Way (RoW) acquisition delays.
    """
    dist = params.substation_distance_km
    if dist <= 1.0:
        score = 100.0 - dist * 4.0
        category = "Immediate Proximity"
        details = f"{dist:.2f} km to EHV substation. Low transmission line capex and minimal RoW risk."
    elif dist <= 2.5:
        score = 96.0 - ((dist - 1.0) / 1.5) * 14.0
        category = "Close Proximity"
        details = f"{dist:.2f} km to EHV substation. Short dedicated cable route within industrial easement."
    elif dist <= 5.0:
        score = 82.0 - ((dist - 2.5) / 2.5) * 17.0
        category = "Moderate Distance"
        details = f"{dist:.2f} km to EHV substation. Feasible dedicated double-circuit line corridor."
    elif dist <= 10.0:
        score = 65.0 - ((dist - 5.0) / 5.0) * 20.0
        category = "Extended Distance"
        details = f"{dist:.2f} km to EHV substation. Substantial transmission line construction and RoW clearances."
    else:
        score = max(10.0, 45.0 - (dist - 10.0) * 2.5)
        category = "Distal / High RoW Risk"
        details = f"{dist:.2f} km to EHV substation. Severe transmission corridor latency and line losses."

    score = round(max(0.0, min(100.0, score)), 2)
    weight = POWER_WEIGHTS["substation_proximity"]
    return SubMetricResult(
        name="Substation Proximity",
        key="substation_proximity",
        score=score,
        weight=weight,
        weighted_score=round(score * weight, 2),
        category=category,
        details=details,
        flagged=(dist > 5.0),
    )

def evaluate_voltage_class(params: PowerInput) -> SubMetricResult:
    """
    Metric 2: Voltage Class (Weight: 0.30)
    Derived from CEA Transmission Planning criteria.
    Higher voltage levels support gigawatt-scale AI load with minimal thermal limits.
    """
    kv = params.voltage_class_kv
    if kv >= 400.0:
        score = 100.0
        category = "400 kV (Extra High Voltage / Bulk)"
        details = f"{kv:.0f} kV EHV grid connection. Ideal for hyperscale AI compute clusters (50MW-200MW+)."
    elif kv >= 220.0:
        score = 85.0 + min(5.0, (kv - 220.0) * 0.5)
        category = "220-230 kV (High Voltage Transmission)"
        details = f"{kv:.0f} kV HV transmission line. Benchmark standard for Indian hyperscale data centers."
    elif kv >= 132.0:
        score = 70.0 + min(5.0, (kv - 132.0) * 0.1)
        category = "110-132 kV (Sub-Transmission)"
        details = f"{kv:.0f} kV connection. Adequate for 20-50 MW capacity; requires dual dedicated bays."
    elif kv >= 66.0:
        score = 50.0 + min(8.0, (kv - 66.0) * 0.2)
        category = "33-66 kV (Medium Industrial Feed)"
        details = f"{kv:.0f} kV connection. Constrained for large-scale GPU training clusters; colocation grade."
    else:
        score = max(15.0, (kv / 33.0) * 45.0)
        category = "11 kV (Distribution Level)"
        details = f"{kv:.0f} kV distribution level. Severe capacity bottleneck; unsuitable for AI workloads."

    score = round(max(0.0, min(100.0, score)), 2)
    weight = POWER_WEIGHTS["voltage_class"]
    return SubMetricResult(
        name="Voltage Class",
        key="voltage_class",
        score=score,
        weight=weight,
        weighted_score=round(score * weight, 2),
        category=category,
        details=details,
        flagged=(kv < 132.0),
    )

def evaluate_substation_spare_mva_margin(params: PowerInput) -> SubMetricResult:
    """
    Metric 3: Substation Spare MVA Margin (Weight: 0.20)
    Evaluates available N-1 contingency transformer headroom at the serving substation.
    """
    spare = params.spare_mva_margin
    load = params.proposed_it_load_mw

    if spare >= 120.0:
        score = 98.0
        category = "Generous Headroom (>= 120 MVA)"
        details = f"{spare:.0f} MVA spare N-1 transformer capacity available (substantially exceeds {load:.0f} MW load)."
    elif spare >= 80.0:
        score = 85.0 + ((spare - 80.0) / 40.0) * 12.0
        category = "Substantial Headroom (80-120 MVA)"
        details = f"{spare:.0f} MVA spare margin provides immediate allocation for {load:.0f} MW compute."
    elif spare >= 40.0:
        score = 65.0 + ((spare - 40.0) / 40.0) * 19.0
        category = "Moderate Headroom (40-80 MVA)"
        details = f"{spare:.0f} MVA spare headroom. Sufficient for initial phase, but power utility augmentation needed for scaling."
    elif spare >= 20.0:
        score = 45.0 + ((spare - 20.0) / 20.0) * 19.0
        category = "Constrained Headroom (20-40 MVA)"
        details = f"{spare:.0f} MVA spare margin. Tight N-1 margin; risk of utility sanction delays."
    else:
        score = max(10.0, (spare / 20.0) * 44.0)
        category = "Deficient Margin (< 20 MVA)"
        details = f"{spare:.0f} MVA spare capacity is critically deficient for {load:.0f} MW. Captive GIS substation required."

    score = round(max(0.0, min(100.0, score)), 2)
    weight = POWER_WEIGHTS["substation_spare_mva_margin"]
    return SubMetricResult(
        name="Substation Spare MVA Margin",
        key="substation_spare_mva_margin",
        score=score,
        weight=weight,
        weighted_score=round(score * weight, 2),
        category=category,
        details=details,
        flagged=(spare < 40.0),
    )

def evaluate_renewable_open_access_corridors(params: PowerInput) -> SubMetricResult:
    """
    Metric 4: Renewable Open Access Corridors (Weight: 0.20)
    Measures compliance with MoP Green Energy Open Access Rules 2022, ISTS connectivity,
    and regional solar/wind PPA wheeling feasibility.
    """
    score = round(max(0.0, min(100.0, params.renewable_open_access_score)), 2)

    if score >= 85.0:
        category = "Prime Clean Energy Corridor"
        details = f"Score {score:.1f}/100. Direct access to ISTS Green Energy Corridor with streamlined PPA wheeling."
    elif score >= 70.0:
        category = "Strong Open Access Readiness"
        details = f"Score {score:.1f}/100. Favorable state open-access policy with established solar/wind captive avenues."
    elif score >= 50.0:
        category = "Moderate Open Access Friction"
        details = f"Score {score:.1f}/100. Subject to cross-subsidy surcharges or wheeling congestion during peak hours."
    else:
        category = "High Regulatory Friction"
        details = f"Score {score:.1f}/100. Limited green open access; high transmission wheeling tariffs and banking restrictions."

    weight = POWER_WEIGHTS["renewable_open_access_corridors"]
    return SubMetricResult(
        name="Renewable Open Access Corridors",
        key="renewable_open_access_corridors",
        score=score,
        weight=weight,
        weighted_score=round(score * weight, 2),
        category=category,
        details=details,
        flagged=(score < 50.0),
    )

def calculate_power_assessment(params: PowerInput) -> PowerAssessmentOutput:
    """
    Evaluates the 4-metric electrical grid pipeline according to Hackathon specifications:
    Power Score = sum(Score_j * Weight_j)
    """
    sub_metrics: List[SubMetricResult] = [
        evaluate_substation_proximity(params),
        evaluate_voltage_class(params),
        evaluate_substation_spare_mva_margin(params),
        evaluate_renewable_open_access_corridors(params),
    ]

    total_weighted_score = sum(sm.weighted_score for sm in sub_metrics)
    power_score = round(total_weighted_score, 2)

    if power_score >= 80.0:
        summary = "Exceptional electrical reliability with high-voltage EHV connectivity and ample N-1 transformer headroom."
    elif power_score >= 65.0:
        summary = "Robust grid access; minor transmission extension or utility bay sanction required."
    elif power_score >= 50.0:
        summary = "Moderate power feasibility; constrained substation spare capacity demands proactive grid investment."
    else:
        summary = "High electrical grid vulnerability; low voltage class or severe transformer headroom bottleneck."

    return PowerAssessmentOutput(
        power_score=power_score,
        weights=POWER_WEIGHTS,
        sub_metrics=sub_metrics,
        summary=summary,
    )
