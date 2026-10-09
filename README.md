# SuperIndia.ai ⚡🇮🇳
> **Deterministic Geospatial Decision Intelligence Platform for India's AI Compute & National Infrastructure**  
> *Developed for Hackyard BUILD 2026 — AI Systems & National Infrastructure Track*

---

## 1. Executive Summary & Core Principle

India is rapidly scaling its sovereign and enterprise AI data center compute footprint. However, siting hyperscale GPU clusters requires navigating severe hydrological constraints and high-voltage grid availability.

**SuperIndia.ai** implements a zero-black-box, deterministic site-assessment platform grounded in:
- **Central Ground Water Authority (CGWA)** aquifer extraction boundaries and BIS 10500 water quality standards.
- **Central Electricity Authority (CEA)** transmission planning criteria and MoP Green Energy Open Access Regulations 2022.

### Core Architecture Axiom
> **"One model → one responsibility → domain aggregator → composite site assessment."**  
> Zero black-box hallucinations. All engineering scoring is derived mathematically and deterministically from physical telemetry and utility tariffs.

---

## 2. Mathematical Formulations & Engineering Engines

### A. 7-Model Water Engine (Domain Weight: 45%)

The water engine computes site feasibility across seven sub-models:

$$\text{Water Score} = \sum_{i=1}^{7} (\text{Score}_i \times \text{Weight}_i)$$

| Sub-Model | Weight | Engineering Standard / CGWA Threshold |
| :--- | :---: | :--- |
| **Water Availability** | **0.15** | CGWA Stage of Groundwater Extraction ($\le 70\%$ Safe, $70\text{--}90\%$ Semi-critical, $90\text{--}100\%$ Critical, $>100\%$ Over-exploited) |
| **Water Quality** | **0.15** | BIS 10500 Total Dissolved Solids (TDS in mg/L) & cooling tower scaling/fouling indices |
| **Demand Stress** | **0.15** | Competing industrial extraction and aquifer draft. **Note: Sub-score $< 60$ triggers an automated Stress Flag.** |
| **Reuse & Effluent Proximity** | **0.15** | Distance to nearest STP / CETP tertiary treatment plant (km) and recycled MLD availability |
| **Supply vs Demand Balance** | **0.20** | Safety ratio of assured supply (MLD) to projected AI cooling demand (MLD) |
| **Storage Headroom (72h Buffer)** | **0.10** | On-site emergency chilled/raw water storage buffer measured against 72-hour autonomous mission-critical mandate |
| **Climate Resilience** | **0.10** | Multi-factor drought vulnerability index, 100-year flood zone exposure, and coastal storm surge |

---

### B. 4-Metric Electrical Grid Pipeline (Domain Weight: 55%)

The power engine models high-voltage interconnection reliability and green energy wheeling:

$$\text{Power Score} = \sum_{j=1}^{4} (\text{Score}_j \times \text{Weight}_j)$$

| Metric | Weight | Engineering Criteria (CEA Transmission Rules) |
| :--- | :---: | :--- |
| **Substation Proximity** | **0.30** | Distance to nearest EHV substation ($\le 1.5\text{km}$ prime, $1.5\text{--}5\text{km}$ viable, $>5\text{km}$ high Right-of-Way risk) |
| **Voltage Class** | **0.30** | Interconnection voltage: $400\text{kV}$ (100), $220\text{--}230\text{kV}$ (85), $132\text{kV}$ (70), $66\text{--}33\text{kV}$ (50), $11\text{kV}$ (25) |
| **Substation Spare MVA Margin** | **0.20** | N-1 transformer contingency headroom margin at the serving utility bay vs proposed IT load (MW) |
| **Renewable Open Access Corridors** | **0.20** | ISTS Green Energy Corridor connectivity, solar/wind PPA wheeling feasibility, and state cross-subsidy waivers |

---

### C. Composite Site Viability & Classification Tiers

The overall site score is calculated via the domain aggregator:

$$\text{Composite Score} = (\text{Water Score} \times 0.45) + (\text{Power Score} \times 0.55)$$

| Tier Badge | Composite Score | Classification | Color Code | Action |
| :--- | :---: | :--- | :---: | :--- |
| **VIABLE** | $\ge 75.0$ | **VIABLE / RECOMMENDED** | `#10B981` (Emerald) | Fast-track environmental permitting & EPC design |
| **CONDITIONAL** | $50.0 - 74.9$ | **CONDITIONAL / HIGH RISK** | `#F59E0B` (Amber) | Mandatory mitigation investments required |
| **UNVIABLE** | $< 50.0$ | **UNVIABLE / REJECT** | `#EF4444` (Red) | Greenfield site rejected for hyperscale AI compute |

---

### D. Automated Diagnostic & Engineering Mitigation Engine

The platform continuously evaluates regulatory constraints and automatically issues actionable mandates:

- **Demand Stress $\le 50$:**  
  *Warning:* `"Competitive industrial extraction stress"`  
  *Mandate:* `"1. Deploy on-site closed-loop cooling towers. 2. Tap MIDC CETP tertiary treated greywater to avoid municipal cuts."`

- **Coastal / Flood Ground Elevation $< 10\text{m}$:**  
  *Warning:* `"100-year flood zone & CRZ restrictions"`  
  *Mandate:* `"Unviable for sub-grade electrical infrastructure."`

- **Substation Proximity $> 5\text{km}$:**  
  *Warning:* `"Transmission Right-of-Way (RoW) acquisition latency"`  
  *Mandate:* `"Construct dedicated EHV transmission line corridor with redundant dual-circuit bays."`

- **Substation Spare Headroom $< 40\text{ MVA}$:**  
  *Warning:* `"Constrained N-1 contingency grid margin"`  
  *Mandate:* `"Require captive Gas Insulated Substation (GIS) or upfront utility transformer augmentation."`

- **Storage Headroom $< 72\text{ hours}$:**  
  *Warning:* `"Sub-72-hour emergency cooling buffer vulnerability"`  
  *Mandate:* `"Expand on-site water reservoir or install atmospheric water generation (AWG) standby system."`

---

## 3. Monorepo Project Architecture

```text
SuperIndia.ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints.py         # REST routes (/assess, /sites, /compare)
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py            # App settings and CORS setup
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── schemas.py           # Pydantic input/output schemas
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── water_engine.py      # Refactored 7-model water pipeline
│   │   │   ├── power_engine.py      # 4-metric electrical grid pipeline
│   │   │   ├── aggregator.py        # Composite scoring & mitigation engine
│   │   │   └── __init__.py
│   │   ├── data/
│   │   │   └── benchmark_sites.json # Pre-seeded ground truth for 5 hubs
│   │   └── main.py                  # FastAPI application entrypoint
│   ├── requirements.txt
│   └── run.py                       # Backend server launcher
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapView.jsx          # Leaflet dark-mode cartography
│   │   │   ├── ScoreCard.jsx        # Gauge/score visualizer with badges
│   │   │   ├── ExplainabilityPanel.jsx # Granular 7+4 sub-metric progress bars
│   │   │   ├── MitigationCard.jsx   # Automated risk flags & engineering mandates
│   │   │   ├── SiteComparison.jsx   # Multi-site audit table
│   │   │   └── CustomSiteModal.jsx  # Interactive greenfield site simulator
│   │   ├── services/
│   │   │   └── api.js               # Axios client connecting to backend API
│   │   ├── App.jsx                  # Main analytical command center
│   │   ├── index.css                # Tailwind directives & dark mode overrides
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── vite.config.js
├── README.md
├── README.md
├── start.sh                         # Unified local launch script (Linux / macOS)
├── start.bat                        # Unified local launch script (Windows)
├── tunnel.sh                        # Instant HTTPS tunnel launcher (Unix / macOS)
└── tunnel.bat                       # Instant HTTPS tunnel launcher (Windows)
```

---

## 4. Pre-Seeded Benchmark Demonstration Hubs

SuperIndia.ai ships with pre-seeded strategic AI hubs, including the three core demonstration sites:

1. **Mahape MIDC (TTC Industrial Area), Navi Mumbai**
   - **Composite Score:** 80.8 (VIABLE)
   - **Water Score:** 74.0 | **Power Score:** 86.4
   - *Key Telemetry:* 220kV EHV grid (1.5 km), 95 MVA spare margin, 14.5m elevation, Demand Stress 48.0 (triggers closed-loop cooling and MIDC CETP tertiary treated greywater mandate).

2. **Taloja MIDC (Industrial Corridor), Navi Mumbai / Raigad**
   - **Composite Score:** 73.2 (CONDITIONAL / HIGH RISK)
   - **Water Score:** 61.6 | **Power Score:** 82.7
   - *Key Telemetry:* 88% groundwater extraction, 1050 mg/L TDS brackish chemical load (triggers high salinity/softening mandate), Demand Stress 42.0 (severe competing industrial draft).

3. **Coastal South Mumbai (Port Trust / Nariman Point)**
   - **Composite Score:** 60.8 (CONDITIONAL / HIGH RISK)
   - **Water Score:** 62.4 | **Power Score:** 59.6
   - *Key Telemetry:* 4.2m coastal ground elevation (< 10m threshold! triggers 100-year flood zone & CRZ restrictions alert and *"Unviable for sub-grade electrical infrastructure"* mandate), 30 MVA spare margin.

4. **Noida - Sector 132 / Yamuna Corridor, Uttar Pradesh** (Composite: 83.0 - VIABLE)
5. **Bengaluru - KIADB Aerospace Park (Devanahalli), Karnataka** (Composite: 74.0 - CONDITIONAL)
6. **Chennai - Siruseri SIPCOT (OMR Corridor), Tamil Nadu** (Composite: 75.6 - VIABLE)
7. **Hyderabad - Fab City / Shamshabad Hub, Telangana** (Composite: 91.8 - VIABLE - Top Ranked)

---

## 5. REST API Documentation

The FastAPI backend exposes the following endpoints under `/api`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/sites` | List all benchmark demonstration hubs with calculated assessments |
| `GET` | `/api/sites/{site_id}` | Retrieve detailed assessment for a single benchmark site |
| `POST` | `/api/assess` | Run the 7+4 deterministic engine on any custom site payload |
| `POST` | `/api/compare` | Multi-site ranking and comparative analysis matrix |
| `GET` | `/health` / `/api/health` | Health check and engine status |
| `GET` | `/docs` | Interactive Swagger UI documentation |

---

## 6. Quick Start & Execution

### Prerequisites
- Python 3.10+ (installed with `fastapi`, `uvicorn`, `pydantic`)
- Node.js 18+ and npm

### Instant Public HTTPS Tunnel (For Judges & Teammates)

To make the full-stack dashboard accessible publicly from any phone, laptop, or remote device without broken localhost calls:

**On Windows:**
```cmd
tunnel.bat
```

**On Linux / macOS:**
```bash
chmod +x tunnel.sh
./tunnel.sh
```

*(This automatically checks/starts FastAPI on port 8000, Vite on port 5173 with proxy configured, launches the tunnel via Cloudflare or localtunnel, and prints the public HTTPS URL).*

### Local Startup

On Linux / macOS / Git Bash:
```bash
chmod +x start.sh
./start.sh
```

On Windows:
```cmd
start.bat
```

### Manual Component Startup

**1. Launch the Backend API:**
```bash
cd backend
python run.py
# Backend runs at http://127.0.0.1:8000
```

**2. Launch the Frontend Command Center:**
```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

---

## 7. Hackathon Evaluation Checklist

- [x] **Core Architecture Principle:** One model → one responsibility → domain aggregator → composite site assessment.
- [x] **7-Model Water Engine:** Availability (0.15), Quality (0.15), Demand Stress (0.15), Reuse (0.15), Supply/Demand (0.20), Storage (0.10), Resilience (0.10).
- [x] **Automated Stress Flag:** Fired deterministically when Demand Stress sub-score $< 60$.
- [x] **4-Metric Power Module:** Substation Proximity (0.30), Voltage Class (0.30), Spare MVA (0.20), Renewable Open Access (0.20).
- [x] **Composite Formula & Tiers:** $(W \times 0.45) + (P \times 0.55)$ with Viable ($\ge 75$), Conditional ($50\text{--}74.9$), Unviable ($< 50$).
- [x] **Automated Mandates:** Demand Stress $\le 50$ (closed-loop + CETP mandate) & Coastal Elevation $< 10\text{m}$ (CRZ / sub-grade restriction).
- [x] **Geospatial Dark-Mode Cartography:** Leaflet map with pulsing status markers and interactive hub selection.
- [x] **Granular Explainability:** Progress bars and telemetry notes for all 11 sub-metrics.
- [x] **Multi-Site Audit Matrix:** Comparative ranking table across all 5 benchmark hubs.
- [x] **Greenfield Simulation:** Modal allowing arbitrary coordinate and utility telemetry assessment.
