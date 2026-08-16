from typing import Optional
from pydantic import BaseModel, Field

class Cell(BaseModel):
    cell_id: str
    canonical_name: str
    tissue_origin: Optional[str]=None
    aliases: list[str]=[]
    diameter_um: Optional[float]=None
    critical_shear_pa: Optional[float]=None
    deformability_index: Optional[float]=None
    preferred_density_million_ml: Optional[float]=None
    rheology: dict={}
    recommended_bioinks: list[str]=[]
    evidence_status: str='metadata_only'
    evidence_records: list[dict]=[]
    data_provenance: dict={}

class ExperimentInput(BaseModel):
    cell_id: str
    additional_cell_ids: list[str]=[]
    cell_diameter_um: Optional[float]=Field(default=None, gt=0)
    cell_critical_shear_pa: Optional[float]=Field(default=None, gt=0)
    channel_width_um: float=Field(gt=0)
    channel_height_um: float=Field(gt=0)
    channel_length_mm: float=Field(gt=0)
    wall_thickness_mm: float=Field(gt=0)
    build_width_mm: float=Field(gt=0)
    build_length_mm: float=Field(gt=0)
    flow_rate_ul_min: float=Field(gt=0)
    perfusion_viscosity_pa_s: Optional[float]=Field(default=0.001, gt=0)
    perfusion_density_kg_m3: float=Field(default=1000, gt=0)
    consistency_index_k: float=Field(default=0.001, gt=0)
    flow_index_n: float=Field(default=1.0, gt=0)
    nozzle_diameter_um: float=Field(gt=0)
    nozzle_length_mm: float=Field(default=1.0, gt=0)
    extrusion_flow_rate_ul_min: Optional[float]=Field(default=None, gt=0)
    pressure_kpa: float=Field(default=50, gt=0)
    print_speed_mm_s: float=Field(default=10, gt=0)
    temperature_c: float=Field(default=25, gt=0)
    cell_density_million_ml: float=Field(default=1, gt=0)
    fabrication_strategy: str='cell_laden_bioprinting'

class ValidationIssue(BaseModel):
    field: str
    severity: str
    code: str
    message: str

class PhysicsReport(BaseModel):
    reynolds: float
    velocity_m_s: float
    pressure_drop_pa: float
    wall_shear_pa: float
    apparent_viscosity_pa_s: float
    nozzle_shear_pa: float
    nozzle_pressure_drop_pa: float
    estimated_viability_index: Optional[float]=None
    hydraulic_resistance_pa_s_m3: float
    safety_factor: float
    passed: bool
    issues: list[ValidationIssue]

class FlowSuggestionRequest(BaseModel):
    cell_id: str
    channel_width_um: float=Field(gt=0)
    channel_height_um: float=Field(gt=0)
    channel_length_mm: float=Field(gt=0)
    consistency_index_k: float=Field(gt=0)
    flow_index_n: float=Field(gt=0)
    target_safety_margin: float=Field(default=0.5, gt=0, lt=1)

class FlowSuggestion(BaseModel):
    recommended_flow_ul_min: float
    rationale: str
