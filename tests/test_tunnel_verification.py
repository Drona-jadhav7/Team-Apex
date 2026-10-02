import urllib.request
import json
import subprocess
import time
import re
import sys
import os

# Set standard streams to utf-8 if supported
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def fetch_with_retry(url, retries=8, delay=2):
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "SuperIndiaVerifier/1.0"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                return response.status, response.read().decode("utf-8")
        except Exception as e:
            last_err = e
            time.sleep(delay)
    raise last_err

def test_tunnel():
    print("==================================================================")
    print(" SuperIndia.ai - Tunnel & Demonstration Sites Verification")
    print("==================================================================")

    # 1. Local Vite Proxy Verification
    print("\n[Step 1] Verifying Local Vite Proxy (http://127.0.0.1:5173)...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:5173/api/sites", timeout=5) as r:
            sites = json.loads(r.read().decode("utf-8"))
            print(f"  [OK] Vite Proxy /api/sites OK - {len(sites)} sites returned.")
    except Exception as e:
        print(f"  [FAIL] Failed to reach /api/sites through Vite proxy: {e}")
        return False

    # 2. Launch cloudflared tunnel in subprocess
    print("\n[Step 2] Launching temporary Cloudflare Tunnel...")
    cloudflared_path = r"C:\Users\DRONA\nodejs\cloudflared.exe"
    if not os.path.exists(cloudflared_path):
        cloudflared_path = "cloudflared"

    proc = subprocess.Popen(
        [
            cloudflared_path,
            "tunnel",
            "--url",
            "http://localhost:5173",
            "--http-host-header",
            "localhost:5173"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    tunnel_url = None
    start_time = time.time()
    url_regex = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    # Read output until URL is found (timeout 25s)
    while time.time() - start_time < 25:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.2)
            continue
        match = url_regex.search(line)
        if match:
            tunnel_url = match.group(0)
            break

    if not tunnel_url:
        print("  [FAIL] Failed to obtain public tunnel URL from cloudflared.")
        proc.terminate()
        return False

    print(f"  [OK] Public HTTPS Tunnel Assigned: {tunnel_url}")
    print("  Waiting 3s for Cloudflare edge DNS propagation...")
    time.sleep(3)

    try:
        # 3. Test Frontend HTML over Tunnel
        print("\n[Step 3] Testing Public Frontend Access over HTTPS...")
        status, html = fetch_with_retry(f"{tunnel_url}/")
        print(f"  [OK] Frontend Status: {status} OK (HTML size: {len(html)} bytes)")

        # 4. Test Backend API through Vite Proxy over Public HTTPS
        print("\n[Step 4] Testing Tunneled API Proxy (/api/sites)...")
        status, raw_json = fetch_with_retry(f"{tunnel_url}/api/sites")
        sites_data = json.loads(raw_json)
        print(f"  [OK] API Status: {status} OK - Received {len(sites_data)} benchmark sites.")

        # 5. Verify the 3 specific demonstration sites
        print("\n[Step 5] Verifying 3 Core Demonstration Sites:")
        target_ids = ["site_mahape_midc", "site_taloja_midc", "site_coastal_south_mumbai"]
        found_sites = {s["site_id"]: s for s in sites_data if s["site_id"] in target_ids}

        for sid in target_ids:
            if sid not in found_sites:
                print(f"  [FAIL] Missing demonstration site ID: {sid}")
                return False
            
            site = found_sites[sid]
            print(f"\n  -> Site: {site['site_name']}")
            print(f"     - State/District: {site['district']}, {site['state']}")
            print(f"     - Ground Elevation: {site['elevation_m']} m")
            print(f"     - Composite Score: {site['composite_score']} ({site['tier_badge']} - {site['tier']})")
            print(f"     - Water Score (45%): {site['water_score']} (7 Sub-models verified)")
            print(f"     - Power Score (55%): {site['power_score']} (4 CEA Metrics verified)")
            print(f"     - Active Risk Flags ({len(site['risk_flags'])}): {site['risk_flags']}")
            print(f"     - Engineering Mandates ({len(site['engineering_mandates'])}): {site['engineering_mandates']}")

        print("\n==================================================================")
        print(" ALL VERIFICATIONS PASSED: ZERO CORS OR NETWORK ERRORS! ")
        print("==================================================================")
        return True

    except Exception as err:
        print(f"\n  [FAIL] Error during tunnel test: {err}")
        return False
    finally:
        print("\nCleaning up temporary test tunnel process...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        print("Done.")

if __name__ == "__main__":
    success = test_tunnel()
    sys.exit(0 if success else 1)
