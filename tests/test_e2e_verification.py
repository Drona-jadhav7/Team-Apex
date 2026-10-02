import urllib.request
import json

BASE = 'http://127.0.0.1:8000/api'

def run_tests():
    # 1. Test GET /sites
    req = urllib.request.urlopen(f'{BASE}/sites')
    sites = json.loads(req.read().decode())
    print(f"=== 1. GET /sites: {len(sites)} sites ===")
    for s in sites:
        print(f"Site: {s['site_name']} | Composite: {s['composite_score']} ({s['tier_badge']}) | Water: {s['water_score']} | Power: {s['power_score']} | Flags: {len(s['risk_flags'])}")

    # 2. Test GET /sites/{id}
    req2 = urllib.request.urlopen(f'{BASE}/sites/site_navi_mumbai')
    nm = json.loads(req2.read().decode())
    print("\n=== 2. GET /sites/site_navi_mumbai ===")
    print("Risk Flags:", nm['risk_flags'])
    print("Engineering Mandates:", nm['engineering_mandates'])

    # 3. Test POST /assess with custom payload
    custom_payload = {
        'site_name': 'Kochi Marine Data Park',
        'state': 'Kerala',
        'district': 'Ernakulam',
        'latitude': 9.9312,
        'longitude': 76.2673,
        'elevation_m': 4.5,
        'proposed_it_load_mw': 45.0,
        'water_params': {
            'groundwater_extraction_pct': 68.0,
            'water_quality_tds': 850.0,
            'demand_stress_score': 45.0,
            'data_center_demand_mld': 1.2,
            'local_aquifer_stress_pct': 70.0,
            'industrial_density_index': 65.0,
            'stp_distance_km': 3.0,
            'tertiary_supply_mld': 15.0,
            'assured_supply_mld': 2.0,
            'on_site_storage_hours': 36.0,
            'elevation_m': 4.5,
            'drought_risk_index': 20.0,
            'flood_zone_risk': 65.0
        },
        'power_params': {
            'substation_distance_km': 1.8,
            'voltage_class_kv': 220.0,
            'spare_mva_margin': 65.0,
            'proposed_it_load_mw': 45.0,
            'renewable_open_access_score': 85.0
        }
    }
    req3 = urllib.request.Request(
        f'{BASE}/assess',
        data=json.dumps(custom_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res3 = urllib.request.urlopen(req3)
    custom_res = json.loads(res3.read().decode())
    print("\n=== 3. POST /assess Custom Site ===")
    print("Site:", custom_res['site_name'])
    print(f"Composite: {custom_res['composite_score']} ({custom_res['tier']})")
    print("Flags fired:", custom_res['risk_flags'])
    print("Mandates issued:", custom_res['engineering_mandates'])

    # 4. Test POST /compare
    req4 = urllib.request.Request(
        f'{BASE}/compare',
        data=json.dumps({}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res4 = urllib.request.urlopen(req4)
    compare_res = json.loads(res4.read().decode())
    print("\n=== 4. POST /compare Summary ===")
    print(compare_res['comparison_summary'])
    print("Ranking:")
    for r in compare_res['ranked_sites']:
        print(f"Rank {r['rank']}: {r['site_name']} - {r['composite_score']} ({r['tier_badge']})")

    # 5. Check frontend HTML
    frontend_req = urllib.request.urlopen('http://127.0.0.1:5173/')
    print(f"\n=== 5. Frontend HTTP status: {frontend_req.getcode()} ===")

if __name__ == '__main__':
    run_tests()
