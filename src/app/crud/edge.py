from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.core.dependencies import get_db
from app.models import LineageEdge
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.schemas.edge import EdgeCreate
from app.crud.dataset import DatasetCRUD

class EdgeCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def delete_edge(self, upstream_id: uuid.UUID, downstream_id: uuid.UUID) -> LineageEdge:
        edge = await self.db.get(LineageEdge, (upstream_id, downstream_id))
        if edge:
            await self.db.delete(edge)
            await self.db.commit()
        else:
            raise HTTPException(status_code=404, detail="Edge not found")
        return edge
    
    async def create_edge(self, edge_in: EdgeCreate) -> LineageEdge:

        dataset_crud = DatasetCRUD(self.db)
        # we have to prevent cycles in the graph 
        impacted_datasets = await dataset_crud.get_impact_analysis(edge_in.downstream_id)
        if edge_in.upstream_id in [ds.id for ds in impacted_datasets]:
            raise HTTPException(status_code=400, detail="Creating this edge would introduce a cycle in the graph")

        edge = LineageEdge(
            upstream_id=edge_in.upstream_id,
            downstream_id=edge_in.downstream_id
        )
        self.db.add(edge)
        try:
            await self.db.commit()
            await self.db.refresh(edge)
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Edge already exists")
        
        return edge if edge else None