from fastapi import APIRouter, Depends, status
from app.core.settings import get_settings, Settings
from app.crud.edge import EdgeCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from fastapi import Body
from app.schemas.edge import EdgeCreate, EdgeResponse
import uuid

router = APIRouter(
    prefix="/lineage",
    tags=["lineage"],
)

@router.post("/edges", status_code=status.HTTP_201_CREATED, response_model=EdgeResponse)
async def create_edge(db_session:  AsyncSession=Depends(get_db), edge_data: EdgeCreate = Body(...)):
    edge_crud = EdgeCRUD(db_session)
    return await edge_crud.create_edge(edge_data)

@router.delete("/edges/{upstream_id}/{downstream_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_edge(upstream_id: uuid.UUID, downstream_id: uuid.UUID, db_session: AsyncSession=Depends(get_db)):
    edge_crud = EdgeCRUD(db_session)
    edge = await edge_crud.delete_edge(upstream_id, downstream_id)
    return edge