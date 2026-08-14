from typing import TYPE_CHECKING

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SupplierReliability, supplier_reliability_type
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.order import Order


class Supplier(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "suppliers"
    __table_args__ = (Index("ix_suppliers_reliability", "reliability"),)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    reliability: Mapped[SupplierReliability] = mapped_column(supplier_reliability_type, nullable=False)

    orders: Mapped[list["Order"]] = relationship(back_populates="supplier")
