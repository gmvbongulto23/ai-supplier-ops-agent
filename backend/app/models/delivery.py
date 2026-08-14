import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import OrderStatus, order_status_type
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.order import Order


class Delivery(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "deliveries"
    __table_args__ = (
        Index("ix_deliveries_order_id", "order_id"),
        Index("ix_deliveries_status", "status"),
        Index("ix_deliveries_order_status", "order_id", "status"),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(order_status_type, nullable=False)
    expected_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="deliveries")
