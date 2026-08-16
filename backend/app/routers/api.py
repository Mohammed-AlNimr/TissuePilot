from fastapi import APIRouter, HTTPException
from ..schemas import ExperimentInput, FlowSuggestionRequest
from ..services.physics import get_cell, calculate, suggest_flow
from ..services.store import cells, materials, tissues
router=APIRouter(prefix='/api')

@router.get('/cells')
def list_cells(): return cells()
@router.get('/materials')
def list_materials(): return materials()
@router.get('/tissues')
def list_tissues(): return tissues()
@router.get('/cells/{cell_id}')
def cell(cell_id:str):
    try:return get_cell(cell_id).model_dump()
    except ValueError: raise HTTPException(404,'Unknown cell')
@router.post('/physics/validate')
def validate(x:ExperimentInput):
    try:return calculate(x,get_cell(x.cell_id))
    except ValueError as e: raise HTTPException(422,str(e))
@router.post('/physics/suggest-flow')
def flow(x:FlowSuggestionRequest):
    try:return suggest_flow(x)
    except ValueError as e: raise HTTPException(422,str(e))
