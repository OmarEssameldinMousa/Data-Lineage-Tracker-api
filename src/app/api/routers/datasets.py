from os import name

from fastapi import APIRouter, Depends, status, Body
from app.core.dependencies import get_db
from app.crud.dataset import DatasetCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.dataset import DatasetResponse, DatasetDepthResponse, LineageGraphResponse, DatasetCreate
import uuid 
from fastapi.exceptions import HTTPException
from app.models import Dataset
import asyncio
router = APIRouter(
    prefix="/datasets",
    tags=["datasets"],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DatasetResponse)
async def create_dataset(request: DatasetCreate = Body(...), db_session: AsyncSession = Depends(get_db)):
    dataset_crud = DatasetCRUD(db_session)
    dataset = await dataset_crud.create_dataset(name=request.name)
    return dataset

@router.get("/{dataset_id}/impact", response_model=list[DatasetResponse]) 
async def get_impact(dataset_id: uuid.UUID, db_session: AsyncSession = Depends(get_db)):
    dataset_crud = DatasetCRUD(db_session)
    dataset = await dataset_crud.is_exist(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    impacted_datasets = await dataset_crud.get_impact_analysis(dataset_id=dataset_id)

    return impacted_datasets
    

@router.get("/{dataset_id}/impact-depth", response_model=list[DatasetDepthResponse])
async def get_impact_with_depth(dataset_id: uuid.UUID, db_session: AsyncSession = Depends(get_db)):
    dataset_crud = DatasetCRUD(db_session)

    dataset = await dataset_crud.is_exist(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    impacted_datasets_with_depth = await dataset_crud.get_impact_with_depth(dataset_id=dataset_id)

    return [
        DatasetDepthResponse(dataset=ds, depth=depth) 
        for ds, depth in impacted_datasets_with_depth
    ]

@router.get("/{dataset_id}/lineage", response_model=LineageGraphResponse)
async def get_full_lineage(dataset_id: uuid.UUID, db_session: AsyncSession = Depends(get_db)):
    dataset_crud = DatasetCRUD(db_session)
    dataset = await dataset_crud.is_exist(dataset_id)
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    upstream_datasets, downstream_datasets = await asyncio.gather(
        dataset_crud.get_root_cause_analysis(dataset_id=dataset_id),
        dataset_crud.get_impact_analysis(dataset_id=dataset_id)
    )


    return {
        "upstream": upstream_datasets,
        "downstream": downstream_datasets
    }