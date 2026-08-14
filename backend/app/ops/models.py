from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ReliabilityStatus(str, Enum):
    RELIABLE = "reliable"
    INCONSISTENT = "inconsistent"


class OrderStatus(str, Enum):
    ON_TIME = "on_time"
    DELAYED = "delayed"
    AT_RISK = "at_risk"
    DELIVERED = "delivered"


class Supplier(BaseModel):
    id: str
    name: str
    products_supplied: list[str]
    reliability_status: ReliabilityStatus
    contact_info: str


class SupplierCreate(BaseModel):
    name: str
    products_supplied: list[str]
    reliability_status: ReliabilityStatus
    contact_info: str


class Order(BaseModel):
    id: str
    supplier_id: str
    product: str
    quantity: int
    order_date: datetime
    expected_delivery: datetime
    status: OrderStatus = OrderStatus.ON_TIME


class OrderCreate(BaseModel):
    supplier_id: str
    product: str
    quantity: int
    order_date: datetime
    expected_delivery: datetime
    status: OrderStatus = OrderStatus.ON_TIME


class Delivery(BaseModel):
    order_id: str
    eta: datetime
    status: OrderStatus = OrderStatus.ON_TIME
    delay_info: str | None = None


class DeliveryCreate(BaseModel):
    order_id: str
    eta: datetime
    status: OrderStatus = OrderStatus.ON_TIME
    delay_info: str | None = None


class Inventory(BaseModel):
    product: str
    current_quantity: float
    avg_usage_per_hour: float
    minimum_required_quantity: float


class InventoryCreate(BaseModel):
    product: str
    current_quantity: float
    avg_usage_per_hour: float
    minimum_required_quantity: float


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"


class Recommendation(BaseModel):
    id: str
    product: str
    order_id: str | None = None
    severity: str
    message: str
    reason: str
    backup_supplier_id: str | None = None
    status: RecommendationStatus = RecommendationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accepted_at: datetime | None = None
