# TissuePilot

TissuePilot is an evidence-aware research platform for tissue engineering, microfluidics, bioprinting, biomaterials and organ-on-chip design.

## Scientific scope

This repository contains a research decision-support system. It is **not** a clinical device, validated CFD package, universal cell-viability predictor, or laboratory SOP.

### Scientific safeguards in 1.8.0

- Perfusion and extrusion are modeled as separate physical systems.
- Rectangular microchannel calculations use a finite-width hydraulic correction rather than a pure parallel-plate approximation.
- Extrusion shear/pressure requires an independent extrusion flow rate; perfusion flow is never silently reused.
- Cell-specific critical-shear values are treated as biological evidence constraints, not universal constants.
- Seed/context values cannot produce a scientific PASS without primary-source DOI/PMID evidence or documented laboratory verification.
- LLM-extracted parameters remain provisional until researcher review and source attachment.
- Universal viability prediction from shear alone is disabled.

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

### Docker

```bash
docker compose up --build
```

## Scientific review

See `docs/SCIENTIFIC_ENGINE_1.8.md` for the model boundaries and evidence policy.

## Validation

```bash
python -m compileall -q backend/app
python scripts/release_smoke_test.py
```

## Safety

Do not use numerical outputs as patient-specific or clinical recommendations. Experimental qualification, manufacturer instructions, sterility controls, rheology characterization, imaging, leak testing and biological endpoints remain necessary before experimental execution.
