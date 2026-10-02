from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class WaterInput(BaseModel):
    groundwater_extraction_pct: float = Field(
        75.0, description="CGWA groundwater stage of extraction percentage"
    )
    water_quality_tds: float = Field(
        500.0, description="Total Dissolved Solids in mg/L (BIS 10500)"
    )
    demand_stress_score: Optional[float] = Field(
        None, description="Explicit demand stress score 0-100 or computed dynamically"
    )
    data_center_demand_mld: float = Field(
        1.5, description="Projected data center cooling & operational water demand in MLD"
    )
    local_aquifer_stress_pct: float = Field(
        65.0, description="Local competing aquifer draft & industrial stress percentage"
    )
    industrial_density_index: float = Field(
        60.0, description="Industrial density index (0-100)"
    )
    stp_distance_km: float = Field(
        4.0, description="Distance to nearest STP / CETP tertiary treatment plant in km"
    )
    tertiary_supply_mld: float = Field(
        20.0, description="Tertiary treated recycled greywater availability in MLD"
    )
    assured_supply_mld: float = Field(
        2.5, description="Assured municipal / canal / industrial pipeline water supply in MLD"
    )
    on_site_storage_hours: float = Field(
        48.0, description="Dedicated on-site emergency water storage headroom in hours (72h buffer target)"
    )
    elevation_m: float = Field(
        25.0, description="Site ground surface elevation in meters above sea level"
    )
    drought_risk_index: float = Field(
        30.0, description="Climate drought vulnerability index 0-100"
    )
    flood_zone_risk: float = Field(
        20.0, description="100-year flood zone vulnerability index 0-100"
    )

class PowerInput(BaseModel):
    substation_distance_km: float = Field(
        2.0, description="Distance to nearest 400kV/220kV EHV substation in km"
    )
    voltage_class_kv: float = Field(
        220.0, description="Interconnection voltage class in kV (400, 220, 132, 66, 33, 11)"
    )
    spare_mva_margin: float = Field(
        80.0, description="Substation spare N-1 transformer headroom margin in MVA"
    )
    proposed_it_load_mw: float = Field(
        50.0, description="Proposed AI data center IT load in MW"
    )
    renewable_open_access_score: float = Field(
        75.0, description="Renewable Open Access / ISTS corridor accessibility score (0-100)"
    )

class SiteInput(BaseModel):
    site_id: Optional[str] = None
    site_name: str = Field(..., description="Name of the candidate site / hub")
    state: str = Field(..., description="State name")
    district: str = Field(..., description="District name")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    elevation_m: float = Field(25.0, description="Ground elevation in meters")
    proposed_it_load_mw: float = Field(50.0, description="Target IT load in MW")
    water_params: WaterInput = Field(default_factory=WaterInput)
    power_params: PowerInput = Field(default_factory=PowerInput)

class SubMetricResult(BaseModel):
    name: str
    key: str
    score: float
    weight: float
    weighted_score: float
    category: str
    details: str
    flagged: bool = False

class WaterAssessmentOutput(BaseModel):
    water_score: float
    weights: Dict[str, float]
    sub_metrics: List[SubMetricResult]
    stress_flag_triggered: bool
    summary: str

class PowerAssessmentOutput(BaseModel):
    power_score: float
    weights: Dict[str, float]
    sub_metrics: List[SubMetricResult]
    summary: str

class SiteAssessmentResponse(BaseModel):
    site_id: Optional[str] = None
    site_name: str
    state: str
    district: str
    latitude: float
    longitude: float
    elevation_m: float
    proposed_it_load_mw: float
    composite_score: float
    tier: str
    tier_badge: str
    tier_color: str
    water_score: float
    power_score: float
    water_assessment: WaterAssessmentOutput
    power_assessment: PowerAssessmentOutput
    risk_flags: List[str]
    engineering_mandates: List[str]
    diagnostics: List[str]
    timestamp: str

class SiteComparisonRequest(BaseModel):
    site_ids: Optional[List[str]] = None
    custom_sites: Optional[List[SiteInput]] = None

class SiteComparisonResponse(BaseModel):
    sites: List[SiteAssessmentResponse]
    ranked_sites: List[Dict[str, Any]]
    best_site: Optional[str]
    comparison_summary: str
