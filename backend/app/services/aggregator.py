from datetime import datetime
from typing import List, Tuple
from backend.app.models.schemas import (
    SiteInput,
    SiteAssessmentResponse,
)
from backend.app.services.water_engine import calculate_water_assessment
from backend.app.services.power_engine import calculate_power_assessment

def assess_site(site: SiteInput) -> SiteAssessmentResponse:
    """
    Core Architecture Principle:
    'One model -> one responsibility -> domain aggregator -> composite site assessment.'
    
    Composite Site Score = (Water Score * 0.45) + (Power Score * 0.55)
    
    Classification Tiers:
      >= 75.0: VIABLE / RECOMMENDED (Green)
      50.0 - 74.9: CONDITIONAL / HIGH RISK (Amber)
      < 50.0: UNVIABLE / REJECT (Red)
    """
    # 1. Run Water Engine
    water_result = calculate_water_assessment(site.water_params)
    water_score = water_result.water_score

    # 2. Run Power Engine
    power_result = calculate_power_assessment(site.power_params)
    power_score = power_result.power_score

    # 3. Composite Calculation
    composite_score = round((water_score * 0.45) + (power_score * 0.55), 2)

    # 4. Classification Tiers
    if composite_score >= 75.0:
        tier = "VIABLE / RECOMMENDED"
        tier_badge = "VIABLE"
        tier_color = "#10B981"  # Emerald green
    elif composite_score >= 50.0:
        tier = "CONDITIONAL / HIGH RISK"
        tier_badge = "CONDITIONAL"
        tier_color = "#F59E0B"  # Amber
    else:
        tier = "UNVIABLE / REJECT"
        tier_badge = "UNVIABLE"
        tier_color = "#EF4444"  # Red

    # 5. Automated Diagnostic & Mitigation Engine
    risk_flags: List[str] = []
    engineering_mandates: List[str] = []
    diagnostics: List[str] = []

    # Specific Mandate 1: If Demand Stress <= 50
    demand_metric = next(
        (sm for sm in water_result.sub_metrics if sm.key == "demand_stress"), None
    )
    demand_stress_score = demand_metric.score if demand_metric else 100.0

    if demand_stress_score <= 50.0:
        risk_flags.append("Competitive industrial extraction stress")
        engineering_mandates.append(
            "1. Deploy on-site closed-loop cooling towers. 2. Tap MIDC CETP tertiary treated greywater to avoid municipal cuts."
        )
        diagnostics.append(
            f"Demand stress score ({demand_stress_score:.1f}/100) breached the <= 50 threshold due to severe competing regional water abstraction."
        )
    elif demand_stress_score < 60.0:
        risk_flags.append("Moderate industrial demand stress (Warning)")
        diagnostics.append(
            f"Demand stress score ({demand_stress_score:.1f}/100) triggered automated stress flag (< 60 threshold)."
        )

    # Specific Mandate 2: If Coastal / Flood Elevation < 10m
    # Check site elevation or water params elevation
    site_elevation = min(site.elevation_m, site.water_params.elevation_m)
    if site_elevation < 10.0:
        risk_flags.append("100-year flood zone & CRZ restrictions")
        engineering_mandates.append("Unviable for sub-grade electrical infrastructure.")
        diagnostics.append(
            f"Site ground elevation ({site_elevation:.1f}m) is below the 10m threshold; vulnerable to high-tide coastal surge and Coastal Regulation Zone (CRZ) clauses."
        )

    # Additional Domain Diagnostics & Engineering Mandates
    # Substation distance > 5km
    if site.power_params.substation_distance_km > 5.0:
        risk_flags.append("Transmission Right-of-Way (RoW) acquisition latency")
        engineering_mandates.append(
            "Construct dedicated EHV transmission line corridor with redundant dual-circuit bays."
        )
        diagnostics.append(
            f"Substation distance is {site.power_params.substation_distance_km:.2f} km; high risk of easement dispute and line construction delays."
        )

    # Substation spare margin < 40 MVA
    if site.power_params.spare_mva_margin < 40.0:
        risk_flags.append("Constrained N-1 contingency grid margin")
        engineering_mandates.append(
            "Require captive Gas Insulated Substation (GIS) or upfront utility transformer augmentation."
        )
        diagnostics.append(
            f"Substation spare capacity ({site.power_params.spare_mva_margin:.0f} MVA) cannot guarantee N-1 contingency for {site.proposed_it_load_mw:.0f} MW IT load."
        )

    # Storage Headroom < 72 hours
    if site.water_params.on_site_storage_hours < 72.0:
        risk_flags.append("Sub-72-hour emergency cooling buffer vulnerability")
        engineering_mandates.append(
            "Expand on-site water reservoir or install atmospheric water generation (AWG) standby system."
        )
        diagnostics.append(
            f"On-site water storage ({site.water_params.on_site_storage_hours:.0f}h) fails the 72-hour autonomous data center cooling requirement."
        )

    # Groundwater extraction over-exploited (> 100%)
    if site.water_params.groundwater_extraction_pct > 100.0:
        risk_flags.append("Over-exploited CGWA groundwater basin")
        engineering_mandates.append(
            "Enforce 100% zero-liquid discharge (ZLD) closed-loop cooling and compulsory rainwater aquifer recharge."
        )
        diagnostics.append(
            f"CGWA groundwater extraction is at {site.water_params.groundwater_extraction_pct:.1f}%; commercial borehole drilling prohibited by law."
        )

    # Water Quality TDS > 1000 mg/L
    if site.water_params.water_quality_tds > 1000.0:
        risk_flags.append("High salinity / mineral scaling risk")
        engineering_mandates.append(
            "Install industrial reverse-osmosis (RO) softening plant with anti-scalant chemical dosing."
        )
        diagnostics.append(
            f"Feedwater TDS is {site.water_params.water_quality_tds:.0f} mg/L; high risk of cooling tower heat exchanger fouling."
        )

    # If no risk flags triggered
    if not risk_flags:
        diagnostics.append(
            "All water and power infrastructure parameters satisfy CEA/CGWA greenfield criteria without primary blocking flags."
        )
        engineering_mandates.append(
            "Standard dual-source utility interconnection and dual-pipe greywater metering recommended."
        )

    return SiteAssessmentResponse(
        site_id=site.site_id,
        site_name=site.site_name,
        state=site.state,
        district=site.district,
        latitude=site.latitude,
        longitude=site.longitude,
        elevation_m=site_elevation,
        proposed_it_load_mw=site.proposed_it_load_mw,
        composite_score=composite_score,
        tier=tier,
        tier_badge=tier_badge,
        tier_color=tier_color,
        water_score=water_score,
        power_score=power_score,
        water_assessment=water_result,
        power_assessment=power_result,
        risk_flags=risk_flags,
        engineering_mandates=engineering_mandates,
        diagnostics=diagnostics,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
