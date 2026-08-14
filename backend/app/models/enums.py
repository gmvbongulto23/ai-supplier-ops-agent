import enum

from sqlalchemy import Enum as SAEnum


class SupplierReliability(str, enum.Enum):
    RELIABLE = "reliable"
    INCONSISTENT = "inconsistent"


class OrderStatus(str, enum.Enum):
    ON_TIME = "on_time"
    DELAYED = "delayed"
    AT_RISK = "at_risk"
    DELIVERED = "delivered"


supplier_reliability_type = SAEnum(
    SupplierReliability,
    name="supplier_reliability",
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
)

order_status_type = SAEnum(
    OrderStatus,
    name="order_status",
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
)
