from sqlalchemy import select, literal
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.models.dataset import Dataset
from app.models.edge import LineageEdge

""""
CTE 
WITH RECURSIVE downstream AS (
    -- BASE CASE 
    SELECT downstream_id 
    from Lineage_edges
    where upstream_id = :dataset_id

    -- RECURISVE STEP
    SELECT le.downstream_id 
    FROM lineage_edges le
    JOIN downstream d 
        ON le.upstream_id = d.downstream_id
)
"""


class DatasetCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def is_exist(self, dataset_id: uuid.UUID) -> bool:
        return True if await self.db.execute(select(1).where(Dataset.id == dataset_id).limit(1)) else False  

    async def create_dataset(self, name: str) -> Dataset:
        
        dataset = Dataset(name=name)

        # if the dataset name already exists, we will let the database handle the unique constraint violation and raise an error
        self.db.add(dataset)
        await self.db.commit()
        await self.db.refresh(dataset)
        return dataset

    async def get_impact_analysis(self, dataset_id: uuid.UUID) -> list[Dataset]:
        # Base case
        base_query = select(LineageEdge.downstream_id).where(
            LineageEdge.upstream_id == dataset_id
        )

        # Recursive CTE
        cte = base_query.cte(name="impact_cte", recursive=True)

        edge_alias = aliased(LineageEdge)

        # Recursive step
        recursive_step = select(edge_alias.downstream_id).join(
            cte,
            edge_alias.upstream_id == cte.c.downstream_id
        )

        # Union
        cte = cte.union_all(recursive_step)

        # Final query (remove duplicates)
        final_query = (
            select(Dataset)
            .join(cte, Dataset.id == cte.c.downstream_id)
            .distinct()
            .order_by(Dataset.created_at)
        )

        result = await self.db.execute(final_query)
        return list(result.scalars().all())
    
    async def get_impact_with_depth(self, dataset_id: uuid.UUID)-> list[tuple[Dataset, int]]:
        base_query = select(
            LineageEdge.downstream_id,
            literal(1).label("depth")
        ).where(LineageEdge.upstream_id == dataset_id)

        cte = base_query.cte(name="impact_depth_cte", recursive=True)

        edge_alias = aliased(LineageEdge)

        recursive_step = select(
            edge_alias.downstream_id,
            (cte.c.depth + 1).label("depth")
        ).join(
            cte,
            edge_alias.upstream_id == cte.c.downstream_id
        )

        cte = cte.union_all(recursive_step)

        final_query = (
            select(Dataset, cte.c.depth)
            .join(cte, Dataset.id == cte.c.downstream_id)
            .distinct()
            .order_by(cte.c.depth)
        )

        result = await self.db.execute(final_query)
        return  result.all() # list of (Dataset, depth)
    
    async def get_root_cause_analysis(self, dataset_id: uuid.UUID) -> list[Dataset]:
        
        base_query = select(LineageEdge.upstream_id).where(
            LineageEdge.downstream_id == dataset_id
        )

        cte = base_query.cte(name="cause_cte",recursive=True)
        
        edge_alias = aliased(LineageEdge)

        recursive_step = select(edge_alias.upstream_id).join(
            cte, 
            edge_alias.downstream_id == cte.c.upstream_id
        )

        cte = cte.union_all(recursive_step)

        final_query = (
            select(Dataset)
            .join(cte, Dataset.id == cte.c.upstream_id)
            .distinct()
            .order_by(Dataset.created_at)
        )

        result = await self.db.execute(final_query)
        return list(result.scalars().all())