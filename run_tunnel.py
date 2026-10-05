import subprocess
import time
import re
import os
import sys

cloudflared_path = r"C:\Users\DRONA\nodejs\cloudflared.exe"
if not os.path.exists(cloudflared_path):
    cloudflared_path = "cloudflared"

print(f"Launching Cloudflare Tunnel targeting http://127.0.0.1:5173 ...")

cmd = [
    cloudflared_path,
    "tunnel",
    "--url",
    "http://127.0.0.1:5173",
    "--http-host-header",
    "localhost:5173"
]

proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    encoding="utf-8",
    errors="replace"
)

url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
tunnel_url = None

# Monitor stdout until URL appears
start_time = time.time()
while time.time() - start_time < 35:
    line = proc.stdout.readline()
    if line:
        sys.stdout.write(line)
        sys.stdout.flush()
        m = url_pattern.search(line)
        if m:
            tunnel_url = m.group(0)
            break
    else:
        time.sleep(0.1)

if tunnel_url:
    print(f"\n[SUCCESS] Public Cloudflare Tunnel Assigned: {tunnel_url}")
    with open("tunnel_url.txt", "w", encoding="utf-8") as f:
        f.write(tunnel_url.strip())
else:
    print("\n[ERROR] Could not extract tunnel URL within timeout.")

# Keep process alive and forward output
try:
    for line in iter(proc.stdout.readline, ""):
        sys.stdout.write(line)
        sys.stdout.flush()
except KeyboardInterrupt:
    proc.terminate()
