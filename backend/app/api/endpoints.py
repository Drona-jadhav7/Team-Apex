import json
import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path

from backend.app.models.schemas import (
    SiteInput,
    SiteAssessmentResponse,
    SiteComparisonRequest,
    SiteComparisonResponse,
)
from backend.app.services.aggregator import assess_site

router = APIRouter(tags=["Assessments"])

BENCHMARK_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "benchmark_sites.json"
)

def load_benchmark_sites() -> List[SiteInput]:
    if not os.path.exists(BENCHMARK_FILE):
        return []
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [SiteInput(**item) for item in data]

@router.get("/health")
def api_health():
    return {
        "status": "healthy",
        "service": "SuperIndia.ai API",
        "version": "1.0.0",
    }

@router.post("/assess", response_model=SiteAssessmentResponse)
def assess_site_endpoint(site: SiteInput):
    """
    Run deterministic 7-model water and 4-metric power assessment on candidate site.
    Returns composite score, tier, explainability breakdown, risk flags, and engineering mandates.
    """
    try:
        return assess_site(site)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment error: {str(e)}")

@router.get("/sites", response_model=List[SiteAssessmentResponse])
def get_benchmark_sites():
    """
    Retrieve pre-seeded ground truth assessments for 5 major Indian AI/data center hubs:
    Navi Mumbai, Noida, Bengaluru, Chennai, and Hyderabad.
    """
    sites = load_benchmark_sites()
    return [assess_site(site) for site in sites]

@router.get("/sites/{site_id}", response_model=SiteAssessmentResponse)
def get_site_by_id(site_id: str = Path(..., description="Unique ID of benchmark site")):
    """
    Retrieve single benchmark site assessment by ID.
    """
    sites = load_benchmark_sites()
    for site in sites:
        if site.site_id == site_id:
            return assess_site(site)
    raise HTTPException(status_code=404, detail=f"Site with ID '{site_id}' not found.")

@router.post("/compare", response_model=SiteComparisonResponse)
def compare_sites_endpoint(req: SiteComparisonRequest):
    """
    Multi-site audit and comparison matrix across water, power, and composite feasibility scores.
    """
    all_benchmarks = {s.site_id: s for s in load_benchmark_sites()}
    sites_to_assess: List[SiteInput] = []

    if req.site_ids:
        for sid in req.site_ids:
            if sid in all_benchmarks:
                sites_to_assess.append(all_benchmarks[sid])
            else:
                raise HTTPException(status_code=404, detail=f"Benchmark site '{sid}' not found")
    elif req.custom_sites:
        sites_to_assess.extend(req.custom_sites)
    else:
        # Default: compare all 5 benchmark sites
        sites_to_assess = list(all_benchmarks.values())

    assessments = [assess_site(s) for s in sites_to_assess]
    # Rank descending by composite score
    sorted_assessments = sorted(assessments, key=lambda a: a.composite_score, reverse=True)

    ranked_list = []
    for rank, item in enumerate(sorted_assessments, start=1):
        ranked_list.append({
            "rank": rank,
            "site_id": item.site_id,
            "site_name": item.site_name,
            "state": item.state,
            "composite_score": item.composite_score,
            "water_score": item.water_score,
            "power_score": item.power_score,
            "tier": item.tier,
            "tier_badge": item.tier_badge,
            "tier_color": item.tier_color,
            "risk_flags_count": len(item.risk_flags),
        })

    best_site = sorted_assessments[0].site_name if sorted_assessments else None
    summary = (
        f"Compared {len(sorted_assessments)} candidate hubs. "
        f"Top ranked site is '{best_site}' with Composite Score of {sorted_assessments[0].composite_score:.1f}/100 ({sorted_assessments[0].tier_badge})."
        if sorted_assessments else "No sites to compare."
    )

    return SiteComparisonResponse(
        sites=assessments,
        ranked_sites=ranked_list,
        best_site=best_site,
        comparison_summary=summary,
    )
