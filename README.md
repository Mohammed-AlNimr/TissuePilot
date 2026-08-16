# TissuePilot

TissuePilot 1.8.0 is an evidence-aware research platform for tissue engineering, microfluidics, bioprinting, biomaterials and organ-on-chip design.

**Scientific boundary:** this is research decision support, not clinical software, validated CFD, a universal viability predictor, or a laboratory SOP.

## Scientific safeguards
- Perfusion flow and extrusion flow are separate inputs.
- Rectangular microchannel calculations use finite-width hydraulic correction.
- Nozzle length is explicit in extrusion pressure estimation.
- Cell-specific shear limits are treated as biological evidence constraints, not universal constants.
- Candidate/context data cannot produce a scientific PASS without primary DOI/PMID evidence or documented laboratory/institutional verification.
- LLM-extracted values remain provisional pending researcher review.
- Universal viability prediction from shear alone is disabled.

## Run

```bash
docker compose up --build
```

Web: http://localhost:8080  
API: http://localhost:8000/docs

Or run backend/frontend separately as described in the repository documentation.

## Scientific documentation
See `docs/SCIENTIFIC_ENGINE_1.8.md`.

## Safety
Numerical outputs require experimental validation, exact-formulation rheology characterization, sterility controls, imaging/leak testing and appropriate biological endpoints before experimental use.
