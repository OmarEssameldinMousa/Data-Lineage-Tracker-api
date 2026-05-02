from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from datetime import datetime
import uuid

class LineageEdge(Base):
    __tablename__ = "lineage_edges"

    upstream_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("datasets.id"), primary_key=True)
    downstream_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("datasets.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    upstream_dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        foreign_keys=[upstream_id],
        back_populates="downstream_edges"
    )
    downstream_dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        foreign_keys=[downstream_id],
        back_populates="upstream_edges"
    )
