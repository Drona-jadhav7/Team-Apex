# Architecture

```text
Frontend
   ↓
Backend API
   ↓
Decision Services
   ├── Site Scoring
   ├── Demand Analysis
   ├── Partner Matching
   └── Report Generation
   ↓
Data + AI
   ├── Verified datasets
   ├── RAG knowledge
   ├── Agents
   └── Evaluation
   ↓
Decision Output
   ├── Site readiness
   ├── Scenario results
   └── Preliminary report
```

## Design principle

Every important output should distinguish:
- source-backed facts
- model assumptions
- scenario calculations
- AI-generated interpretation
