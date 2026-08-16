# Scientific Engine 1.8

## Boundaries

TissuePilot separates perfusion-channel physics from extrusion-bioprinting physics. Perfusion flow is supplied independently from extrusion flow. Nozzle length is explicit because diameter alone cannot determine pressure drop.

### Perfusion

The solver uses volumetric flow, channel geometry, perfusate viscosity/density and hydraulic diameter. For rectangular channels it applies a finite-width analytical correction. The reported wall shear is a characteristic broad-wall estimate, not a maximum corner shear from CFD.

### Extrusion

For a power-law material, the wall shear-rate screening term uses the Rabinowitsch/Mooney correction:

`gamma_w = ((3n+1)/(4n)) * 4Q/(pi R^3)`

The nozzle pressure estimate is a simplified fully developed model and does not represent cartridge friction, entrance/exit losses, die swell, viscoelasticity or non-circular nozzle geometry.

### Biological evidence

Cell critical-shear limits are not universal constants. A candidate value is never sufficient for a scientific PASS. Approval requires a primary DOI/PMID-backed parameter record or documented laboratory/institutional verification. LLM-extracted values remain provisional until reviewed.

### Viability

A universal numerical viability predictor has deliberately been disabled. Cell viability depends on exposure duration, cell type/state, material rheology, nozzle geometry, pressure, temperature and post-print biology. The platform should report experimental endpoints rather than manufacture a biological percentage from a single shear value.

## Interpretation

Outputs are research decision-support and screening calculations. They are not clinical recommendations, validated CFD, manufacturing release criteria, or substitutes for rheology characterization and experimental validation.
