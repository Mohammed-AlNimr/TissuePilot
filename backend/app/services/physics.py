"""Deterministic engineering screening models.

Perfusion flow and extrusion flow are intentionally separate. Biological thresholds
are accepted only when their provenance is evidence-approved. This module is not CFD,
not a universal cell-viability predictor, and not a clinical decision tool.
"""
import math
from dataclasses import dataclass
from .store import cells
from ..schemas import ExperimentInput, Cell, ValidationIssue, PhysicsReport, FlowSuggestionRequest, FlowSuggestion
RHO_WATER=1000.0; MAX_FLOW_UL_MIN=50.0; MAX_PRESSURE_KPA=200.0; MAX_TEMP_C=45.0; LAMINAR_RE_LIMIT=10.0

@dataclass
class CoreResult:
    reynolds: float; velocity_m_s: float; pressure_drop_pa: float; wall_shear_pa: float; apparent_viscosity_pa_s: float
    nozzle_shear_pa: float; nozzle_pressure_drop_pa: float; shear_rate_s: float; nozzle_shear_rate_s: float
    hydraulic_diameter_m: float; rectangular_correction: float

def get_cell(cell_id:str)->Cell:
    for row in cells().get('cells',[]):
        if row['cell_id']==cell_id: return Cell(**row)
    raise ValueError(f'Unknown cell_id: {cell_id}')

def _rectangular_correction(w,h):
    if w<h: w,h=h,w
    total=sum(math.tanh(m*math.pi*w/(2*h))/(m**5) for m in range(1,32,2))
    return max(min(1-(192*h/(math.pi**5*w))*total,1),0.05)

def _core(w_um,h_um,L_mm,Qp,K,n,nozzle_um=410,nozzle_length_mm=1,Q_extrusion_ul_min=None,perfusion_viscosity_pa_s=None,perfusion_density_kg_m3=1000):
    w=max(w_um,1e-9)*1e-6; h=max(h_um,1e-9)*1e-6; L=max(L_mm,1e-9)*1e-3
    Q=max(Qp,0)*1e-9/60; area=max(w*h,1e-24); velocity=Q/area
    rho=max(perfusion_density_kg_m3,100); mu=max(perfusion_viscosity_pa_s if perfusion_viscosity_pa_s is not None else K,1e-12)
    dh=2*w*h/max(w+h,1e-18); Re=rho*velocity*dh/mu
    corr=_rectangular_correction(w,h); dp=12*mu*L*Q/max(w*h**3*corr,1e-30); shear=6*mu*Q/max(w*h**2,1e-30); gamma=velocity/max(h,1e-12)
    Qe=max(Q_extrusion_ul_min or 0,0)*1e-9/60; r=max(nozzle_um,1e-6)*0.5e-6
    gamma_n=((3*n+1)/(4*n))*4*Qe/(math.pi*r**3) if Qe>0 else 0
    eta_n=max(K*max(gamma_n,1e-12)**(n-1),1e-12) if Qe>0 else 0
    nozzle_shear=eta_n*gamma_n if Qe>0 else 0
    Ln=max(nozzle_length_mm,1e-9)*1e-3
    nozzle_dp=(2*Ln*K/r*(gamma_n**n)) if Qe>0 else 0
    return CoreResult(Re,velocity,dp,shear,mu,nozzle_shear,nozzle_dp,gamma,gamma_n,dh,corr)

def _evidence_approved(cell):
    prov=getattr(cell,'data_provenance',None) or {}; records=getattr(cell,'evidence_records',None) or []
    if not bool(prov.get('verified')): return False
    if any(isinstance(r,dict) and (r.get('doi') or r.get('pmid')) for r in records): return True
    return str(prov.get('verification_type','')).lower() in {'laboratory_measurement','institutional_validation'}

def sanity_check(x,cell):
    issues=[]; diameter=x.cell_diameter_um if x.cell_diameter_um is not None else cell.diameter_um; limit=x.cell_critical_shear_pa if x.cell_critical_shear_pa is not None else cell.critical_shear_pa
    if diameter is None: issues.append(ValidationIssue(field='cell_id',severity='error',code='CELL_DIAMETER_MISSING',message='Cell diameter requires evidence-approved data or verified laboratory input.'))
    if limit is None: issues.append(ValidationIssue(field='cell_id',severity='error',code='CELL_SHEAR_LIMIT_MISSING',message='Critical shear limit is unavailable.'))
    if limit is not None and not _evidence_approved(cell): issues.append(ValidationIssue(field='cell_id',severity='error',code='BIOLOGICAL_EVIDENCE_NOT_VERIFIED',message='The selected shear limit is contextual/candidate data. A primary DOI/PMID-backed parameter record or verified laboratory measurement is required for a scientific PASS.'))
    if x.flow_rate_ul_min>MAX_FLOW_UL_MIN: issues.append(ValidationIssue(field='flow_rate_ul_min',severity='error',code='FLOW_LIMIT',message=f'Flow exceeds {MAX_FLOW_UL_MIN:g} µL/min guardrail.'))
    if x.pressure_kpa>MAX_PRESSURE_KPA: issues.append(ValidationIssue(field='pressure_kpa',severity='error',code='PRINTER_PRESSURE',message=f'Pressure exceeds {MAX_PRESSURE_KPA:g} kPa guardrail.'))
    if x.temperature_c<=0 or x.temperature_c>MAX_TEMP_C: issues.append(ValidationIssue(field='temperature_c',severity='error',code='BIOLOGICAL_TEMPERATURE',message=f'Temperature must be >0 and <= {MAX_TEMP_C:g} °C for this conservative envelope.'))
    if x.fabrication_strategy!='acellular_chip_post_seeding' and x.extrusion_flow_rate_ul_min is None: issues.append(ValidationIssue(field='extrusion_flow_rate_ul_min',severity='warning',code='EXTRUSION_FLOW_MISSING',message='Extrusion flow is undeclared; nozzle shear/pressure cannot gate cell-laden printing.'))
    if diameter is not None and x.channel_width_um<=diameter*1.25: issues.append(ValidationIssue(field='channel_width_um',severity='error',code='BIO_GEOMETRY_CELL',message='Channel width is too close to cell diameter for the conservative envelope.'))
    if x.fabrication_strategy!='acellular_chip_post_seeding' and diameter is not None and x.nozzle_diameter_um<diameter*4: issues.append(ValidationIssue(field='nozzle_diameter_um',severity='error',code='NOZZLE_CELL_COMPATIBILITY',message='Nozzle diameter is below the configured conservative cell-to-nozzle ratio.'))
    return issues

def calculate(x,cell):
    selected=[cell]
    for cid in x.additional_cell_ids:
        try:
            c=get_cell(cid)
            if c.cell_id not in [z.cell_id for z in selected]: selected.append(c)
        except ValueError: pass
    limiting=cell.model_copy(update={'critical_shear_pa':x.cell_critical_shear_pa}) if x.cell_critical_shear_pa is not None else min((c for c in selected if c.critical_shear_pa is not None),key=lambda c:c.critical_shear_pa,default=cell)
    issues=sanity_check(x,limiting)
    c=_core(x.channel_width_um,x.channel_height_um,x.channel_length_mm,x.flow_rate_ul_min,x.consistency_index_k,x.flow_index_n,x.nozzle_diameter_um,x.nozzle_length_mm,x.extrusion_flow_rate_ul_min,x.perfusion_viscosity_pa_s,x.perfusion_density_kg_m3)
    if c.reynolds>=LAMINAR_RE_LIMIT: issues.append(ValidationIssue(field='flow_rate_ul_min',severity='error',code='RE_LAMINAR',message=f'Reynolds number {c.reynolds:.3g} is not below screening criterion Re < {LAMINAR_RE_LIMIT:g}.'))
    if limiting.critical_shear_pa is None: raise ValueError('No usable critical-shear limit; verify cell evidence.')
    if c.wall_shear_pa>limiting.critical_shear_pa: issues.append(ValidationIssue(field='flow_rate_ul_min',severity='error',code='WALL_SHEAR',message=f'Characteristic wall shear {c.wall_shear_pa:.3g} Pa exceeds the selected-cell design limit {limiting.critical_shear_pa:.3g} Pa.'))
    if x.fabrication_strategy!='acellular_chip_post_seeding' and x.extrusion_flow_rate_ul_min is not None and c.nozzle_shear_pa>limiting.critical_shear_pa: issues.append(ValidationIssue(field='extrusion_flow_rate_ul_min',severity='error',code='NOZZLE_SHEAR',message=f'Estimated nozzle wall shear {c.nozzle_shear_pa:.3g} Pa exceeds the selected-cell design limit {limiting.critical_shear_pa:.3g} Pa.'))
    relevant=c.wall_shear_pa
    if x.fabrication_strategy!='acellular_chip_post_seeding' and x.extrusion_flow_rate_ul_min is not None: relevant=max(relevant,c.nozzle_shear_pa)
    sf=limiting.critical_shear_pa/max(relevant,1e-12); passed=not any(i.severity=='error' for i in issues)
    return PhysicsReport(reynolds=c.reynolds,velocity_m_s=c.velocity_m_s,pressure_drop_pa=c.pressure_drop_pa,wall_shear_pa=c.wall_shear_pa,apparent_viscosity_pa_s=c.apparent_viscosity_pa_s,nozzle_shear_pa=c.nozzle_shear_pa,nozzle_pressure_drop_pa=c.nozzle_pressure_drop_pa,estimated_viability_index=None,hydraulic_resistance_pa_s_m3=c.pressure_drop_pa/max(x.flow_rate_ul_min*1e-9/60,1e-18),safety_factor=sf,passed=passed,issues=issues)

def suggest_flow(req):
    cell=get_cell(req.cell_id)
    if not _evidence_approved(cell) or cell.critical_shear_pa is None: raise ValueError('Evidence-approved critical shear is required for constrained flow suggestion.')
    target=cell.critical_shear_pa*req.target_safety_margin
    for q in [i/10 for i in range(1,501)]:
        x=ExperimentInput(cell_id=req.cell_id,channel_width_um=req.channel_width_um,channel_height_um=req.channel_height_um,channel_length_mm=req.channel_length_mm,wall_thickness_mm=1,build_width_mm=100,build_length_mm=100,flow_rate_ul_min=q,consistency_index_k=req.consistency_index_k,flow_index_n=req.flow_index,nozzle_diameter_um=max(400,(cell.diameter_um or 50)*5),temperature_c=25,pressure_kpa=50,cell_density_million_ml=1)
        c=_core(x.channel_width_um,x.channel_height_um,x.channel_length_mm,q,x.consistency_index_k,x.flow_index_n,x.nozzle_diameter_um)
        if c.reynolds<LAMINAR_RE_LIMIT and c.wall_shear_pa<=target: return FlowSuggestion(recommended_flow_ul_min=q,rationale='Deterministic screening value constrained by evidence-approved cell shear and laminar-flow guardrails; validate experimentally.')
    return FlowSuggestion(recommended_flow_ul_min=0.1,rationale='No feasible value found inside configured screening envelope.')
