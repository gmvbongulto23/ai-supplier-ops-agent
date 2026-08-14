import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import OrderStatus, order_status_type
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.delivery import Delivery
    from app.models.product import Product
    from app.models.supplier import Supplier


class Order(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_orders_quantity_non_negative"),
        Index("ix_orders_supplier_id", "supplier_id"),
        Index("ix_orders_product_id", "product_id"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_supplier_status", "supplier_id", "status"),
    )

    supplier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(order_status_type, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    supplier: Mapped["Supplier"] = relationship(back_populates="orders")
    product: Mapped["Product"] = relationship(back_populates="orders")
    deliveries: Mapped[list["Delivery"]] = relationship(back_populates="order")
