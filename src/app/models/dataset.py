from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from datetime import datetime
import uuid

class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    upstream_edges: Mapped[list["LineageEdge"]] = relationship(
        "LineageEdge",
        foreign_keys=lambda: [LineageEdge.downstream_id],
        back_populates="downstream_dataset",
        cascade="all, delete-orphan"
    )

    downstream_edges: Mapped[list["LineageEdge"]] = relationship(
        "LineageEdge",
        foreign_keys=lambda: [LineageEdge.upstream_id],
        back_populates="upstream_dataset",
        cascade="all, delete-orphan"
    )
